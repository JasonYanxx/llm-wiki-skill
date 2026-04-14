# Web Viewer

## Purpose

`web/` 提供本地 research workbench viewer，用于浏览和轻量交互，不是 canonical 编辑入口。

## Responsibilities

- 浏览 `indexes/` 与 `compiled/`
- 展示 workbench health
- 展示对象图
- 提交 anchored audit
- 在需要时支持 auth 保护

## Non-Goals

- 取代 vault 内的主维护入口
- 发明一套与 `ops.json` 脱节的健康状态
- 自动发现 repo roots

## Primary Command

```bash
cd web && npm start -- --wiki "/path/to/workbench-root" --port 4175
```
