# Workbench Runtime Contract

这个 spec 说明 `llm-wiki-skill` 面向外部 Obsidian workbench 的稳定 contract。

## Canonical Structure

```text
<workbench-root>/
├── WORKBENCH.md
├── raw/
├── compiled/
├── indexes/
├── outputs/
├── audit/
└── log/
```

## Canonical Entry

- `WORKBENCH.md`
- `indexes/Home.md`

## Operation Loop

- `preflight`
- `ingest`
- `compile`
- `review`
- `promote`
- `lint`
- `audit`
- `postflight`

## Repo Boundary

- 这个 repo 提供 harness、viewer、plugin、references
- 具体 vault 才是被维护对象
- `repo_roots` 必须显式确认
