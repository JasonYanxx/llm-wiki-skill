---
name: llm-wiki
description: >-
  Build and maintain a Chinese-first AI-native Obsidian research workbench:
  scaffold canonical vaults, run a closed-loop maintenance harness, maintain
  project/idea/knowledge/people/review objects, keep registry + ops runtime
  state healthy, file and process anchored audits, and support long-term Codex
  maintenance against a real vault target rather than the repo itself.
---

# llm-wiki v2 — 中文优先的 Obsidian Maintenance Harness

> 这是 Codex 维护 research workbench 时要遵守的协议，不是 vault 本身。

## 先区分 3 层对象

### 1. 项目仓库

项目仓库负责：
- harness 源码
- scaffold / harness / lint / audit 脚本
- web viewer
- Obsidian audit plugin

项目仓库不是被维护对象本身。

### 2. `llm-wiki` skill

skill 负责：
- 规定 Codex 的维护状态机
- 规定什么能写、什么不能写
- 规定什么时候 blocked、什么时候可以 compile / promote

skill 不是 runtime target。

### 3. Obsidian vault

vault 才是被维护的 runtime target。
Codex 真正维护 Obsidian 的入口始终是 vault 内：
- `WORKBENCH.md`
- `indexes/Home.md`

不是项目仓库根目录，也不是 Obsidian app 本身。

## 语言合同

默认 profile：
- vault 正文、导航、review、log、prompt 模板以中文为主
- 英文只保留给稳定命名层：
  - canonical 文件名 / slug
  - `registry.json` 的 `id / type / path`
  - `ops.json` key
  - status enum
  - 必要的 canonical title

不要把整个 vault 写成英文百科。

## Session Start

每次维护 session 的最小入口固定为：
1. `WORKBENCH.md`
2. `indexes/Home.md`
3. `compiled/_meta/registry.json`
4. `compiled/_meta/ops.json`（如果存在）

如果 `ops.json` 缺失，应先运行或模拟 `preflight` 逻辑，再继续。

## Canonical Runtime Contract

```text
<workbench-root>/
├── WORKBENCH.md
├── raw/
├── compiled/
│   ├── _meta/
│   │   ├── registry.json
│   │   └── ops.json
│   ├── projects/
│   ├── ideas/
│   ├── knowledge/
│   ├── people/
│   └── review/
├── indexes/
├── outputs/
├── audit/
└── log/
```

### `_meta` 职责

- `registry.json`
  - compiled 对象索引
  - graph / index / lint / repo-aware stale check 的机器可读基础
- `ops.json`
  - harness 运行状态
  - blocked / ready
  - missing inputs
  - raw delta
  - promote candidates
  - pending repo bridge
  - last successful loop

## 强闭环维护状态机

### 1. `preflight`

先检查：
- `WORKBENCH.md` 是否存在
- `indexes/Home.md` 是否存在
- `Current Focus` 的 4 个键是否都已填写
- 是否有新的 raw delta
- 是否有 open audits
- 是否有 pending repo bridge

如果 `Current Focus` 缺项，则：
- `maintenance_mode = blocked`
- 允许有限读取、query、audit
- 禁止核心 `compile / promote`

### 2. `ingest`

只把新材料规范化进 `raw/`：
- `raw/inbox/`
- `raw/daily/`
- `raw/projects/<slug>/`
- `raw/external/papers/`
- `raw/external/others/`

不要在 ingest 阶段直接创建 compiled 对象。

### 3. `compile`

把信号写入：
- `compiled/`
- `indexes/`
- `compiled/_meta/registry.json`
- `log/`

规则：
- 默认做 signal-driven partial refresh
- 不得覆盖 human-owned zones
- 只有在 `maintenance_mode = ready` 时才允许进行核心 compile

### 4. `review`

更新：
- `compiled/review/Review.md`
- `log/`

目标：
- 管理 `noticed / organized / retained / deferred`
- 把 knowledge 层变成可调用的长期骨架，而不是越积越散

### 5. `promote`

只允许稳定候选进入正式对象层。

promote 门槛：
- 来源稳定
- `related_object_ids` 明确
- Provenance 可写
- 用途清楚

如果门槛未满足：
- 候选只能留在 `outputs/queries/`
- 不要为了“看起来完整”而强行创建 `idea` 或 `project`

### 6. `lint`

`lint_wiki.py` 现在既检查结构，也检查 harness readiness：
- canonical root
- registry drift
- `ops.json`
- `Current Focus`
- 中文优先 profile
- git 噪声治理
- provenance
- disconnected compiled objects
- stale source refs
- wikilinks
- log / audit shape

### 7. `audit`

永远不要忽略 open audit files。

使用 anchor window 定位目标区域，决定：
- `accept`
- `partial`
- `reject`
- `defer`

处理完成后：
- 更新目标页面
- 把条目移入 `audit/resolved/`
- 追加 `log/`

### 8. `postflight`

在结束前确认：
- 本轮是否真的更新了 log
- lint 是否通过
- `ops.json` 是否更新了 `last_successful_loop_at`

没有形成闭环，就不要把这一轮当成成功维护。

## Human-owned Zones

- `indexes/Home.md -> Current Focus`
- project / idea 页中的 `My Notes`

这些区块默认不允许被 compile 覆盖。

## Repo-aware Contract

`repo_roots` 必须显式确认，禁止猜测。

只允许链接显式执行入口：
- `PROJECT.md`
- `README.md`
- `docs/index.md`

如果 repo 路径未确认：
- 不要伪造 `registry.meta.repo_roots`
- 把它记为 pending repo bridge

## Objects

### Project

- `compiled/projects/<project-slug>/index.md`
- status: `active | holding | done`
- 固定结构：
  1. Overview
  2. Status
  3. Execution Entry
  4. Related Objects
  5. AI Compiled
  6. My Notes
  7. Provenance

### Idea

- `compiled/ideas/<idea-slug>.md`
- status: `spark | exploring | incubating | project-ready`
- 固定结构：
  1. Proposition
  2. Status
  3. AI Judgment
  4. Related Objects
  5. My Notes
  6. Provenance

### Knowledge

- `compiled/knowledge/<English Canonical Title>.md`
- 固定结构：
  1. Current Understanding
  2. Why It Matters
  3. Related Projects and Ideas
  4. AI Compiled Body
  5. Provenance

### People

- `compiled/people/<source-facing name>.md`
- 固定结构：
  1. Current Relationship
  2. Academic Profile
  3. Related Objects
  4. Recent Interactions
  5. Next Follow-up
  6. Provenance

### Review

- `compiled/review/Review.md`
- 固定结构：
  1. Overview
  2. Noticed
  3. Organized
  4. Retained
  5. Deferred

## 推荐脚本

```bash
python3 llm-wiki/scripts/scaffold.py <workbench-root> "<title>"
python3 llm-wiki/scripts/harness.py preflight <workbench-root>
python3 llm-wiki/scripts/lint_wiki.py <workbench-root>
python3 llm-wiki/scripts/harness.py postflight <workbench-root>
python3 llm-wiki/scripts/audit_review.py <workbench-root> --open
```

## References

按需读取这些参考，而不是一次性全读：
- `references/harness-guide.md`
- `references/schema-guide.md`
- `references/article-guide.md`
- `references/audit-guide.md`
- `references/log-guide.md`
- `references/tooling-tips.md`
- `references/prompt-pack.md`

## 默认行为

- 优先使用脚本和既有模板，而不是临时发明新结构
- 优先在 vault 内完成闭环，而不是把知识碎片留在对话里
- 默认保持中文优先
- 默认保护 human-owned zones
- 默认把项目执行留在 repo，把研究记忆与控制层留在 workbench
