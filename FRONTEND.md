# FRONTEND.md

这个 repo 的前端表面只有两类：本地 web viewer 与 Obsidian audit plugin。

## Web Viewer

- 位置：`web/`
- 角色：次级浏览界面
- 负责：
  - 浏览 `indexes/` 与 `compiled/`
  - 展示 workbench health
  - 展示对象图
  - 提交 anchored audit
- 不负责：
  - 取代 vault 内的 canonical maintenance entry
  - 发明独立于 `ops.json` 之外的健康状态模型

## Obsidian Audit Plugin

- 位置：`plugins/obsidian-audit/`
- 角色：Obsidian 内的 feedback surface
- 负责：
  - 在 Obsidian 中提交 anchored audit
  - 读取 workbench health 提醒当前入口状态
- 不负责：
  - compile / review / promote 总控
  - 替代 `WORKBENCH.md + indexes/Home.md`

## Shared UI Rules

- 文案与定位保持“Research Workbench”语义
- runtime health 读取统一来源
- 安全边界保持显式：
  - 非 loopback 场景优先开启 viewer auth
  - plugin 本地状态不进 git

## Read Next

- 架构边界：[ARCHITECTURE.md](ARCHITECTURE.md)
- 可靠性检查：[RELIABILITY.md](RELIABILITY.md)
- 安全约束：[SECURITY.md](SECURITY.md)
- web 规格：[docs/product-specs/web-viewer.md](docs/product-specs/web-viewer.md)
- plugin 规格：[docs/product-specs/obsidian-audit-plugin.md](docs/product-specs/obsidian-audit-plugin.md)
