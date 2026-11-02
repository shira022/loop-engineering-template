#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";
import pixelmatch from "pixelmatch";
import { PNG } from "pngjs";
import { collectA11y, collectLayout } from "./lib/checks.mjs";
import {
  buildReport,
  normalizeThresholds,
  renderMarkdown,
  routePasses,
  sanitizeRouteName,
} from "./lib/report.mjs";

const CWD = process.cwd();
const DEFAULT_OUT_ROOT = "tools/ui-regression/out";
const DEFAULT_BASELINE_DIR = "tools/ui-regression/baseline";

const USAGE = `Usage:
  node tools/ui-regression/sweep.mjs --config sweep.example.json [options]

Options:
  --config <file>      Path to the sweep config JSON (required)
  --out <dir>          Output directory (default: tools/ui-regression/out/run-<UTC>)
  --update-baseline    Copy screenshots into baselineDir and skip diff checks
  --no-screenshots     Do not capture screenshots or run pixel diffs
  --json               Print the report JSON to stdout
  -h, --help           Show this help

Exit codes: 0 = all routes pass, 1 = violations/diff exceeded, 2 = config or startup error.`;

function utcStamp(date = new Date()) {
  const pad = (value) => String(value).padStart(2, "0");
  return (
    `${date.getUTCFullYear()}${pad(date.getUTCMonth() + 1)}${pad(date.getUTCDate())}` +
    `-${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}${pad(date.getUTCSeconds())}`
  );
}

function parseArgs(argv) {
  const options = {
    config: null,
    out: null,
    updateBaseline: false,
    noScreenshots: false,
    json: false,
    help: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const [flag, inlineValue] = arg.startsWith("--") ? arg.split("=", 2) : [arg, undefined];
    switch (flag) {
      case "--config":
        options.config = inlineValue ?? argv[++i];
        break;
      case "--out":
        options.out = inlineValue ?? argv[++i];
        break;
      case "--update-baseline":
        options.updateBaseline = true;
        break;
      case "--no-screenshots":
        options.noScreenshots = true;
        break;
      case "--json":
        options.json = true;
        break;
      case "-h":
      case "--help":
        options.help = true;
        break;
      default:
        throw new Error(`unknown argument: ${arg}`);
    }
  }

  return options;
}

function resolveFromCwd(value) {
  return path.isAbsolute(value) ? value : path.resolve(CWD, value);
}

function loadConfig(configPath) {
  const absoluteConfig = resolveFromCwd(configPath);
  let raw;
  try {
    raw = fs.readFileSync(absoluteConfig, "utf8");
  } catch (error) {
    throw new Error(`cannot read config "${configPath}": ${error.message}`);
  }

  let config;
  try {
    config = JSON.parse(raw);
  } catch (error) {
    throw new Error(`config "${configPath}" is not valid JSON: ${error.message}`);
  }

  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("config must be a JSON object");
  }
  if (typeof config.baseUrl !== "string" || !config.baseUrl.trim()) {
    throw new Error('config.baseUrl must be a non-empty string');
  }
  try {
    new URL(config.baseUrl);
  } catch {
    throw new Error(`config.baseUrl is not a valid URL: ${config.baseUrl}`);
  }
  if (!Array.isArray(config.routes) || config.routes.length === 0) {
    throw new Error("config.routes must be a non-empty array");
  }

  const names = new Set();
  const fileNames = new Set();
  const routes = config.routes.map((route, index) => {
    if (!route || typeof route !== "object") {
      throw new Error(`config.routes[${index}] must be an object`);
    }
    if (typeof route.name !== "string" || !route.name.trim()) {
      throw new Error(`config.routes[${index}].name must be a non-empty string`);
    }
    if (typeof route.path !== "string" || !route.path.trim()) {
      throw new Error(`config.routes[${index}].path must be a non-empty string`);
    }
    if (route.waitFor !== undefined && typeof route.waitFor !== "string") {
      throw new Error(`config.routes[${index}].waitFor must be a string`);
    }
    try {
      new URL(route.path, config.baseUrl);
    } catch {
      throw new Error(`config.routes[${index}].path is not a valid URL path`);
    }
    const name = route.name.trim();
    if (names.has(name)) {
      throw new Error(`duplicate route name: "${name}"`);
    }
    names.add(name);
    const fileName = sanitizeRouteName(name);
    if (fileNames.has(fileName)) {
      throw new Error(`route names collide after sanitizing for file output: "${name}"`);
    }
    fileNames.add(fileName);
    return {
      name,
      path: route.path,
      waitFor: route.waitFor,
      fileName,
    };
  });

  const viewport = config.viewport ?? {};
  const width = viewport.width ?? 1280;
  const height = viewport.height ?? 800;
  if (!Number.isInteger(width) || width <= 0 || !Number.isInteger(height) || height <= 0) {
    throw new Error("config.viewport.width and config.viewport.height must be positive integers");
  }

  return {
    configPath: absoluteConfig,
    configDir: path.dirname(absoluteConfig),
    baseUrl: config.baseUrl,
    viewport: { width, height },
    routes,
    thresholds: normalizeThresholds(config.thresholds),
    a11y: config.a11y !== false,
    screenshots: config.screenshots !== false,
    baselineDir: resolveFromCwd(config.baselineDir || DEFAULT_BASELINE_DIR),
  };
}

function readPng(file) {
  return PNG.sync.read(fs.readFileSync(file));
}

function writePng(file, png) {
  fs.writeFileSync(file, PNG.sync.write(png));
}

function paddedCopy(source, width, height) {
  const target = new PNG({ width, height });
  for (let i = 0; i < target.data.length; i += 4) {
    target.data[i] = 255;
    target.data[i + 1] = 255;
    target.data[i + 2] = 255;
    target.data[i + 3] = 255;
  }
  for (let y = 0; y < source.height; y += 1) {
    for (let x = 0; x < source.width; x += 1) {
      const from = (source.width * y + x) << 2;
      const to = (width * y + x) << 2;
      target.data[to] = source.data[from];
      target.data[to + 1] = source.data[from + 1];
      target.data[to + 2] = source.data[from + 2];
      target.data[to + 3] = source.data[from + 3];
    }
  }
  return target;
}

function compareScreenshots(currentPath, baselinePath, diffPath) {
  const current = readPng(currentPath);
  const baseline = readPng(baselinePath);

  const width = Math.max(current.width, baseline.width);
  const height = Math.max(current.height, baseline.height);
  const currentPadded = paddedCopy(current, width, height);
  const baselinePadded = paddedCopy(baseline, width, height);
  const diff = new PNG({ width, height });

  const diffPixels = pixelmatch(
    baselinePadded.data,
    currentPadded.data,
    diff.data,
    width,
    height,
    { threshold: 0.1, includeAA: true, alpha: 0.5 },
  );

  writePng(diffPath, diff);
  return diffPixels / (width * height);
}

function relativeForReport(absolutePath) {
  return path.relative(CWD, absolutePath).split(path.sep).join("/");
}

async function sweepRoute(browser, settings, route, outDir, overrideScreenshots) {
  const context = await browser.newContext({
    viewport: settings.viewport,
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();

  const result = {
    name: route.name,
    path: route.path,
    status: "pass",
    console_errors: [],
    page_errors: [],
    failed_requests: [],
    http_errors: [],
    a11y: [],
    overflow_px: 0,
    screenshot: null,
    diff_ratio: 0,
  };

  page.on("console", (message) => {
    if (message.type() === "error" && result.console_errors.length < 5) {
      result.console_errors.push(message.text());
    }
  });
  page.on("pageerror", (error) => {
    result.page_errors.push(error?.message || String(error));
  });
  page.on("requestfailed", (request) => {
    result.failed_requests.push({
      url: request.url(),
      failure: request.failure()?.errorText || "unknown failure",
    });
  });
  page.on("response", (response) => {
    if (response.status() >= 400) {
      result.http_errors.push({ url: response.url(), status: response.status() });
    }
  });

  const url = new URL(route.path, settings.baseUrl).toString();
  try {
    await page.goto(url, { waitUntil: "load", timeout: 30000 });
  } catch (error) {
    result.page_errors.push(`navigation failed: ${error.message}`);
  }

  if (route.waitFor) {
    try {
      await page.waitForSelector(route.waitFor, { state: "attached", timeout: 10000 });
    } catch (error) {
      result.page_errors.push(
        `waitFor selector "${route.waitFor}" failed: ${error.message}`,
      );
    }
  }

  await page.waitForLoadState("networkidle", { timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(150);

  if (settings.a11y) {
    try {
      result.a11y = await page.evaluate(collectA11y);
    } catch (error) {
      result.page_errors.push(`a11y evaluation failed: ${error.message}`);
    }
  }

  try {
    const layout = await page.evaluate(collectLayout);
    result.overflow_px = layout.overflow_px;
  } catch (error) {
    result.page_errors.push(`layout evaluation failed: ${error.message}`);
  }

  if (overrideScreenshots) {
    const screenshotPath = path.join(outDir, "screens", `${route.fileName}.png`);
    try {
      await page.screenshot({ path: screenshotPath, fullPage: true });
      result.screenshot = relativeForReport(screenshotPath);
    } catch (error) {
      result.page_errors.push(`screenshot failed: ${error.message}`);
    }

    if (result.screenshot) {
      if (settings.updateBaseline) {
        fs.mkdirSync(settings.baselineDir, { recursive: true });
        fs.copyFileSync(
          screenshotPath,
          path.join(settings.baselineDir, `${route.fileName}.png`),
        );
      } else {
        const baselinePath = path.join(settings.baselineDir, `${route.fileName}.png`);
        if (fs.existsSync(baselinePath)) {
          try {
            const diffPath = path.join(outDir, "diff", `${route.fileName}.png`);
            result.diff_ratio = compareScreenshots(screenshotPath, baselinePath, diffPath);
          } catch (error) {
            result.page_errors.push(`pixel diff failed: ${error.message}`);
          }
        }
      }
    }
  }

  result.status = routePasses(result, settings.thresholds) ? "pass" : "fail";
  await context.close();
  return result;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log(USAGE);
    return 0;
  }
  if (!options.config) {
    throw new Error("--config is required");
  }
  if (options.updateBaseline && options.noScreenshots) {
    throw new Error("--update-baseline cannot be combined with --no-screenshots");
  }

  const settings = loadConfig(options.config);
  settings.updateBaseline = options.updateBaseline;
  const startedAt = new Date();
  const outDir = options.out
    ? resolveFromCwd(options.out)
    : path.join(resolveFromCwd(DEFAULT_OUT_ROOT), `run-${utcStamp(startedAt)}`);
  const overrideScreenshots = settings.screenshots && !options.noScreenshots;

  fs.mkdirSync(path.join(outDir, "screens"), { recursive: true });
  fs.mkdirSync(path.join(outDir, "diff"), { recursive: true });

  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-dev-shm-usage"],
    });

    const routes = [];
    for (const route of settings.routes) {
      routes.push(await sweepRoute(browser, settings, route, outDir, overrideScreenshots));
    }

    const durationMs = Date.now() - startedAt.getTime();
    const report = buildReport({
      baseUrl: settings.baseUrl,
      startedAt: startedAt.toISOString(),
      durationMs,
      routes,
      thresholds: settings.thresholds,
    });

    const reportJsonPath = path.join(outDir, "report.json");
    const reportMarkdownPath = path.join(outDir, "report.md");
    fs.writeFileSync(reportJsonPath, JSON.stringify(report, null, 2) + "\n");
    fs.writeFileSync(
      reportMarkdownPath,
      renderMarkdown(report, settings.thresholds) + "\n",
    );

    if (options.json) {
      console.log(JSON.stringify(report, null, 2));
    } else {
      console.log(`UI regression sweep: ${settings.baseUrl}`);
      for (const route of report.routes) {
        const mark = route.status === "pass" ? "PASS" : "FAIL";
        console.log(`  ${mark} ${route.name} (${route.path})`);
      }
      console.log(
        `Summary: ${report.summary.routes} routes, ${report.summary.passed} passed, ` +
          `${report.summary.failed} failed, ${report.summary.violations} violations`,
      );
      console.log(`Reports: ${relativeForReport(reportJsonPath)}, ${relativeForReport(reportMarkdownPath)}`);
    }

    return report.summary.failed > 0 ? 1 : 0;
  } finally {
    if (browser) await browser.close();
  }
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((error) => {
    console.error(`ui-regression: ${error.message}`);
    process.exitCode = 2;
  });
