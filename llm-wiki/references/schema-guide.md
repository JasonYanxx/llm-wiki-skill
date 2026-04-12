# WORKBENCH.md 与 Home.md Guide

## 1. `WORKBENCH.md`

`WORKBENCH.md` 是 vault 的稳定系统协议。
它负责锁定：
- 系统边界
- 语言合同
- canonical root contract
- human-owned zones
- object protocols
- harness loop
- migration / compatibility notes

它不应该变成：
- 每日任务清单
- project dashboard
- 临时想法回收站

## 2. `indexes/Home.md`

Home 是日常维护入口。
其中最重要的是 `Current Focus`：

```markdown
## Current Focus

- Primary active project:
- Current blocker:
- Primary repo jump point:
- Immediate next push:
```

这 4 个键是强制项。
没有它们，harness 应该把工作台标记为 `blocked`。

## 3. 中文优先

- `WORKBENCH.md`、`indexes/*.md`、`Review.md`、`log/*.md` 默认中文
- 文件路径、slug、registry key、ops key、status enum 保持英文稳定命名

## 4. Root Contract

```text
WORKBENCH.md
raw/
compiled/
indexes/
outputs/
audit/
log/
```

`compiled/_meta/` 至少包含：
- `registry.json`
- `ops.json`
