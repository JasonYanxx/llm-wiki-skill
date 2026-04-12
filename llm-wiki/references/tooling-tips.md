# Tooling Tips

## Obsidian

建议把这个 workbench 当成研究控制层，而不是生活总库。

推荐约定：
- 快速捕获放 `raw/inbox/`
- 日记放 `raw/daily/`
- 项目原始材料放 `raw/projects/<slug>/`
- 外部材料放 `raw/external/...`

## Web Viewer

web 是次级界面，主要负责：
- 浏览 `indexes/`
- 浏览 `compiled/`
- 看 `ops.json` 对应的 health 状态
- 看 graph
- 提交 anchored audit

它不是主编辑环境。

## Obsidian Audit Plugin

插件只做 2 件事：
- 在 Obsidian 内提交 anchored audit
- 提示当前 workbench health

它不是 compile / review / promote 的总控台。

## Repo-aware 使用建议

- 只连显式执行入口：`PROJECT.md`、`README.md`、`docs/index.md`
- `repo_roots` 只接受用户确认
- 不要把 Obsidian 当 repo 的执行体

## Git 噪声

scaffold 出来的 `.gitignore` 至少应忽略：
- `.obsidian/graph.json`
- `.obsidian/workspace.json`
- `.obsidian/workspace-mobile.json`
- `.obsidian/plugins/`
