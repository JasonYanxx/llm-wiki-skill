import fs from "node:fs";
import path from "node:path";
import type { Request, Response } from "express";
import type { ServerConfig } from "../config.js";
import { createRenderer } from "../render/markdown.js";

const ALLOWED_ASSET_EXTENSIONS = new Set([
  ".avif",
  ".bmp",
  ".gif",
  ".heic",
  ".jpeg",
  ".jpg",
  ".m4a",
  ".mov",
  ".mp3",
  ".mp4",
  ".ogg",
  ".pdf",
  ".png",
  ".tif",
  ".tiff",
  ".wav",
  ".webm",
  ".webp",
]);

export function handlePage(cfg: ServerConfig) {
  return (req: Request, res: Response) => {
    const relRaw = (req.query.path as string | undefined) ?? "";
    const rel = safeRel(relRaw, "indexes/Home.md");
    if (!rel) {
      res.status(400).json({ error: "missing or invalid `path` query" });
      return;
    }

    const full = resolveMarkdownPath(cfg.wikiRoot, rel);
    if (!full) {
      res.status(404).json({ error: "file not found", path: rel });
      return;
    }

    // Guarantee the resolved path is still inside wikiRoot.
    const relFromRoot = path.relative(cfg.wikiRoot, full);
    if (relFromRoot.startsWith("..") || path.isAbsolute(relFromRoot)) {
      res.status(403).json({ error: "path escapes workbench root" });
      return;
    }

    const rawMarkdown = fs.readFileSync(full, "utf-8");
    const renderer = createRenderer({
      wikiRoot: cfg.wikiRoot,
      pagePath: relFromRoot.split(path.sep).join("/"),
    });
    const rendered = renderer.render(rawMarkdown);
    res.json({
      path: relFromRoot.split(path.sep).join("/"),
      title: rendered.title,
      frontmatter: rendered.frontmatter,
      html: rendered.html,
      raw: rendered.rawMarkdown,
    });
  };
}

export function handleRaw(cfg: ServerConfig) {
  return (req: Request, res: Response) => {
    const relRaw = (req.query.path as string | undefined) ?? "";
    const rel = safeRel(relRaw);
    if (!rel) {
      res.status(400).send("bad path");
      return;
    }
    const full = path.join(cfg.wikiRoot, rel);
    if (!fs.existsSync(full) || !fs.statSync(full).isFile()) {
      res.status(404).send("not found");
      return;
    }
    res.type("text/markdown").send(fs.readFileSync(full));
  };
}

export function handleFile(cfg: ServerConfig) {
  return (req: Request, res: Response) => {
    const relRaw = (req.query.path as string | undefined) ?? "";
    const rel = safeRel(relRaw);
    if (!rel) {
      res.status(400).send("bad path");
      return;
    }
    const full = path.resolve(cfg.wikiRoot, rel);
    const relFromRoot = path.relative(cfg.wikiRoot, full);
    if (relFromRoot.startsWith("..") || path.isAbsolute(relFromRoot)) {
      res.status(403).send("forbidden");
      return;
    }
    if (!isAllowedAssetPath(relFromRoot)) {
      res.status(403).send("forbidden");
      return;
    }
    if (!fs.existsSync(full) || !fs.statSync(full).isFile()) {
      res.status(404).send("not found");
      return;
    }
    const realRoot = fs.realpathSync.native(cfg.wikiRoot);
    const realFull = fs.realpathSync.native(full);
    const relFromRealRoot = path.relative(realRoot, realFull);
    if (relFromRealRoot.startsWith("..") || path.isAbsolute(relFromRealRoot)) {
      res.status(403).send("forbidden");
      return;
    }
    res.sendFile(realFull);
  };
}

function safeRel(input: string, fallback?: string): string | null {
  if (!input) return fallback ?? null;
  // Reject absolute and ..
  if (path.isAbsolute(input)) return null;
  const normalized = path.posix.normalize(input);
  if (normalized.startsWith("..")) return null;
  return normalized;
}

function isAllowedAssetPath(relPath: string): boolean {
  const ext = path.extname(relPath).toLowerCase();
  return ALLOWED_ASSET_EXTENSIONS.has(ext);
}

function resolveMarkdownPath(root: string, rel: string): string | null {
  const prefixes = ["", "indexes", "compiled", "raw", "outputs", "wiki"];
  const seen = new Set<string>();

  const addCandidate = (candidate: string): void => {
    const normalized = path.posix.normalize(candidate);
    if (!normalized.startsWith("..")) seen.add(normalized);
  };

  addCandidate(rel);
  if (!rel.endsWith(".md")) addCandidate(`${rel}.md`);
  addCandidate(path.posix.join(rel, "index.md"));

  for (const prefix of prefixes) {
    if (!prefix || rel.startsWith(`${prefix}/`)) continue;
    addCandidate(path.posix.join(prefix, rel));
    if (!rel.endsWith(".md")) addCandidate(path.posix.join(prefix, `${rel}.md`));
    addCandidate(path.posix.join(prefix, rel, "index.md"));
  }

  for (const candidate of seen) {
    const full = path.join(root, candidate);
    if (fs.existsSync(full) && fs.statSync(full).isFile()) return full;
    if (fs.existsSync(full) && fs.statSync(full).isDirectory()) {
      const index = path.join(full, "index.md");
      if (fs.existsSync(index) && fs.statSync(index).isFile()) return index;
    }
  }
  return null;
}
