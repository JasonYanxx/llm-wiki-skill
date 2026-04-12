import fs from "node:fs";
import path from "node:path";
import type { Request, Response } from "express";
import type { ServerConfig } from "../config.js";

export interface TreeNode {
  name: string;
  path: string; // relative to wikiRoot
  kind: "file" | "dir";
  children?: TreeNode[];
}

/**
 * Build a navigation tree from the canonical workbench surfaces.
 * The tree is recursive, sorted, and only includes `indexes/` plus `compiled/`
 * markdown content. `compiled/_meta/` is intentionally hidden.
 */
export function buildTree(wikiRoot: string): TreeNode {
  const children: TreeNode[] = [];
  for (const rel of ["indexes", "compiled"]) {
    const dir = path.join(wikiRoot, rel);
    if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) continue;
    children.push(walk(wikiRoot, dir, rel));
  }
  return { name: "workbench", path: "", kind: "dir", children };
}

function walk(wikiRoot: string, dir: string, rel: string): TreeNode {
  const relParts = rel.split("/");
  if (relParts[0] === "compiled" && relParts[1] === "_meta") {
    return { name: "_meta", path: rel, kind: "dir", children: [] };
  }
  const entries = fs
    .readdirSync(dir, { withFileTypes: true })
    .filter((e) => !e.name.startsWith("."))
    .filter((e) => !(rel === "compiled" && e.name === "_meta"))
    .sort((a, b) => {
      if (a.isDirectory() !== b.isDirectory()) return a.isDirectory() ? -1 : 1;
      return a.name.localeCompare(b.name);
    });

  const children: TreeNode[] = [];
  for (const e of entries) {
    const full = path.join(dir, e.name);
    const nodeRel = path.posix.join(rel, e.name);
    if (e.isDirectory()) {
      children.push(walk(wikiRoot, full, nodeRel));
    } else if (e.name.endsWith(".md")) {
      children.push({ name: e.name.replace(/\.md$/, ""), path: nodeRel, kind: "file" });
    }
  }

  return { name: path.basename(dir), path: rel, kind: "dir", children };
}

export function handleTree(cfg: ServerConfig) {
  return (_req: Request, res: Response) => {
    res.json(buildTree(cfg.wikiRoot));
  };
}
