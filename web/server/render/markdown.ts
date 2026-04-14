import MarkdownIt from "markdown-it";
import anchor from "markdown-it-anchor";
// @ts-expect-error - no types shipped
import attrs from "markdown-it-attrs";
// @ts-expect-error - no types shipped
import texmath from "markdown-it-texmath";
import katex from "katex";
import path from "node:path";
import fs from "node:fs";
import { wikilinksPlugin, type WikilinkResolver } from "./wikilinks.js";

export interface RenderedPage {
  html: string;
  frontmatter: Record<string, unknown> | null;
  rawMarkdown: string;
  title: string | null;
}

export interface RendererOptions {
  wikiRoot: string;
  pagePath: string;
}

export function createRenderer(opts: RendererOptions) {
  const assetIndex = new Map<string, string | null>();
  const md = new MarkdownIt({
    html: false,
    linkify: true,
    typographer: false,
    breaks: false,
  });

  md.use(attrs, {});
  md.use(anchor, {
    permalink: anchor.permalink.linkInsideHeader({
      symbol: "§",
      placement: "before",
    }),
  });
  md.use(texmath, {
    engine: katex,
    delimiters: "dollars",
    katexOptions: { throwOnError: false, strict: false },
  });

  const resolver: WikilinkResolver = (target) => {
    if (isImageTarget(target)) {
      const asset = resolveAssetPath(opts.wikiRoot, opts.pagePath, target, assetIndex);
      return {
        href: `/api/file?path=${encodeURIComponent(asset ?? target)}`,
        exists: Boolean(asset),
      };
    }
    // Try a few resolutions: exact relative path, match by stem under wiki/.
    const candidate = findPage(opts.wikiRoot, target);
    if (candidate) {
      const rel = path.relative(opts.wikiRoot, candidate).split(path.sep).join("/");
      return {
        href: `/?page=${encodeURIComponent(rel)}`,
        exists: true,
      };
    }
    return {
      href: `/?page=${encodeURIComponent(target)}`,
      exists: false,
    };
  };

  md.use(wikilinksPlugin, resolver);

  const defaultImage =
    md.renderer.rules.image ??
    ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options));
  md.renderer.rules.image = (tokens, idx, options, env, self) => {
    const tok = tokens[idx]!;
    const src = tok.attrGet("src") ?? "";
    const asset = resolveAssetPath(opts.wikiRoot, opts.pagePath, src, assetIndex);
    if (asset) tok.attrSet("src", `/api/file?path=${encodeURIComponent(asset)}`);
    tok.attrJoin("class", "markdown-image");
    return defaultImage(tokens, idx, options, env, self);
  };

  // Attach data-source-line to every top-level block token so the client can
  // map DOM selections back to source lines.
  md.core.ruler.push("source-line", (state) => {
    for (const tok of state.tokens) {
      if (tok.map && tok.level === 0 && tok.type.endsWith("_open")) {
        tok.attrSet("data-source-line", `${tok.map[0]},${tok.map[1]}`);
      }
    }
  });

  // Customize fence rendering so mermaid blocks are left for the client to render.
  const defaultFence = md.renderer.rules.fence!;
  md.renderer.rules.fence = (tokens, idx, options, env, self) => {
    const tok = tokens[idx]!;
    const info = (tok.info || "").trim();
    const lang = info.split(/\s+/)[0];
    if (lang === "mermaid") {
      const line =
        tok.map && tok.level === 0
          ? ` data-source-line="${tok.map[0]},${tok.map[1]}"`
          : "";
      return `<pre class="mermaid-block"${line}><code class="language-mermaid">${escapeHtml(tok.content)}</code></pre>\n`;
    }
    return defaultFence(tokens, idx, options, env, self);
  };

  return {
    render(rawMarkdown: string): RenderedPage {
      const { frontmatter, body, title } = stripFrontmatter(rawMarkdown);
      const html = md.render(body);
      return { html, frontmatter, rawMarkdown, title };
    },
  };
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function isExternalUrl(target: string): boolean {
  return /^[a-z][a-z0-9+.-]*:/i.test(target) || target.startsWith("//");
}

function decodePath(target: string): string {
  try {
    return decodeURIComponent(target);
  } catch {
    return target;
  }
}

function isImageTarget(target: string): boolean {
  const clean = target.split("#")[0]!.split("?")[0]!;
  return /\.(png|jpe?g|gif|webp|svg|bmp|heic|tiff)$/i.test(clean);
}

function resolveAssetPath(
  wikiRoot: string,
  pagePath: string,
  target: string,
  cache: Map<string, string | null>,
): string | null {
  if (!target || isExternalUrl(target)) return null;

  const decoded = decodePath(target).replace(/\\/g, "/");
  const withoutHash = decoded.split("#")[0]!.split("?")[0]!;
  const normalizedTarget = withoutHash.startsWith("/") ? withoutHash.slice(1) : withoutHash;
  const noteDir = path.posix.dirname(pagePath);
  const candidates = new Set<string>();

  const addCandidate = (candidate: string): void => {
    const normalized = path.posix.normalize(candidate);
    if (!normalized.startsWith("..")) candidates.add(normalized);
  };

  addCandidate(path.posix.join(noteDir, normalizedTarget));
  addCandidate(normalizedTarget);

  const base = path.posix.basename(normalizedTarget);
  addCandidate(path.posix.join("图片", base));

  for (const candidate of candidates) {
    const full = path.join(wikiRoot, candidate);
    if (fs.existsSync(full) && fs.statSync(full).isFile()) return candidate;
  }

  if (!base) return null;
  if (cache.has(base)) return cache.get(base) ?? null;

  const found = findByFilename(wikiRoot, base);
  const rel = found ? path.relative(wikiRoot, found).split(path.sep).join("/") : null;
  cache.set(base, rel);
  return rel;
}

function findByFilename(dir: string, target: string): string | null {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === ".git" || entry.name === "node_modules") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      const hit = findByFilename(full, target);
      if (hit) return hit;
    } else if (entry.isFile() && entry.name === target) {
      return full;
    }
  }
  return null;
}

const FRONTMATTER_RE = /^---\n([\s\S]*?)\n---\n?/;

function stripFrontmatter(text: string): {
  frontmatter: Record<string, unknown> | null;
  body: string;
  title: string | null;
} {
  const m = FRONTMATTER_RE.exec(text);
  let frontmatter: Record<string, unknown> | null = null;
  let body = text;
  if (m) {
    // We don't need full YAML parsing here — keep it for display only.
    frontmatter = {};
    for (const line of m[1]!.split("\n")) {
      const idx = line.indexOf(":");
      if (idx < 0) continue;
      frontmatter[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    }
    body = text.slice(m[0].length);
  }
  const h1 = /^#\s+(.+?)\s*$/m.exec(body);
  const title =
    (frontmatter && typeof frontmatter.title === "string" && (frontmatter.title as string)) ||
    (h1 && h1[1]) ||
    null;
  return { frontmatter, body, title };
}

/**
 * Resolve a wikilink target to a file under wikiRoot. Tries:
 *   - the exact relative path as given
 *   - that path + ".md"
 *   - that path + "/index.md"
 *   - the same three forms under canonical roots (`indexes/`, `compiled/`,
 *     `raw/`, `outputs/`) and legacy `wiki/`
 *   - a search for any md file whose stem or basename matches the target
 */
export function findPage(wikiRoot: string, target: string): string | null {
  const tryPath = (rel: string): string | null => {
    const full = path.join(wikiRoot, rel);
    if (fs.existsSync(full) && fs.statSync(full).isFile()) return full;
    if (fs.existsSync(full) && fs.statSync(full).isDirectory()) {
      const index = path.join(full, "index.md");
      if (fs.existsSync(index) && fs.statSync(index).isFile()) return index;
    }
    return null;
  };

  const candidates = [
    target,
    `${target}.md`,
    path.posix.join(target, "index.md"),
  ];
  const roots = ["indexes", "compiled", "raw", "outputs", "wiki"];

  for (const candidate of candidates) {
    const direct = tryPath(candidate);
    if (direct) return direct;
  }
  for (const root of roots) {
    if (target.startsWith(`${root}/`)) continue;
    for (const candidate of candidates) {
      const direct = tryPath(path.posix.join(root, candidate));
      if (direct) return direct;
    }
  }

  for (const root of ["compiled", "indexes", "raw", "wiki"]) {
    const base = path.join(wikiRoot, root);
    if (!fs.existsSync(base)) continue;
    const match = findByStem(base, target) || findByStem(base, path.posix.basename(target));
    if (match) return match;
  }
  return null;
}

function findByStem(dir: string, target: string): string | null {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      const sub = findByStem(full, target);
      if (sub) return sub;
    } else if (e.isFile() && e.name.endsWith(".md")) {
      const stem = e.name.replace(/\.md$/, "");
      if (stem === target || e.name === target) return full;
    }
  }
  return null;
}
