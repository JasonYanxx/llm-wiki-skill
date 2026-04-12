#!/usr/bin/env python3
"""
scaffold.py — Bootstrap a new Chinese-first Research Workbench directory structure.

Usage:
    python3 scaffold.py <workbench-root> "<Workbench Title>"

Example:
    python3 scaffold.py ~/workbenches/yan-vault "严言研究工作台"

Creates:
    <workbench-root>/
    ├── WORKBENCH.md
    ├── .gitignore
    ├── raw/
    │   ├── inbox/
    │   ├── daily/
    │   ├── projects/
    │   └── external/
    │       ├── papers/
    │       └── others/
    ├── compiled/
    │   ├── _meta/
    │   │   ├── registry.json
    │   │   └── ops.json
    │   ├── projects/
    │   ├── ideas/
    │   ├── knowledge/
    │   ├── people/
    │   └── review/
    │       └── Review.md
    ├── indexes/
    │   ├── Home.md
    │   ├── Projects.md
    │   ├── Ideas.md
    │   ├── Knowledge.md
    │   ├── People.md
    │   └── Review.md
    ├── outputs/
    │   └── queries/
    ├── audit/
    │   └── resolved/
    └── log/
        └── YYYYMMDD.md
"""

from __future__ import annotations

import json
import os
import shlex
import sys
from datetime import date, datetime
from pathlib import Path

FOCUS_KEYS = [
    "Primary active project",
    "Current blocker",
    "Primary repo jump point",
    "Immediate next push",
]


def scaffold(root: str, title: str) -> None:
    today = date.today()
    today_iso = today.isoformat()
    today_compact = today.strftime("%Y%m%d")
    now = datetime.now()
    now_iso = now.isoformat()
    now_hm = now.strftime("%H:%M")
    workbench_name = title.strip() or "研究工作台"
    helper_dir = Path(__file__).resolve().parent

    dirs = [
        "raw/inbox",
        "raw/daily",
        "raw/projects",
        "raw/external/papers",
        "raw/external/others",
        "compiled/_meta",
        "compiled/projects",
        "compiled/ideas",
        "compiled/knowledge",
        "compiled/people",
        "compiled/review",
        "indexes",
        "outputs/queries",
        "log",
        "audit",
        "audit/resolved",
    ]

    for rel in dirs:
        os.makedirs(os.path.join(root, rel), exist_ok=True)
    print(f"✓ 已创建目录骨架: {root}/")

    gitkeep_dirs = [
        "raw/inbox",
        "raw/daily",
        "raw/projects",
        "raw/external/papers",
        "raw/external/others",
        "compiled/projects",
        "compiled/ideas",
        "compiled/knowledge",
        "compiled/people",
        "outputs/queries",
        "audit",
        "audit/resolved",
    ]
    for rel in gitkeep_dirs:
        _write(root, os.path.join(rel, ".gitkeep"), "")

    _write(root, ".gitignore", render_gitignore())
    _write(root, "WORKBENCH.md", render_workbench_md(workbench_name))
    print("✓ 已创建 WORKBENCH.md 与 .gitignore")

    _write(root, "indexes/Home.md", render_home_md(workbench_name))
    _write(root, "indexes/Projects.md", render_projects_index_md())
    _write(root, "indexes/Ideas.md", render_ideas_index_md())
    _write(root, "indexes/Knowledge.md", render_knowledge_index_md())
    _write(root, "indexes/People.md", render_people_index_md())
    _write(root, "indexes/Review.md", render_review_index_md())
    print("✓ 已创建 indexes/*.md")

    _write(root, "compiled/review/Review.md", render_review_md())
    print("✓ 已创建 compiled/review/Review.md")

    registry = {
        "meta": {
            "schema_version": "2.0",
            "generated_at": f"{today_iso}T00:00:00",
            "workbench_title": workbench_name,
            "canonical_schema": "WORKBENCH.md",
            "runtime_state": "compiled/_meta/ops.json",
            "repo_roots": {},
            "language_profile": "zh-CN primary; English reserved for stable machine-readable identifiers",
            "notes": "Registry is the machine-readable source for compiled objects, generated indexes, and repo-aware stale checks.",
        },
        "objects": [
            {
                "id": "review:global",
                "type": "review",
                "path": "compiled/review/Review.md",
                "title": "Review 总览",
                "status": "active",
                "summary": "全局知识消化队列，用于整理 noticed、organized、retained、deferred。",
                "updated_at": today_iso,
                "source_count": 0,
                "audit_open_count": 0,
                "source_refs": [],
                "related_object_ids": [],
                "stage": "noticed",
                "next_action": "完成 preflight，补齐 Current Focus，然后开始第一次 ingest / compile / review。",
            }
        ],
    }
    _write(root, "compiled/_meta/registry.json", json.dumps(registry, indent=2, ensure_ascii=False) + "\n")

    ops = {
        "generated_at": now_iso,
        "current_focus_ok": False,
        "missing_inputs": [f"Current Focus / {key}" for key in FOCUS_KEYS],
        "maintenance_mode": "blocked",
        "delta": {
            "raw_paths": [],
            "promote_candidates": [],
        },
        "open_audit_count": 0,
        "pending_repo_bridge": [],
        "last_successful_loop_at": None,
        "last_lint_status": "unknown",
    }
    _write(root, "compiled/_meta/ops.json", json.dumps(ops, indent=2, ensure_ascii=False) + "\n")
    print("✓ 已创建 compiled/_meta/registry.json 与 compiled/_meta/ops.json")

    log_md = f"""# {today_iso}

## [{now_hm}] scaffold | 初始化 {workbench_name}
- 创建了 canonical workbench 目录：`raw/`、`compiled/`、`indexes/`、`outputs/`、`audit/`、`log/`
- 创建了 `WORKBENCH.md`、索引页、全局 Review 页面以及 `_meta/registry.json`
- 创建了 `compiled/_meta/ops.json`，当前状态为 `blocked`
- 下一步先填写 `indexes/Home.md` 中的 `Current Focus`，再运行 `harness.py preflight`
"""
    _write(root, f"log/{today_compact}.md", log_md)
    print(f"✓ 已创建 log/{today_compact}.md")

    preflight_cmd = render_helper_command(helper_dir / "harness.py", "preflight", root)
    health_cmd = render_helper_command(helper_dir / "harness.py", "health", root)
    lint_cmd = render_helper_command(helper_dir / "lint_wiki.py", root)
    audit_cmd = render_helper_command(helper_dir / "audit_review.py", root, "--open")

    print(
        f"""
✅ 已完成中文优先的 Research Workbench scaffold: {root}/

建议下一步:
  1. 先填写 `indexes/Home.md` 中的 `Current Focus`
  2. 检查 `WORKBENCH.md` 是否需要改成你的真实研究协议
  3. 将新材料放入 `raw/inbox/` 或 `raw/external/`
  4. 运行 preflight: {preflight_cmd}
  5. 查看 health:    {health_cmd}
  6. 运行 lint:      {lint_cmd}
  7. 处理审阅:       {audit_cmd}
"""
    )


def render_gitignore() -> str:
    return """# macOS
.DS_Store

# Obsidian runtime noise
.obsidian/graph.json
.obsidian/workspace.json
.obsidian/workspace-mobile.json

# Local plugin build noise
.obsidian/plugins/
"""


def render_workbench_md(title: str) -> str:
    return f"""# {title}

> 这是当前 research workbench 的稳定协议文件。
> Codex 每次维护时，真实入口始终是 `WORKBENCH.md` 与 `indexes/Home.md`。

## 1. 系统边界与目标

- **项目仓库** 负责 harness 源码、脚本、web viewer 与 Obsidian audit plugin。
- **`llm-wiki` skill** 负责 Codex 的维护协议与操作顺序。
- **当前 vault** 才是被维护的 runtime target。
- Codex 维护 Obsidian 的时候，入口不是项目仓库根目录，也不是 Obsidian app 本身，而是这个 vault 里的 `WORKBENCH.md + indexes/Home.md`。

这个工作台的目标是：
- 用低摩擦的方式把新信号先接进 `raw/`
- 让 Codex 持续维护 `compiled/`、`indexes/`、`registry` 与 `ops`
- 通过 `review`、`audit`、`log` 把长期科研支持做成稳定闭环

这个工作台不负责：
- 把 Obsidian 变成代码仓库的执行主体
- 把旧 Vault 原样镜像过来
- 自动把每一条捕获都提升成正式对象

## 2. 语言合同

- vault 正文、导航说明、review 文案、log 文案默认使用中文。
- 英文保留给稳定命名层：
  - canonical 文件名与 slug
  - `registry.json` 中的 `id / type / path`
  - `ops.json` key
  - status 枚举
  - 必要的 canonical title
- 页面标题可以中英混合，但默认优先中文表达。

## 3. Canonical Root Contract

- 根文件与根目录：
  - `WORKBENCH.md`
  - `raw/`
  - `compiled/`
  - `indexes/`
  - `outputs/`
  - `audit/`
  - `log/`
- `compiled/_meta/registry.json` 是 compiled 层的机器可读索引。
- `compiled/_meta/ops.json` 是 harness 运行状态层。
- `raw/` 是证据与输入，不是主浏览层。
- `outputs/` 放查询结果、候选提案和其他非 canonical 产物。

## 4. Human-owned Zones

- `indexes/Home.md` 中的 `Current Focus` 由人类维护。
- project / idea 页面中的 `My Notes` 由人类维护。
- Codex 在 `compile` 时不得覆盖这些区块。

## 5. Object Protocols

### Project

- 路径：`compiled/projects/<project-slug>/index.md`
- 状态：`active | holding | done`
- 固定结构：
  1. Overview
  2. Status
  3. Execution Entry
  4. Related Objects
  5. AI Compiled
  6. My Notes
  7. Provenance

### Idea

- 路径：`compiled/ideas/<idea-slug>.md`
- 状态：`spark | exploring | incubating | project-ready`
- 固定结构：
  1. Proposition
  2. Status
  3. AI Judgment
  4. Related Objects
  5. My Notes
  6. Provenance

### Knowledge

- 路径：`compiled/knowledge/<English Canonical Title>.md`
- 固定结构：
  1. Current Understanding
  2. Why It Matters
  3. Related Projects and Ideas
  4. AI Compiled Body
  5. Provenance

### People

- 路径：`compiled/people/<source-facing name>.md`
- 固定结构：
  1. Current Relationship
  2. Academic Profile
  3. Related Objects
  4. Recent Interactions
  5. Next Follow-up
  6. Provenance

### Review

- 路径：`compiled/review/Review.md`
- 固定结构：
  1. Overview
  2. Noticed
  3. Organized
  4. Retained
  5. Deferred

## 6. Harness Loop

维护状态机固定为：
1. `preflight`
2. `ingest`
3. `compile`
4. `review`
5. `promote`
6. `lint`
7. `audit`
8. `postflight`

阻断规则：
- 如果 `indexes/Home.md -> Current Focus` 缺关键输入，则 `maintenance_mode = blocked`
  - 允许有限读取、query、audit
  - 禁止核心 `compile / promote`
- 如果 repo 路径未被用户确认，则禁止猜测 `registry.meta.repo_roots`
- 如果候选还没有稳定来源、明确 related objects 和可写 provenance，则禁止 promote，只能先留在 `outputs/queries/`

## 7. Repo-aware Contract

- `registry.meta.repo_roots` 只接受用户确认过的本地路径。
- `repo:` source refs 仅连接显式执行入口：
  - `PROJECT.md`
  - `README.md`
  - `docs/index.md`
- 不做深度 repo 扫描，也不自动推断 repo 根路径。

## 8. Migration and Compatibility Notes

- `WORKBENCH.md` 取代旧 `CLAUDE.md` 的协议角色。
- `compiled/` 取代旧 `wiki/` 的 canonical compiled 层。
- `indexes/` 取代旧的单一入口页。
- 旧 `CLAUDE.md` 与 `wiki/` 仍可作为迁移输入读取，但不再是 canonical truth。
"""


def render_home_md(title: str) -> str:
    return f"""# Home

> 这是 {title} 的默认落地页。
> `Current Focus` 是人类输入锚点，其余区块由 Codex 按 registry 与 compiled 层维护。

## Current Focus

<!-- Human-owned: compile must not rewrite this section. -->
- Primary active project:
- Current blocker:
- Primary repo jump point:
- Immediate next push:

## Projects

- 入口：[[indexes/Projects|Projects 索引]]
- 当前暂无已推广项目时，由 Codex 在 compile 后补齐

## Ideas

- 入口：[[indexes/Ideas|Ideas 索引]]
- 尚未成熟的候选先进入 `outputs/queries/`

## Review

- 入口：[[compiled/review/Review|全局 Review 队列]]
- 目标：把 noticed / organized / retained / deferred 管理成稳定节奏

## People

- 入口：[[indexes/People|People 索引]]
- 只维护与你当前研究推进直接相关的人

## Recent Changes

- 工作台已初始化
- `compiled/_meta/registry.json` 与 `compiled/_meta/ops.json` 已创建
- 下一步请先填写 `Current Focus`，再运行 `harness.py preflight`
"""


def render_projects_index_md() -> str:
    return """# Projects

> 这是 project 对象的导航页。按状态组织，而不是按文件夹原样罗列。

## Active

*(暂时为空)*

## Holding

*(暂时为空)*

## Done

*(暂时为空)*
"""


def render_ideas_index_md() -> str:
    return """# Ideas

> 这是 idea 对象的导航页。只有通过 promote 门槛的候选才进入这里。

## Spark

*(暂时为空)*

## Exploring

*(暂时为空)*

## Incubating

*(暂时为空)*

## Project-ready

*(暂时为空)*
"""


def render_knowledge_index_md() -> str:
    return """# Knowledge

> 这是 knowledge 对象的导航页。默认按研究主题逐步聚合。

## Core Domains

*(暂时为空)*

## Emerging Domains

*(暂时为空)*
"""


def render_people_index_md() -> str:
    return """# People

> 这是 people 对象的导航页。只保留对当前研究推进有用的人物上下文。

## Core Collaborators

*(暂时为空)*

## Active Contacts

*(暂时为空)*

## Watchlist

*(暂时为空)*
"""


def render_review_index_md() -> str:
    return """# Review

> 这是全局知识消化队列的控制页，而不是长文页面。

## Main Queue

- [[compiled/review/Review|打开全局 Review 队列]]

## Notes

- `noticed`：刚进入系统，还没结构化
- `organized`：已经连起来，但还不稳定
- `retained`：可复用、可调用
- `deferred`：刻意延后处理
"""


def render_review_md() -> str:
    today = date.today().isoformat()
    return f"""---
title: Review 总览
type: review
status: active
updated: {today}
source_refs: []
related_object_ids: []
stage: noticed
next_action: 完成 preflight 后，根据最新 raw delta 更新本页。
---

# Review

## Overview

这里是全局知识消化队列。
每次 review 至少要回答这 4 个问题：
- 最近有什么新知识进入了系统
- 哪些对象已经结构化但还不稳定
- 哪些知识已经进入 retained，可直接支持研究推进
- 哪些主题应该先 defer，避免稀释当前 focus

## Noticed

*(暂时为空)*

## Organized

*(暂时为空)*

## Retained

*(暂时为空)*

## Deferred

*(暂时为空)*
"""


def _write(root: str, rel_path: str, content: str) -> None:
    full_path = os.path.join(root, rel_path)
    os.makedirs(os.path.dirname(full_path) or ".", exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as handle:
        handle.write(content)


def render_helper_command(script_path: Path, *args: str) -> str:
    parts = [shlex.quote(sys.executable), shlex.quote(str(script_path))]
    parts.extend(shlex.quote(arg) for arg in args)
    return " ".join(parts)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    scaffold(sys.argv[1], sys.argv[2])
