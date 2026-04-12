# Harness Guide

这份指南回答一个核心问题：**Codex 到底是在维护什么？**

## 三层边界

### 项目仓库

项目仓库负责：
- harness 源码
- 脚本
- web viewer
- Obsidian audit plugin

它不是 runtime target。

### `llm-wiki` skill

skill 负责约束 Codex 的维护流程与边界。

它不是 vault。

### Obsidian vault

vault 才是被维护对象。
Codex 维护时的真正入口始终是：
- `WORKBENCH.md`
- `indexes/Home.md`

## 标准闭环

1. `preflight`
2. `ingest`
3. `compile`
4. `review`
5. `promote`
6. `lint`
7. `audit`
8. `postflight`

## `ops.json` 的角色

`compiled/_meta/ops.json` 不是知识对象，它是 runtime state：
- `generated_at`
- `current_focus_ok`
- `missing_inputs`
- `maintenance_mode`
- `delta.raw_paths`
- `delta.promote_candidates`
- `open_audit_count`
- `pending_repo_bridge`
- `last_successful_loop_at`
- `last_lint_status`

web 和 plugin 应读取它来展示状态，而不是各自发明另一套逻辑。

## blocked 的含义

如果 `indexes/Home.md -> Current Focus` 缺关键输入：
- 允许有限读取、query、audit
- 不允许核心 `compile / promote`

这不是为了惩罚用户，而是为了避免 agent 在没有真实研究锚点时胡乱维护。

## 中文优先合同

- vault 页面正文与导航默认中文
- 英文只保留给稳定命名层
- 不要把 scaffold 出来的页面写成全英文说明书
