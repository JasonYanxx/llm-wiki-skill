# Compiled Object Writing Guide

`compiled/` 里的对象不是中立百科，而是**服务于用户当前科研推进的长期对象**。

## 通用规则

- 固定 section 结构尽量稳定
- 让 Provenance 可读，不只写 frontmatter
- 优先用自然的 Obsidian 链接
- 保护 human-owned zones
- 页面正文默认中文；稳定命名层允许英文

## Project

```markdown
# <中英皆可的项目标题>

## Overview
## Status
## Execution Entry
## Related Objects
## AI Compiled
## My Notes
## Provenance
```

要求：
- 轻量控制页，不承担 repo 执行本体
- `Execution Entry` 只指向显式入口
- `My Notes` 由人类维护

## Idea

```markdown
# <想法标题>

## Proposition
## Status
## AI Judgment
## Related Objects
## My Notes
## Provenance
```

只有当想法具备稳定来源、明确 related objects 和清楚用途时，才适合进入正式 idea 层。

## Knowledge

```markdown
# <中文优先标题，可保留 English canonical title>

## Current Understanding
## Why It Matters
## Related Projects and Ideas
## AI Compiled Body
## Provenance
```

要求：
- 写“我当前如何理解它”
- 写“它为什么影响当前研究”
- 不写成脱离上下文的百科定义

## People

```markdown
# <姓名或人物标题>

## Current Relationship
## Academic Profile
## Related Objects
## Recent Interactions
## Next Follow-up
## Provenance
```

只维护与当前研究推进直接相关的人，不追求完整通讯录。

## Review

```markdown
# Review

## Overview
## Noticed
## Organized
## Retained
## Deferred
```

它是队列页，不是长文对象。
