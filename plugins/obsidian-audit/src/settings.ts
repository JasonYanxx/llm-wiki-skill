import { App, PluginSettingTab, Setting } from "obsidian";
import type LLMWikiAuditPlugin from "./main.js";
import { formatHealthNotice } from "./health.js";

export interface LLMWikiAuditSettings {
  /** Path of the workbench root relative to the vault root. `.` means the vault itself is the workbench. */
  wikiRoot: string;
  /** Path of the audit directory relative to the workbench root. */
  auditDir: string;
  /** Free-form author name written into every audit file. */
  author: string;
}

export const DEFAULT_SETTINGS: LLMWikiAuditSettings = {
  wikiRoot: ".",
  auditDir: "audit",
  author: "me",
};

export class LLMWikiAuditSettingTab extends PluginSettingTab {
  plugin: LLMWikiAuditPlugin;

  constructor(app: App, plugin: LLMWikiAuditPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();
    containerEl.createEl("h2", { text: "Research Workbench Audit 设置" });

    const intro = containerEl.createDiv({ cls: "llm-wiki-audit-settings-note" });
    intro.createEl("p", {
      text: "插件只负责 anchored audit 与健康状态提醒。真正的维护入口仍然在 vault 内的 WORKBENCH.md 与 indexes/Home.md。",
    });

    const healthSection = containerEl.createDiv({ cls: "llm-wiki-audit-health" });
    healthSection.createEl("h3", { text: "工作台健康状态" });
    const healthBody = healthSection.createDiv({ text: "正在读取状态……" });
    void this.renderHealth(healthBody);

    new Setting(containerEl)
      .setName("Workbench root")
      .setDesc(
        "相对于 vault root 的路径。如果整个 vault 本身就是 workbench，则保持 `.`。",
      )
      .addText((text) =>
        text
          .setPlaceholder(".")
          .setValue(this.plugin.settings.wikiRoot)
          .onChange(async (value) => {
            this.plugin.settings.wikiRoot = value.trim() || ".";
            await this.plugin.saveSettings();
            await this.renderHealth(healthBody);
          }),
      );

    new Setting(containerEl)
      .setName("Audit directory")
      .setDesc("相对于 workbench root 的目录，插件会把 audit 文件写到这里。")
      .addText((text) =>
        text
          .setPlaceholder("audit")
          .setValue(this.plugin.settings.auditDir)
          .onChange(async (value) => {
            this.plugin.settings.auditDir = value.trim() || "audit";
            await this.plugin.saveSettings();
            await this.renderHealth(healthBody);
          }),
      );

    new Setting(containerEl)
      .setName("Author")
      .setDesc("写入每条 audit frontmatter 的 `author` 字段。")
      .addText((text) =>
        text
          .setPlaceholder("lewis")
          .setValue(this.plugin.settings.author)
          .onChange(async (value) => {
            this.plugin.settings.author = value.trim() || "me";
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("刷新健康状态")
      .setDesc("重新读取 `compiled/_meta/ops.json` 以及 Current Focus readiness。")
      .addButton((button) =>
        button.setButtonText("刷新").onClick(async () => {
          await this.renderHealth(healthBody);
        }),
      );
  }

  private async renderHealth(container: HTMLElement): Promise<void> {
    const health = await this.plugin.readWorkbenchHealth();
    container.empty();
    container.createEl("p", { text: formatHealthNotice(health) });
    container.createEl("p", { text: health.summary });
    if (health.missingInputs.length > 0) {
      const list = container.createEl("ul");
      for (const item of health.missingInputs) {
        list.createEl("li", { text: item });
      }
    }
  }
}
