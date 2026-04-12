import fs from "node:fs";
import path from "node:path";
import type { Request, Response } from "express";
import type { ServerConfig } from "../config.js";

export interface GraphNode {
  id: string; // path relative to wikiRoot, e.g. "compiled/knowledge/Calibration.md"
  label: string; // display name
  path: string; // same as id, kept explicit for client
  group: string; // projects | ideas | knowledge | people | review | other
  degree: number; // in + out link count, used for node sizing
  title: string | null;
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

const WIKILINK_RE = /\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]/g;

export function buildGraph(wikiRoot: string): GraphData {
  const compiledDir = path.join(wikiRoot, "compiled");
  if (!fs.existsSync(compiledDir)) return { nodes: [], edges: [] };

  const files = collectMdFiles(compiledDir).filter((f) => !f.includes(`${path.sep}_meta${path.sep}`));
  const registryByPath = loadRegistryByPath(wikiRoot);

  // Build a lookup keyed by common wikilink forms so graph edges follow the
  // compiled object layer without foregrounding raw/index pages.
  const byKey: Map<string, string> = new Map(); // key → rel-from-wikiRoot path
  const nodes: Map<string, GraphNode> = new Map();

  for (const f of files) {
    const relFromRoot = path.relative(wikiRoot, f).split(path.sep).join("/");
    const relFromCompiled = path.relative(compiledDir, f).split(path.sep).join("/");
    const registryObject = registryByPath.get(relFromRoot);
    const stem = path.basename(f, ".md");
    const isIndex = stem === "index";
    const fallbackLabel = isIndex ? path.basename(path.dirname(f)) : stem;
    const title = registryObject?.title ?? extractTitle(fs.readFileSync(f, "utf-8")) ?? fallbackLabel;
    const group = normalizeGroup(registryObject?.type ?? relFromCompiled.split("/")[0] ?? "other");
    const id = relFromRoot;

    const node: GraphNode = {
      id,
      label: fallbackLabel,
      path: id,
      group,
      degree: 0,
      title,
    };
    nodes.set(id, node);
    indexKey(byKey, relFromRoot, id);
    indexKey(byKey, relFromRoot.replace(/\.md$/, ""), id);
    indexKey(byKey, relFromCompiled, id);
    indexKey(byKey, relFromCompiled.replace(/\.md$/, ""), id);
    indexKey(byKey, stem, id);
    indexKey(byKey, fallbackLabel, id);
    if (title) indexKey(byKey, title, id);
    if (isIndex) {
      indexKey(byKey, path.dirname(relFromRoot), id);
      indexKey(byKey, path.dirname(relFromCompiled), id);
      indexKey(byKey, path.basename(path.dirname(f)), id);
    }
  }

  // Pass 2: build edges. Parse wikilinks per file and resolve targets.
  const edges: GraphEdge[] = [];
  const seenEdges = new Set<string>();
  for (const f of files) {
    const relFromRoot = path.relative(wikiRoot, f).split(path.sep).join("/");
    const srcId = relFromRoot;
    const text = fs.readFileSync(f, "utf-8");
    WIKILINK_RE.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = WIKILINK_RE.exec(text))) {
      const target = m[1]!.trim();
      if (target.startsWith("#")) continue; // anchor-only links — ignore
      const tgtId =
        byKey.get(target) ??
        byKey.get(target.replace(/\.md$/, "")) ??
        byKey.get(target.toLowerCase()) ??
        byKey.get(path.posix.basename(target)) ??
        byKey.get(path.posix.basename(target).toLowerCase()) ??
        byKey.get(path.posix.dirname(target)) ??
        byKey.get(target.toLowerCase());
      if (!tgtId || tgtId === srcId) continue;

      const key = `${srcId}→${tgtId}`;
      if (seenEdges.has(key)) continue;
      seenEdges.add(key);
      edges.push({ source: srcId, target: tgtId });

      nodes.get(srcId)!.degree += 1;
      nodes.get(tgtId)!.degree += 1;
    }
  }

  return {
    nodes: Array.from(nodes.values()),
    edges,
  };
}

function collectMdFiles(dir: string): string[] {
  const out: string[] = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name.startsWith(".")) continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...collectMdFiles(full));
    else if (e.isFile() && e.name.endsWith(".md")) out.push(full);
  }
  return out;
}

function loadRegistryByPath(wikiRoot: string): Map<string, { title?: string; type?: string }> {
  const registryPath = path.join(wikiRoot, "compiled", "_meta", "registry.json");
  if (!fs.existsSync(registryPath)) return new Map();
  try {
    const parsed = JSON.parse(fs.readFileSync(registryPath, "utf-8")) as {
      objects?: Array<{ path?: string; title?: string; type?: string }>;
    };
    const out = new Map<string, { title?: string; type?: string }>();
    for (const obj of parsed.objects ?? []) {
      if (obj.path) out.set(obj.path, { title: obj.title, type: obj.type });
    }
    return out;
  } catch {
    return new Map();
  }
}

function extractTitle(text: string): string | null {
  // frontmatter title
  const fm = /^---\n([\s\S]*?)\n---/.exec(text);
  if (fm) {
    const t = /^title:\s*(.+)$/m.exec(fm[1]!);
    if (t) return t[1]!.trim().replace(/^["']|["']$/g, "");
  }
  const h1 = /^#\s+(.+?)\s*$/m.exec(text);
  return h1 ? h1[1]! : null;
}

function indexKey(map: Map<string, string>, key: string, id: string): void {
  const normalized = key.trim();
  if (!normalized) return;
  map.set(normalized, id);
  map.set(normalized.toLowerCase(), id);
}

function normalizeGroup(group: string): string {
  if (group === "project" || group === "projects") return "projects";
  if (group === "idea" || group === "ideas") return "ideas";
  if (group === "knowledge") return "knowledge";
  if (group === "people") return "people";
  if (group === "review") return "review";
  return "other";
}

export function handleGraph(cfg: ServerConfig) {
  return (_req: Request, res: Response) => {
    res.json(buildGraph(cfg.wikiRoot));
  };
}
