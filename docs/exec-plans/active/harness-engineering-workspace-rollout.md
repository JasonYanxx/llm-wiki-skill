# Harness Engineering Workspace Rollout

> Active execution plan for upgrading `llm-wiki-skill` into a complete agent-first harness workspace.

## Status

- Started: 2026-04-14
- Mode: repo-local harness engineering rollout
- Status: active follow-through

## Goal

建立完整的 repo-local system-of-record、根目录短入口文档、深层 docs knowledge base，以及本地可运行的 workspace 治理脚本。

## Phases

### Phase 0. Cleanup Baseline

- [x] 清理 `.pyc` / `__pycache__`
- [x] 静默 `plugins/obsidian-audit/data.json`
- [x] 把 design memo 与旧执行清单移入 `docs/`

### Phase 1. Root Entry Surface

- [x] 建立 `AGENTS.md`
- [x] 建立 `PROJECT.md`
- [x] 建立 `ARCHITECTURE.md`
- [x] 建立 `DESIGN.md`
- [x] 建立 `FRONTEND.md`
- [x] 建立 `PLANS.md`
- [x] 建立 `QUALITY_SCORE.md`
- [x] 建立 `RELIABILITY.md`
- [x] 建立 `SECURITY.md`

### Phase 2. Deep Docs

- [x] 升级 `docs/index.md`
- [x] 建立 design docs index 与 core beliefs
- [x] 建立 active / completed / tech debt 结构
- [x] 建立 product specs
- [x] 建立 docs-side references catalog

### Phase 3. Local Governance

- [x] 生成 `docs/generated/` inventories
- [x] 新增 repo workspace lint
- [x] 跑 repo-level validation

## Follow-through

即使首轮落地完成，这个 plan 仍保留为 active，用于继续追踪：
- generated inventory 是否保持新鲜
- root entry docs 是否继续与真实结构一致
- 哪些 repo rules 还值得进一步机械化
