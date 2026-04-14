# QUALITY_SCORE.md

这是 repo-level 的质量快照，不替代更细的测试结果。

## Grade Legend

- `A`: 结构清晰，入口稳定，验证路径明确
- `B`: 可用且可维护，但仍有明显缺口
- `C`: 边界或验证不足，继续放大会放大维护成本

## Current Snapshot

| Subsystem | Grade | Why |
| --- | --- | --- |
| `llm-wiki` skill + references | A- | protocol 边界清晰，但 repo-level docs 仍在追平 |
| Python harness scripts | B+ | CLI 入口稳定，repo workspace 治理刚补齐 |
| `audit-shared` | A- | 范围清晰、依赖面小 |
| `web/` | B | viewer 行为已成型，但缺少更系统的 repo-level治理文档历史 |
| `plugins/obsidian-audit/` | B | 角色明确，但本地配置与使用约束需持续守护 |
| repo workspace docs | B | 入口层与深层 docs 已建立，后续靠 lint 和 doc gardening 保持一致 |

## Immediate Quality Priorities

- 持续让根入口文档与 `docs/` 保持交叉引用一致
- 保持 generated inventories 新鲜
- 把 repo-level质量问题优先编码成 lint 或可重复检查
