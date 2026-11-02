const DEFAULT_THRESHOLDS = {
  maxConsoleErrors: 0,
  maxPageErrors: 0,
  maxFailedRequests: 0,
  maxHttpErrors: 0,
  maxA11yViolations: 0,
  maxLayoutOverflowPx: 0,
  pixelDiffRatio: 0.002,
};

export function normalizeThresholds(thresholds = {}) {
  const merged = { ...DEFAULT_THRESHOLDS };
  for (const key of Object.keys(DEFAULT_THRESHOLDS)) {
    if (thresholds[key] !== undefined) {
      const value = Number(thresholds[key]);
      if (!Number.isFinite(value) || value < 0) {
        throw new Error(`threshold "${key}" must be a non-negative number`);
      }
      merged[key] = value;
    }
  }
  return merged;
}

export function sanitizeRouteName(name) {
  return String(name)
    .trim()
    .replace(/[^a-zA-Z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "") || "route";
}

export function countViolations(route, thresholds) {
  const t = thresholds || DEFAULT_THRESHOLDS;
  const overflowExceeded = (route.overflow_px || 0) > t.maxLayoutOverflowPx ? 1 : 0;
  const pixelExceeded = (route.diff_ratio || 0) > t.pixelDiffRatio ? 1 : 0;
  return (
    (route.console_errors || []).length +
    (route.page_errors || []).length +
    (route.failed_requests || []).length +
    (route.http_errors || []).length +
    (route.a11y || []).length +
    overflowExceeded +
    pixelExceeded
  );
}

export function routePasses(route, thresholds) {
  const t = thresholds || DEFAULT_THRESHOLDS;
  return (
    (route.console_errors || []).length <= t.maxConsoleErrors &&
    (route.page_errors || []).length <= t.maxPageErrors &&
    (route.failed_requests || []).length <= t.maxFailedRequests &&
    (route.http_errors || []).length <= t.maxHttpErrors &&
    (route.a11y || []).length <= t.maxA11yViolations &&
    (route.overflow_px || 0) <= t.maxLayoutOverflowPx &&
    (route.diff_ratio || 0) <= t.pixelDiffRatio
  );
}

export function buildReport({ baseUrl, startedAt, durationMs, routes, thresholds }) {
  const t = thresholds || DEFAULT_THRESHOLDS;
  const passed = routes.filter((route) => route.status === "pass").length;
  const failed = routes.length - passed;
  const violations = routes.reduce(
    (total, route) => total + countViolations(route, t),
    0,
  );
  return {
    baseUrl,
    started_at: startedAt,
    duration_ms: durationMs,
    routes,
    summary: {
      routes: routes.length,
      passed,
      failed,
      violations,
    },
  };
}

function bulletList(items) {
  return items.map((item) => `  - ${item}`).join("\n");
}

export function renderMarkdown(report, thresholds) {
  const t = thresholds || DEFAULT_THRESHOLDS;
  const lines = [];
  lines.push("# UI Regression Report");
  lines.push("");
  lines.push(`- Base URL: ${report.baseUrl}`);
  lines.push(`- Started: ${report.started_at}`);
  lines.push(`- Duration: ${report.duration_ms} ms`);
  lines.push(
    `- Routes: ${report.summary.routes} (passed ${report.summary.passed}, failed ${report.summary.failed})`,
  );
  lines.push(`- Violations: ${report.summary.violations}`);
  lines.push("");

  for (const route of report.routes) {
    const label = route.status === "pass" ? "PASS" : "FAIL";
    lines.push(`## ${route.name} — ${label}`);
    lines.push("");
    lines.push(`Path: \`${route.path}\``);
    lines.push("");

    if (route.status === "pass" && countViolations(route, t) === 0) {
      lines.push("No violations.");
      if (route.screenshot) lines.push(`Screenshot: \`${route.screenshot}\``);
      lines.push("");
      continue;
    }

    if ((route.console_errors || []).length) {
      lines.push(
        `- console errors (${route.console_errors.length}/${t.maxConsoleErrors}):`,
      );
      lines.push(bulletList(route.console_errors.map((message) => `\`${message}\``)));
    }
    if ((route.page_errors || []).length) {
      lines.push(`- page errors (${route.page_errors.length}/${t.maxPageErrors}):`);
      lines.push(bulletList(route.page_errors.map((message) => `\`${message}\``)));
    }
    if ((route.failed_requests || []).length) {
      lines.push(
        `- failed requests (${route.failed_requests.length}/${t.maxFailedRequests}):`,
      );
      lines.push(
        bulletList(
          route.failed_requests.map((item) => `\`${item.url}\` — ${item.failure}`),
        ),
      );
    }
    if ((route.http_errors || []).length) {
      lines.push(`- HTTP errors (${route.http_errors.length}/${t.maxHttpErrors}):`);
      lines.push(
        bulletList(
          route.http_errors.map((item) => `${item.status} \`${item.url}\``),
        ),
      );
    }
    if ((route.a11y || []).length) {
      lines.push(
        `- a11y violations (${route.a11y.length}/${t.maxA11yViolations}):`,
      );
      lines.push(
        bulletList(
          route.a11y.map(
            (item) => `\`${item.rule}\` ${item.selector} — ${item.detail}`,
          ),
        ),
      );
    }
    if ((route.overflow_px || 0) > t.maxLayoutOverflowPx) {
      lines.push(
        `- layout overflow: ${route.overflow_px}px (max ${t.maxLayoutOverflowPx}px)`,
      );
    }
    if ((route.diff_ratio || 0) > t.pixelDiffRatio) {
      lines.push(
        `- pixel diff ratio: ${(route.diff_ratio || 0).toFixed(6)} (max ${t.pixelDiffRatio})`,
      );
    }
    if (route.screenshot) lines.push(`- screenshot: \`${route.screenshot}\``);
    lines.push("");
  }

  return lines.join("\n");
}
