# Obsidian Audit Plugin

## Purpose

`plugins/obsidian-audit/` 提供 Obsidian 内的 anchored audit 提交入口。

## Responsibilities

- 根据选中文本创建 anchored audit
- 写入 audit 文件
- 读取当前 workbench health 并提醒入口状态

## Non-Goals

- 不承担 compile / promote / review 总控
- 不把 Obsidian 本地插件状态变成 repo canonical config

## Local State

- `data.json` 属于本机状态
- 它应被 git 忽略

## Primary Command

```bash
cd plugins/obsidian-audit && npm run build
```
