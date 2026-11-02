import test from "node:test";
import assert from "node:assert/strict";
import {
  buildReport,
  countViolations,
  normalizeThresholds,
  renderMarkdown,
  routePasses,
  sanitizeRouteName,
} from "../lib/report.mjs";

const thresholds = normalizeThresholds({ pixelDiffRatio: 0.01 });

function route(overrides = {}) {
  return {
    name: "home",
    path: "/",
    status: "pass",
    console_errors: [],
    page_errors: [],
    failed_requests: [],
    http_errors: [],
    a11y: [],
    overflow_px: 0,
    screenshot: "tools/ui-regression/out/run/screens/home.png",
    diff_ratio: 0,
    ...overrides,
  };
}

test("normalizeThresholds fills defaults and rejects invalid values", () => {
  assert.equal(thresholds.maxConsoleErrors, 0);
  assert.equal(thresholds.pixelDiffRatio, 0.01);
  assert.throws(() => normalizeThresholds({ maxHttpErrors: -1 }), /non-negative/);
  assert.throws(() => normalizeThresholds({ maxHttpErrors: "x" }), /non-negative/);
});

test("sanitizeRouteName produces safe and stable file names", () => {
  assert.equal(sanitizeRouteName("home"), "home");
  assert.equal(sanitizeRouteName("admin/users"), "admin-users");
  assert.equal(sanitizeRouteName("  "), "route");
});

test("countViolations counts each category, overflow and pixel diff", () => {
  const result = route({
    console_errors: ["a"],
    page_errors: ["b", "c"],
    failed_requests: [{ url: "http://x", failure: "net::ERR" }],
    http_errors: [{ url: "http://x", status: 500 }],
    a11y: [
      { rule: "img-alt", selector: "img", detail: "missing" },
      { rule: "h1-count", selector: "h1", detail: "two" },
    ],
    overflow_px: 12,
    diff_ratio: 0.02,
  });
  assert.equal(countViolations(result, thresholds), 9);
});

test("routePasses respects the configured thresholds", () => {
  assert.equal(routePasses(route(), thresholds), true);
  assert.equal(routePasses(route({ overflow_px: 1 }), thresholds), false);
  assert.equal(routePasses(route({ diff_ratio: 0.005 }), thresholds), true);
  assert.equal(routePasses(route({ diff_ratio: 0.02 }), thresholds), false);
});

test("buildReport computes summary counts", () => {
  const report = buildReport({
    baseUrl: "http://127.0.0.1:8765",
    startedAt: "2026-01-01T00:00:00.000Z",
    durationMs: 123,
    thresholds,
    routes: [
      route(),
      route({ name: "broken", status: "fail", console_errors: ["boom"], overflow_px: 5 }),
    ],
  });

  assert.deepEqual(report.summary, {
    routes: 2,
    passed: 1,
    failed: 1,
    violations: 2,
  });
});

test("renderMarkdown keeps clean routes to a single summary line", () => {
  const report = buildReport({
    baseUrl: "http://127.0.0.1:8765",
    startedAt: "2026-01-01T00:00:00.000Z",
    durationMs: 10,
    thresholds,
    routes: [route()],
  });
  const markdown = renderMarkdown(report, thresholds);
  assert.match(markdown, /## home — PASS/);
  assert.match(markdown, /No violations\./);
  assert.match(markdown, /Violations: 0/);
});

test("renderMarkdown includes a violation breakdown for failing routes", () => {
  const report = buildReport({
    baseUrl: "http://127.0.0.1:8765",
    startedAt: "2026-01-01T00:00:00.000Z",
    durationMs: 10,
    thresholds,
    routes: [
      route({
        name: "broken",
        status: "fail",
        page_errors: ["ReferenceError: boom"],
        a11y: [{ rule: "img-alt", selector: "img", detail: "missing alt" }],
      }),
    ],
  });
  const markdown = renderMarkdown(report, thresholds);
  assert.match(markdown, /## broken — FAIL/);
  assert.match(markdown, /page errors \(1\/0\)/);
  assert.match(markdown, /`img-alt` img — missing alt/);
});
