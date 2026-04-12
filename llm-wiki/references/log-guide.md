# Log Guide

`log/` 是运维日志，不是日记。

## 文件形态

- 路径：`log/YYYYMMDD.md`
- H1：`# YYYY-MM-DD`
- 每条操作：

```markdown
## [HH:MM] <op> | <一句话说明>
- ...
```

## 推荐记录内容

- 本轮做了什么
- 更新了哪些 canonical 文件
- 哪些对象被新增 / 刷新 / 延后
- 审阅是如何处理的

## 不要写什么

- 大段正文复制
- 私人流水账
- 替代 `raw/daily/` 的日记内容

## 建议操作标签

- `scaffold`
- `preflight`
- `ingest`
- `compile`
- `review`
- `promote`
- `lint`
- `audit`
- `postflight`
