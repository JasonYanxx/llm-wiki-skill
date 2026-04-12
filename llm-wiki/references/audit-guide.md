# Audit Guide

`audit/` 是人类纠偏面，不是一般评论区。

## 目录

```text
audit/
├── <open>.md
└── resolved/
    └── <resolved>.md
```

## 每条 audit 至少包含

- YAML frontmatter
- `# Comment`
- `# Resolution`

前锚点字段保持与 `audit-shared/` 兼容：
- `target_lines`
- `anchor_before`
- `anchor_text`
- `anchor_after`

## 目标页

常见目标：
- `compiled/projects/...`
- `compiled/ideas/...`
- `compiled/knowledge/...`
- `compiled/people/...`
- `compiled/review/Review.md`
- `indexes/Home.md`

## 处理顺序

优先处理：
1. `error`
2. `warn`
3. `suggest`
4. `info`

## 处理流程

1. 读取 open audits
2. 用 anchor window 定位目标片段
3. 决定 `accept / partial / reject / defer`
4. 对目标页面做最小修复
5. 追加 resolution note
6. 移动到 `audit/resolved/`
7. 追加 `log/`
