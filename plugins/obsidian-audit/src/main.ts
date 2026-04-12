import {
  Editor,
  MarkdownFileInfo,
  MarkdownView,
  Notice,
  Plugin,
  TFile,
  normalizePath,
} from "obsidian";
import {
  DEFAULT_SETTINGS,
  LLMWikiAuditSettingTab,
  type LLMWikiAuditSettings,
} from "./settings.js";
import { FeedbackModal } from "./feedback-modal.js";
import { writeAudit } from "./writer.js";
import { fromMarkdown } from "audit-shared";
import { formatHealthNotice, readWorkbenchHealth, type WorkbenchHealth } from "./health.js";

export default class LLMWikiAuditPlugin extends Plugin {
  settings!: LLMWikiAuditSettings;

  async onload(): Promise<void> {
    await this.loadSettings();

    this.addCommand({
      id: "audit-add-feedback",
      name: "对当前选区提出审阅意见",
      hotkeys: [{ modifiers: ["Mod"], key: "'" }],
      editorCallback: async (editor: Editor, ctx: MarkdownView | MarkdownFileInfo) => {
        if (!(ctx instanceof MarkdownView)) {
          new Notice("审阅意见只能在 markdown 编辑视图中使用");
          return;
        }
        await this.handleAddFeedback(editor, ctx);
      },
    });

    this.addCommand({
      id: "audit-list-feedback-current-file",
      name: "列出当前文件的 open audit",
      callback: async () => {
        await this.handleListFeedbackForCurrentFile();
      },
    });

    this.addCommand({
      id: "audit-open-folder",
      name: "打开 audit 文件夹",
      callback: () => {
        const path = this.resolveAuditDir();
        const folder = this.app.vault.getAbstractFileByPath(path);
        if (folder) {
          // @ts-expect-error — revealInFolder exists on the workspace API
          this.app.showInFolder?.(folder.path);
          new Notice(`Audit 文件夹：${folder.path}`);
        } else {
          new Notice(`未找到 audit 文件夹：${path}`);
        }
      },
    });

    this.addCommand({
      id: "audit-show-workbench-health",
      name: "显示 workbench 健康状态",
      callback: async () => {
        const health = await this.readWorkbenchHealth();
        new Notice(`${formatHealthNotice(health)}\n${health.summary}`, 10000);
      },
    });

    this.addSettingTab(new LLMWikiAuditSettingTab(this.app, this));
  }

  onunload(): void {}

  async loadSettings(): Promise<void> {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings(): Promise<void> {
    await this.saveData(this.settings);
  }

  async readWorkbenchHealth(): Promise<WorkbenchHealth> {
    return readWorkbenchHealth(this.app, this.settings);
  }

  private async handleAddFeedback(editor: Editor, view: MarkdownView): Promise<void> {
    const selection = editor.getSelection();
    if (!selection || !selection.trim()) {
      new Notice("请先选中文本");
      return;
    }
    const file = view.file;
    if (!file) {
      new Notice("当前没有打开文件");
      return;
    }

    const fileText = editor.getValue();
    const from = editor.getCursor("from");
    const to = editor.getCursor("to");
    const selStart = editor.posToOffset(from);
    const selEnd = editor.posToOffset(to);
    if (selEnd <= selStart) {
      new Notice("选区为空");
      return;
    }

    const preview =
      selection.length > 280 ? selection.slice(0, 280) + "…" : selection;
    const modal = new FeedbackModal(this.app, preview);
    const result = await modal.open();
    if (!result) return;

    try {
      await writeAudit(this.app, this.settings, {
        file,
        fileText,
        selStart,
        selEnd,
        severity: result.severity,
        comment: result.comment,
      });
    } catch (err) {
      console.error("[llm-wiki-audit] write failed", err);
    }
  }

  private async handleListFeedbackForCurrentFile(): Promise<void> {
    const view = this.app.workspace.getActiveViewOfType(MarkdownView);
    if (!view || !view.file) {
      new Notice("当前没有打开 markdown 文件");
      return;
    }
    const targetRel = this.fileRelToWiki(view.file.path);
    const auditDir = this.resolveAuditDir();

    const folder = this.app.vault.getAbstractFileByPath(auditDir);
    if (!folder) {
      new Notice(`未找到 audit 文件夹：${auditDir}`);
      return;
    }

    const matches: string[] = [];
    const files = this.app.vault.getMarkdownFiles().filter((f: TFile) =>
      f.path.startsWith(auditDir + "/") && !f.path.startsWith(auditDir + "/resolved/"),
    );
    for (const f of files) {
      try {
        const text = await this.app.vault.read(f);
        const entry = fromMarkdown(text);
        if (entry.target === targetRel && entry.status === "open") {
          matches.push(`[${entry.severity}] ${entry.id}`);
        }
      } catch {
        // skip malformed
      }
    }

    if (matches.length === 0) {
      new Notice(`${targetRel} 当前没有 open audit`);
    } else {
      new Notice(
        `${targetRel} 当前有 ${matches.length} 条 open audit：\n${matches.join("\n")}`,
        8000,
      );
    }
  }

  private fileRelToWiki(vaultPath: string): string {
    const root = this.settings.wikiRoot;
    if (!root || root === ".") return vaultPath;
    const normalized = root.replace(/\/+$/, "");
    if (vaultPath.startsWith(normalized + "/")) {
      return vaultPath.slice(normalized.length + 1);
    }
    return vaultPath;
  }

  private resolveAuditDir(): string {
    const root = this.settings.wikiRoot;
    const dir = this.settings.auditDir || "audit";
    if (!root || root === ".") return normalizePath(dir);
    return normalizePath(`${root.replace(/\/+$/, "")}/${dir.replace(/^\/+/, "")}`);
  }
}
