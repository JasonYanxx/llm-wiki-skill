# llm-wiki-skill

一个用于构建与维护 **AI-maintained Obsidian research workbench** 的源码仓库。

这个仓库现在的定位不是“某个具体 vault 本身”，而是：
- **项目仓库**：维护 harness 源码、脚本、web viewer、Obsidian audit plugin
- **`llm-wiki` skill**：约束 Codex 如何维护 workbench
- **Obsidian vault**：真正被维护的 runtime target

Codex 真正维护 Obsidian 的入口，始终在 vault 内：
- `WORKBENCH.md`
- `indexes/Home.md`

不是这个项目仓库根目录，也不是 Obsidian app 本身。

## v2 目标

当前版本把项目从“schema + scaffold + lint + skill 文档”升级成了一个更完整的 **maintenance harness**：
- 强制 `Current Focus`
- 固定维护状态机：`preflight -> ingest -> compile -> review -> promote -> lint -> audit -> postflight`
- 机器可读运行状态：`compiled/_meta/ops.json`
- 中文优先的 vault-facing 模板与文案
- repo-aware 桥接门槛化
- web / plugin 读取统一 health 状态

## 中文优先合同

这个项目默认支持的 vault profile 是：
- **正文、导航、review、log、prompt 模板以中文为主**
- 英文只保留在稳定命名层：
  - canonical 文件名 / slug
  - registry `id / type / path`
  - `ops.json` key
  - status enum
  - 必要的 canonical title

## 仓库内容

- `llm-wiki/`
  - `SKILL.md`：Codex 维护协议
  - `references/`：schema、harness、对象写作、audit、log、tooling、prompt 模板
  - `scripts/`
    - `scaffold.py`
    - `harness.py`
    - `lint_wiki.py`
    - `audit_review.py`
- `plugins/obsidian-audit/`
  - Obsidian 内的 anchored audit 工具
  - 保持 audit-focused，不承担 canonical maintenance
- `web/`
  - 本地 viewer
  - 浏览 `indexes/` 与 `compiled/`
  - 展示 workbench health / graph / audits
- `audit-shared/`
  - web 与插件共用的 anchored audit schema

## Runtime Contract

scaffold 出来的 workbench 采用：

```text
<workbench-root>/
├── WORKBENCH.md
├── .gitignore
├── raw/
├── compiled/
│   ├── _meta/
│   │   ├── registry.json
│   │   └── ops.json
│   └── ...
├── indexes/
├── outputs/
├── audit/
└── log/
```

其中：
- `compiled/_meta/registry.json` 是 compiled object registry
- `compiled/_meta/ops.json` 是 harness runtime state

## 安装 skill

```bash
cp -r llm-wiki/ ~/.codex/skills/llm-wiki/
```

安装后，Codex 维护任何 workbench 时都应以 `llm-wiki/SKILL.md` 为协议入口。

## Quick Start

```bash
# 1. Scaffold 一个新的 workbench
python3 llm-wiki/scripts/scaffold.py ~/my-workbench "我的研究工作台"

# 2. 填写 indexes/Home.md 里的 Current Focus

# 3. 运行 preflight，生成/刷新 ops.json
python3 llm-wiki/scripts/harness.py preflight ~/my-workbench

# 4. 让 Codex 按 SKILL.md 执行 ingest / compile / review

# 5. 跑 lint
python3 llm-wiki/scripts/lint_wiki.py ~/my-workbench

# 6. 结束后跑 postflight
python3 llm-wiki/scripts/harness.py postflight ~/my-workbench

# 7. 检查 open audits
python3 llm-wiki/scripts/audit_review.py ~/my-workbench --open
```

## Harness CLI

```bash
python3 llm-wiki/scripts/harness.py preflight <workbench-root>
python3 llm-wiki/scripts/harness.py health <workbench-root>
python3 llm-wiki/scripts/harness.py postflight <workbench-root>
```

### `preflight`

- 校验 `WORKBENCH.md` 与 `indexes/Home.md`
- 强制检查 `Current Focus` 的 4 个键
- 发现近期 raw delta / promote candidates / pending repo bridge
- 写入 `compiled/_meta/ops.json`

### `health`

- 输出统一健康状态摘要
- 供 CLI、web、plugin 消费相同状态模型

### `postflight`

- 验证本轮是否形成真实维护闭环
- 运行 lint
- 检查 log 是否更新
- 更新 `ops.json` 中的 `last_successful_loop_at`

## Web Viewer

```bash
cd audit-shared && npm install && npm run build && cd ..
cd web && npm install && npm run build
npm start -- --wiki "/path/to/your/workbench-root" --port 4175
```

它是次级界面，不是 canonical 编辑入口。主要负责：
- 浏览 `indexes/` 与 `compiled/`
- 展示 workbench health
- 浏览 compiled object graph
- 提交 anchored audit

## Obsidian Audit Plugin

```bash
cd audit-shared && npm install && npm run build && cd ..
cd plugins/obsidian-audit
npm install
npm run build
npm run link -- "/path/to/your/Obsidian vault"
```

插件只做一件事：在 Obsidian 里提交 anchored audit，并读取 workbench health 提醒你当前入口是否就绪。  
真正的维护入口仍然是 vault 内的 `WORKBENCH.md + indexes/Home.md`。

## Repo-aware Contract

- `registry.meta.repo_roots` 只接受用户确认的本地 repo 根路径
- `repo:` source refs 只链接显式执行入口：
  - `PROJECT.md`
  - `README.md`
  - `docs/index.md`
- 不做自动 repo 发现

## 兼容性

- 保留 `llm-wiki` 这个技术 ID
- 保留脚本路径
- 保留 web `--wiki` flag
- 旧 `CLAUDE.md` 与 `wiki/` 仍可作为迁移输入读取，但不再是 canonical truth
