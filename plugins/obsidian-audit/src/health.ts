import { App, TFile, normalizePath } from "obsidian";
import type { LLMWikiAuditSettings } from "./settings.js";

const CURRENT_FOCUS_KEYS = [
  "Primary active project",
  "Current blocker",
  "Primary repo jump point",
  "Immediate next push",
];

export interface WorkbenchHealth {
  hasOps: boolean;
  maintenanceMode: "blocked" | "ready";
  currentFocusOk: boolean;
  missingInputs: string[];
  pendingRepoBridge: string[];
  openAuditCount: number;
  lastLintStatus: string;
  lastSuccessfulLoopAt: string | null;
  summary: string;
}

export async function readWorkbenchHealth(
  app: App,
  settings: LLMWikiAuditSettings,
): Promise<WorkbenchHealth> {
  const workbenchRoot = normalizeWorkbenchRoot(settings.wikiRoot);
  const opsPath = joinRel(workbenchRoot, "compiled/_meta/ops.json");
  const homePath = joinRel(workbenchRoot, "indexes/Home.md");
  const workbenchPath = joinRel(workbenchRoot, "WORKBENCH.md");
  const openAuditCount = countOpenAudits(app, settings);

  const missingInputs: string[] = [];
  if (!app.vault.getAbstractFileByPath(workbenchPath)) {
    missingInputs.push("WORKBENCH.md missing");
  }

  const homeFile = app.vault.getAbstractFileByPath(homePath);
  let currentFocusOk = false;
  if (!(homeFile instanceof TFile)) {
    missingInputs.push("indexes/Home.md missing");
  } else {
    const homeText = await app.vault.read(homeFile);
    const focus = parseCurrentFocus(homeText);
    const missingFocus = CURRENT_FOCUS_KEYS.filter((key) => !String(focus[key] ?? "").trim());
    if (missingFocus.length > 0) {
      missingInputs.push(...missingFocus.map((key) => `Current Focus / ${key}`));
    } else {
      currentFocusOk = true;
    }
  }

  const opsFile = app.vault.getAbstractFileByPath(opsPath);
  if (!(opsFile instanceof TFile)) {
    return {
      hasOps: false,
      maintenanceMode: currentFocusOk ? "ready" : "blocked",
      currentFocusOk,
      missingInputs,
      pendingRepoBridge: [],
      openAuditCount,
      lastLintStatus: "unknown",
      lastSuccessfulLoopAt: null,
      summary: currentFocusOk
        ? "尚未生成 ops.json，但 Current Focus 已填写，可以先运行 preflight。"
        : "当前工作台尚未就绪：请先补齐 Current Focus，再运行 preflight。",
    };
  }

  try {
    const parsed = JSON.parse(await app.vault.read(opsFile)) as Record<string, unknown>;
    const missingFromOps = Array.isArray(parsed.missing_inputs)
      ? parsed.missing_inputs.filter((item): item is string => typeof item === "string")
      : missingInputs;
    const pendingRepoBridge = Array.isArray(parsed.pending_repo_bridge)
      ? parsed.pending_repo_bridge.filter((item): item is string => typeof item === "string")
      : [];
    const maintenanceMode = parsed.maintenance_mode === "ready" && currentFocusOk ? "ready" : "blocked";
    return {
      hasOps: true,
      maintenanceMode,
      currentFocusOk,
      missingInputs: missingFromOps,
      pendingRepoBridge,
      openAuditCount,
      lastLintStatus: typeof parsed.last_lint_status === "string" ? parsed.last_lint_status : "unknown",
      lastSuccessfulLoopAt:
        typeof parsed.last_successful_loop_at === "string" ? parsed.last_successful_loop_at : null,
      summary: buildSummary(maintenanceMode, missingFromOps, pendingRepoBridge, openAuditCount),
    };
  } catch {
    return {
      hasOps: false,
      maintenanceMode: "blocked",
      currentFocusOk,
      missingInputs: [...missingInputs, "ops.json parse failed"],
      pendingRepoBridge: [],
      openAuditCount,
      lastLintStatus: "unknown",
      lastSuccessfulLoopAt: null,
      summary: "ops.json 无法解析，请重新运行 preflight。",
    };
  }
}

export function formatHealthNotice(health: WorkbenchHealth): string {
  const missing = health.missingInputs.length > 0
    ? `缺失输入 ${health.missingInputs.length} 项`
    : "无缺失输入";
  const repoBridge = health.pendingRepoBridge.length > 0
    ? `待确认 repo bridge ${health.pendingRepoBridge.length} 个`
    : "无待确认 repo bridge";
  const audits = `open audit ${health.openAuditCount} 条`;
  return `${health.maintenanceMode.toUpperCase()} · ${missing} · ${repoBridge} · ${audits}`;
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

function countOpenAudits(app: App, settings: LLMWikiAuditSettings): number {
  const auditDir = resolveAuditDir(settings);
  return app.vault.getMarkdownFiles().filter((file) =>
    file.path.startsWith(`${auditDir}/`) && !file.path.startsWith(`${auditDir}/resolved/`)
  ).length;
}

function resolveAuditDir(settings: LLMWikiAuditSettings): string {
  return normalizePath(joinRel(normalizeWorkbenchRoot(settings.wikiRoot), settings.auditDir || "audit"));
}

function normalizeWorkbenchRoot(root: string): string {
  if (!root || root === ".") return "";
  return root.replace(/\/+$/, "");
}

function joinRel(...parts: string[]): string {
  return normalizePath(
    parts
      .filter((part) => part && part !== ".")
      .map((part) => part.replace(/^\/+|\/+$/g, ""))
      .filter((part) => part.length > 0)
      .join("/"),
  );
}

function buildSummary(
  mode: "blocked" | "ready",
  missingInputs: string[],
  pendingRepoBridge: string[],
  openAuditCount: number,
): string {
  if (mode === "blocked") {
    return `当前工作台处于 blocked 状态，请先补齐 ${missingInputs.length} 项输入。`;
  }
  if (pendingRepoBridge.length > 0) {
    return `工作台已就绪，但还有 ${pendingRepoBridge.length} 个待确认 repo bridge。`;
  }
  if (openAuditCount > 0) {
    return `工作台已就绪，当前有 ${openAuditCount} 条 open audit。`;
  }
  return "工作台已就绪，可以继续维护。";
}
