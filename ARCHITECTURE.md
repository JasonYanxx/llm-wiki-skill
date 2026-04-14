# ARCHITECTURE.md

这个仓库的关键目标是把 repo 组织成一个 agent 可导航、可验证、可维护的 harness workspace。

## Domain Map

- `llm-wiki/`
  - 维护协议、Python scripts、runtime references
- `audit-shared/`
  - shared schema / anchor / serializer library
- `web/`
  - 本地 viewer，消费 workbench health、graph、audit surface
- `plugins/obsidian-audit/`
  - Obsidian plugin，提交 anchored audit，并读取 health
- `docs/`
  - repo-level system of record
- external vault runtime
  - 被维护对象，不在本 repo 内

## Dependency Shape

- `audit-shared` 可以被 `web/` 与 `plugins/obsidian-audit/` 依赖
- `web/` 与 plugin 不直接相互依赖
- `llm-wiki/scripts/` 与 runtime vault 交互，但不依赖 `web/` 或 plugin 源码
- `llm-wiki/references/` 与 `SKILL.md` 提供 protocol context，不是运行时代码
- `docs/` 描述 repo-level 结构与治理，不替代 runtime references

## Boundary Rules

- repo 根目录入口文档是导航层，不是长文档堆积区
- `docs/` 存放深层、可链接、可持续维护的 system-of-record
- runtime protocol 优先记录在 `llm-wiki/references/`
- workbench canonical truth 优先记录在外部 vault
- repo-aware entry 只连显式入口，不做自动 repo 发现

## Key Interfaces

- runtime harness CLI
  - `scaffold.py`
  - `harness.py`
  - `lint_wiki.py`
  - `audit_review.py`
- repo workspace CLI
  - `generate_repo_inventory.py`
  - `lint_repo_workspace.py`

## Read Next

- 设计原则：[DESIGN.md](DESIGN.md)
- 前端表面：[FRONTEND.md](FRONTEND.md)
- 深层 docs：[docs/index.md](docs/index.md)
