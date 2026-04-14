# PROJECT.md

`llm-wiki-skill` 是一个 **AI-maintained Obsidian research workbench** 的维护 harness 仓库。

## Purpose

这个 repo 负责：
- `llm-wiki` skill 与参考协议
- scaffold / harness / lint / audit_review 脚本
- 本地 web viewer
- Obsidian audit plugin
- 支撑这些能力的 repo-level docs 与治理入口

这个 repo 不负责：
- 直接充当某个 vault 的 runtime target
- 替代 `WORKBENCH.md + indexes/Home.md`
- 在 repo 内存放长期研究内容本体

人类可读总览见 [README.md](README.md)，agent-first 导航从 [AGENTS.md](AGENTS.md) 开始。

## External Runtime Target

真正被维护的是外部 Obsidian workbench。典型 runtime contract 由：
- `WORKBENCH.md`
- `raw/`
- `compiled/`
- `indexes/`
- `outputs/`
- `audit/`
- `log/`

Codex 面向具体 workbench 工作时，应先进入 vault，而不是停留在这个仓库根目录。

## Core Subsystems

- `llm-wiki/`
  - skill、references、Python harness tooling
- `audit-shared/`
  - web 与 plugin 共用的 anchored audit schema / serializer
- `web/`
  - 次级浏览界面与 audit 提交入口
- `plugins/obsidian-audit/`
  - Obsidian 内的 anchored audit surface
- `docs/`
  - repo-level system of record

## Daily Entry

推荐的 repo 维护入口：

1. [AGENTS.md](AGENTS.md)
2. [ARCHITECTURE.md](ARCHITECTURE.md)
3. [PLANS.md](PLANS.md)
4. [docs/index.md](docs/index.md)

常用 repo 级命令：

```bash
python3 llm-wiki/scripts/generate_repo_inventory.py .
python3 llm-wiki/scripts/lint_repo_workspace.py .
python3 -m py_compile llm-wiki/scripts/*.py
```

常用 runtime 级命令：

```bash
python3 llm-wiki/scripts/harness.py health <workbench-root>
python3 llm-wiki/scripts/lint_wiki.py <workbench-root>
```
