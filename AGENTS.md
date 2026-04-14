# AGENTS.md

这个仓库已经按 agent-first workspace 组织。这个文件是你已经进入 repo 之后的本地导航图，不是对外的 primary jump target。

## Canonical Repo Entry Contract

- Canonical repo-aware entry set: `PROJECT.md`, `README.md`, `docs/index.md`.
- 首选 agent execution entry 是 [PROJECT.md](PROJECT.md)
- [README.md](README.md) 提供人类可读总览
- [docs/index.md](docs/index.md) 提供深层 docs catalog
- `ARCHITECTURE.md` 与 `PLANS.md` 是进入之后的次级文档，不是 primary repo-aware jump targets

## Preferred Agent Path

1. [PROJECT.md](PROJECT.md)
2. [README.md](README.md)
3. [ARCHITECTURE.md](ARCHITECTURE.md)
4. [PLANS.md](PLANS.md)
5. [docs/index.md](docs/index.md)

## Core Boundary

- 这个 repo 维护 harness 源码、viewer、plugin、skill 文档
- 被维护对象仍然是外部 Obsidian workbench
- 不要把这个 repo 当成 vault runtime target
- repo-aware 跳转入口只使用 canonical entry set：
  - `PROJECT.md`
  - `README.md`
  - `docs/index.md`

## Do

- 保持根目录入口文档精简，深层内容下沉到 `docs/`
- 保持 `llm-wiki/references/` 作为 runtime protocol 参考库
- 对 repo workspace 变更运行：
  - `python3 llm-wiki/scripts/generate_repo_inventory.py .`
  - `python3 llm-wiki/scripts/lint_repo_workspace.py .`
- 对 Python 工具变更运行：
  - `python3 -m py_compile llm-wiki/scripts/*.py`

## Don’t

- 不要把 design memo 或 task board 直接丢回 repo 根目录
- 不要把 `plugins/obsidian-audit/data.json` 当成版本化配置
- 不要把 viewer 或 plugin 写成 canonical maintenance entry
- 不要破坏现有 workbench runtime contract、脚本路径或 `web --wiki`

## Deep Links

- 项目目的与日常入口：[PROJECT.md](PROJECT.md)
- 架构边界：[ARCHITECTURE.md](ARCHITECTURE.md)
- 设计原则：[DESIGN.md](DESIGN.md)
- 前端表面：[FRONTEND.md](FRONTEND.md)
- 计划与技术债：[PLANS.md](PLANS.md)
- 质量基线：[QUALITY_SCORE.md](QUALITY_SCORE.md)
- 可靠性检查：[RELIABILITY.md](RELIABILITY.md)
- 安全边界：[SECURITY.md](SECURITY.md)
