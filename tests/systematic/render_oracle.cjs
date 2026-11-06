// Oracle cho bộ kiểm hệ thống S1/S2: dùng ĐÚNG renderer của web (markdown-to-jsx, cùng options với
// web_ui/src/components/chat-widget.tsx) và new URL() của Node (chuẩn WHATWG như trình duyệt).
//
// stdin : JSON {"texts": [...], "urls": [...], "allowlist": [...], "base": "https://shop.example/chat"}
// stdout: JSON {"texts": [[{tag, url, protocol, host, web_safe}...]...], "urls": [{protocol, host, error}...]}
//
// Không sửa web; checkUrlSafety() dưới đây chép logic từ chat-widget.tsx:73-147 để biết lớp chặn cuối
// của web có cho URL đó hiển thị hay không.
"use strict";
const path = require("path");
const { createRequire } = require("module");

const webUi = process.env.FOX_WEB_UI || "D:/create/DATN/Agenttic-RAG-for-e-commerce/web_ui";
const req = createRequire(path.join(webUi, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const mtj = req("markdown-to-jsx");
const Markdown = mtj.default || mtj.Markdown || mtj;

function resolve(url, base) {
  try {
    const u = new URL(url, base);
    return { protocol: u.protocol, host: u.hostname.toLowerCase(), error: null };
  } catch (e) {
    return { protocol: null, host: null, error: String(e.message || e) };
  }
}

function checkUrlSafety(urlString, base, allowlist) {
  if (!urlString || typeof urlString !== "string") return { safe: false, isInternal: false };
  const trimmed = urlString.trim();
  const lower = trimmed.toLowerCase();
  if (lower.startsWith("javascript:") || lower.startsWith("data:") || lower.startsWith("vbscript:") ||
      trimmed.startsWith("//") || trimmed.includes("\\") || lower.includes("%5c")) {
    return { safe: false, isInternal: false };
  }
  if (trimmed.startsWith("#")) return { safe: true, isInternal: true };
  try {
    const origin = new URL(base).origin;
    const parsed = new URL(trimmed, origin);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return { safe: false, isInternal: false };
    const isInternal = parsed.origin === origin && trimmed.startsWith("/") && !trimmed.startsWith("//") &&
      !trimmed.includes("\\") && !lower.includes("%5c");
    if (isInternal) return { safe: true, isInternal: true };
    const hostname = parsed.hostname.toLowerCase();
    const isHomoglyph = hostname.startsWith("xn--") || hostname.includes(".xn--");
    const allowed = allowlist.some((a) => hostname === a || hostname.endsWith("." + a));
    return { safe: allowed && !isHomoglyph, isInternal: false };
  } catch {
    return { safe: false, isInternal: false };
  }
}

function renderUrls(text, base, allowlist) {
  const found = [];
  const record = (tag, attr) => (props) => {
    const url = props[attr];
    if (typeof url === "string") {
      const r = resolve(url, base);
      found.push({ tag, url, protocol: r.protocol, host: r.host,
                   web_safe: checkUrlSafety(url, base, allowlist).safe });
    }
    return React.createElement("span", null, props.children || null);
  };
  const element = React.createElement(Markdown, {
    options: {
      disableParsingRawHTML: true,
      overrides: { a: { component: record("a", "href") }, img: { component: record("img", "src") } },
    },
  }, text);
  try {
    renderToStaticMarkup(element);
  } catch (e) {
    found.push({ tag: "error", url: String(e.message || e), protocol: null, host: null, web_safe: false });
  }
  return found;
}

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => { input += chunk; });
process.stdin.on("end", () => {
  const job = JSON.parse(input);
  const base = job.base || "https://shop.example/chat";
  const allowlist = (job.allowlist || ["shop.example"]).map((a) => a.toLowerCase());
  const out = {
    texts: (job.texts || []).map((t) => renderUrls(t, base, allowlist)),
    urls: (job.urls || []).map((u) => resolve(u, base)),
  };
  process.stdout.write(JSON.stringify(out));
});
