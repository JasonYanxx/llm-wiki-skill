# PROJECT.md

`llm-wiki-skill` 是一个 **AI-maintained Obsidian research workbench** 的维护 harness 仓库。

## Canonical Repo Entry Contract

Canonical repo-aware entry set: `PROJECT.md`, `README.md`, `docs/index.md`.

- 当前文件是首选 repo execution entry
- [README.md](README.md) 是人类可读总览
- [docs/index.md](docs/index.md) 是深层 docs catalog
- `ARCHITECTURE.md` 与 `PLANS.md` 是进入之后的次级文档，不是 primary repo-aware jump targets

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

人类可读总览见 [README.md](README.md)，进入 repo 后的本地导航图见 [AGENTS.md](AGENTS.md)。

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

如果你已经通过 canonical entry set 进入到当前文件：

- 如需更宽的人类可读总览，回看 [README.md](README.md)
- 继续进入次级文档时，按下面顺序读取：
  - [ARCHITECTURE.md](ARCHITECTURE.md)
  - [PLANS.md](PLANS.md)
  - [docs/index.md](docs/index.md)

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
