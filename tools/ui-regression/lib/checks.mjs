/**
 * DOM / accessibility / layout heuristics.
 *
 * `collectA11y` and `collectLayout` are passed directly to `page.evaluate()`,
 * so they must be fully self-contained (no references to module scope).
 */

export function collectA11y() {
  const violations = [];

  const text = (el) => (el && el.textContent ? el.textContent : "").replace(/\s+/g, " ").trim();
  const attr = (el, name) => {
    const value = el.getAttribute(name);
    return value == null ? "" : value.trim();
  };
  const byIdText = (id) => {
    if (!id) return "";
    return text(document.getElementById(id));
  };
  const labelledByText = (el) => {
    const ids = attr(el, "aria-labelledby").split(/\s+/).filter(Boolean);
    return ids.map(byIdText).join(" ").trim();
  };

  const cssPath = (el) => {
    if (!el || el.nodeType !== 1) return "";
    if (el === document.documentElement) return "html";
    if (el === document.body) return "body";

    const escape = (value) =>
      typeof CSS !== "undefined" && CSS.escape ? CSS.escape(value) : value;

    const parts = [];
    let current = el;
    while (current && current.nodeType === 1) {
      if (current === document.body) {
        parts.unshift("body");
        break;
      }
      if (current === document.documentElement) {
        parts.unshift("html");
        break;
      }
      const id = current.getAttribute("id");
      if (id) {
        parts.unshift("#" + escape(id));
        break;
      }
      let part = current.tagName.toLowerCase();
      const classes = (current.getAttribute("class") || "")
        .trim()
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2);
      if (classes.length) part += "." + classes.map(escape).join(".");
      const parent = current.parentElement;
      if (parent) {
        const sameTag = Array.from(parent.children).filter(
          (sibling) => sibling.tagName === current.tagName,
        );
        if (sameTag.length > 1) {
          part += ":nth-of-type(" + (sameTag.indexOf(current) + 1) + ")";
        }
      }
      parts.unshift(part);
      current = current.parentElement;
    }
    return parts.join(" > ");
  };

  const add = (rule, el, selector, detail) => {
    violations.push({
      rule,
      selector: selector || cssPath(el),
      detail,
    });
  };

  if (!attr(document.documentElement, "lang")) {
    add("html-lang", document.documentElement, "html", "<html> is missing a non-empty lang attribute");
  }

  for (const img of document.querySelectorAll("img:not([alt])")) {
    add("img-alt", img, undefined, "<img> is missing an alt attribute");
  }

  for (const button of document.querySelectorAll("button")) {
    const name =
      text(button) ||
      attr(button, "aria-label") ||
      labelledByText(button) ||
      attr(button, "title");
    if (!name) {
      add("button-name", button, undefined, "<button> has no accessible name");
    }
  }

  for (const input of document.querySelectorAll("input:not([type=hidden])")) {
    const id = attr(input, "id");
    const explicitLabel = id
      ? Array.from(document.querySelectorAll("label")).some(
          (label) => label.getAttribute("for") === id && text(label),
        )
      : false;
    const wrappingLabel = input.closest("label") && text(input.closest("label"));
    const name =
      explicitLabel ||
      wrappingLabel ||
      attr(input, "aria-label") ||
      labelledByText(input) ||
      attr(input, "placeholder");
    if (!name) {
      add("input-label", input, undefined, "<input> has no associated label or accessible name");
    }
  }

  for (const link of document.querySelectorAll("a")) {
    const name = text(link) || attr(link, "aria-label");
    if (!name) {
      add("link-name", link, undefined, "<a> has no text content or aria-label");
    }
  }

  const h1s = document.querySelectorAll("h1");
  if (h1s.length !== 1) {
    add(
      "h1-count",
      h1s[0] || document.body,
      "h1",
      h1s.length === 0
        ? "page has no <h1> element"
        : "page has " + h1s.length + " <h1> elements (expected exactly 1)",
    );
  }

  const idCounts = new Map();
  for (const el of document.querySelectorAll("[id]")) {
    const id = el.getAttribute("id");
    if (!id) continue;
    idCounts.set(id, (idCounts.get(id) || 0) + 1);
  }
  for (const [id, count] of idCounts) {
    if (count > 1) {
      add("duplicate-id", undefined, "#" + id, 'id "' + id + '" appears ' + count + " times");
    }
  }

  return violations.sort((a, b) =>
    (a.rule + "\u0000" + a.selector).localeCompare(b.rule + "\u0000" + b.selector),
  );
}

export function collectLayout() {
  const root = document.documentElement;
  return {
    overflow_px: Math.max(0, root.scrollWidth - root.clientWidth),
    scrollWidth: root.scrollWidth,
    clientWidth: root.clientWidth,
  };
}
