import fs from "node:fs";
import path from "node:path";
import type { Request, Response } from "express";
import type { ServerConfig } from "../config.js";

const CURRENT_FOCUS_KEYS = [
  "Primary active project",
  "Current blocker",
  "Primary repo jump point",
  "Immediate next push",
];

export interface HealthResponse {
  hasOps: boolean;
  maintenanceMode: "blocked" | "ready";
  currentFocusOk: boolean;
  missingInputs: string[];
  openAuditCount: number;
  pendingRepoBridge: string[];
  delta: {
    rawPaths: string[];
    promoteCandidates: string[];
  };
  lastSuccessfulLoopAt: string | null;
  lastLintStatus: string;
  generatedAt: string | null;
  summary: string;
}

export function handleHealth(cfg: ServerConfig) {
  return (_req: Request, res: Response) => {
    res.json(readHealth(cfg.wikiRoot));
  };
}

function readHealth(wikiRoot: string): HealthResponse {
  const opsPath = path.join(wikiRoot, "compiled", "_meta", "ops.json");
  const homePath = path.join(wikiRoot, "indexes", "Home.md");
  const missingInputs: string[] = [];
  const homeText = fs.existsSync(homePath) ? fs.readFileSync(homePath, "utf-8") : "";
  const focus = parseCurrentFocus(homeText);
  for (const key of CURRENT_FOCUS_KEYS) {
    if (!String(focus[key] ?? "").trim()) {
      missingInputs.push(`Current Focus / ${key}`);
    }
  }

  const openAuditCount = countOpenAudits(wikiRoot);
  const fallback: HealthResponse = {
    hasOps: false,
    maintenanceMode: missingInputs.length === 0 ? "ready" : "blocked",
    currentFocusOk: missingInputs.length === 0,
    missingInputs,
    openAuditCount,
    pendingRepoBridge: [],
    delta: { rawPaths: [], promoteCandidates: [] },
    lastSuccessfulLoopAt: null,
    lastLintStatus: "unknown",
    generatedAt: null,
    summary:
      missingInputs.length === 0
        ? "尚未找到 ops.json，但 Current Focus 已填写，可以先运行 preflight。"
        : "尚未找到 ops.json，且 Current Focus 仍不完整，请先补齐再运行 preflight。",
  };

  if (!fs.existsSync(opsPath)) return fallback;

  try {
    const parsed = JSON.parse(fs.readFileSync(opsPath, "utf-8")) as Record<string, unknown>;
    const delta = isRecord(parsed.delta) ? parsed.delta : {};
    const pendingRepoBridge = Array.isArray(parsed.pending_repo_bridge)
      ? parsed.pending_repo_bridge.filter((item): item is string => typeof item === "string")
      : [];
    const rawPaths = Array.isArray(delta.raw_paths)
      ? delta.raw_paths.filter((item): item is string => typeof item === "string")
      : [];
    const promoteCandidates = Array.isArray(delta.promote_candidates)
      ? delta.promote_candidates.filter((item): item is string => typeof item === "string")
      : [];
    const maintenanceMode = parsed.maintenance_mode === "ready" ? "ready" : "blocked";
    const currentFocusOk = Boolean(parsed.current_focus_ok) && missingInputs.length === 0;
    const issues = Array.isArray(parsed.missing_inputs)
      ? parsed.missing_inputs.filter((item): item is string => typeof item === "string")
      : missingInputs;
    return {
      hasOps: true,
      maintenanceMode,
      currentFocusOk,
      missingInputs: issues.length > 0 ? issues : missingInputs,
      openAuditCount,
      pendingRepoBridge,
      delta: { rawPaths, promoteCandidates },
      lastSuccessfulLoopAt:
        typeof parsed.last_successful_loop_at === "string" ? parsed.last_successful_loop_at : null,
      lastLintStatus: typeof parsed.last_lint_status === "string" ? parsed.last_lint_status : "unknown",
      generatedAt: typeof parsed.generated_at === "string" ? parsed.generated_at : null,
      summary: buildSummary(maintenanceMode, issues.length > 0 ? issues : missingInputs, pendingRepoBridge, openAuditCount),
    };
  } catch {
    return {
      ...fallback,
      summary: "ops.json 无法解析，请重新运行 preflight。",
    };
  }
}

function parseCurrentFocus(text: string): Record<string, string> {
  const lines = text.split(/\r?\n/);
  const section: string[] = [];
  let inSection = false;
  for (const line of lines) {
    if (/^##\s+/.test(line)) {
      if (inSection) break;
      if (line.trim() === "## Current Focus") inSection = true;
      continue;
    }
    if (inSection) section.push(line);
  }

  const out: Record<string, string> = {};
  for (const line of section) {
    const match = line.match(/^\s*-\s*([^:]+):\s*(.*)\s*$/);
    if (!match) continue;
    out[match[1]!.trim()] = match[2]!.trim();
  }
  return out;
}

function countOpenAudits(wikiRoot: string): number {
  const auditDir = path.join(wikiRoot, "audit");
  if (!fs.existsSync(auditDir)) return 0;
  let count = 0;
  walk(auditDir, (full) => {
    if (!full.endsWith(".md")) return;
    const rel = path.relative(auditDir, full);
    if (rel.startsWith(`resolved${path.sep}`) || path.basename(full).startsWith(".")) return;
    count += 1;
  });
  return count;
}

function buildSummary(
  mode: "blocked" | "ready",
  missingInputs: string[],
  pendingRepoBridge: string[],
  openAuditCount: number,
): string {
  if (mode === "blocked") {
    return `当前工作台处于 blocked 状态，优先补齐 ${missingInputs.length} 项输入。`;
  }
  if (pendingRepoBridge.length > 0) {
    return `工作台已就绪，但还有 ${pendingRepoBridge.length} 个待确认 repo bridge。`;
  }
  if (openAuditCount > 0) {
    return `工作台已就绪，当前有 ${openAuditCount} 条 open audit。`;
  }
  return "工作台已就绪，可以继续执行 ingest / compile / review。";
}

function walk(dir: string, visit: (full: string) => void): void {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".")) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, visit);
    else visit(full);
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
