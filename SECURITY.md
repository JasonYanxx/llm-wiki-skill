# SECURITY.md

这个仓库的安全重点是“边界清晰”而不是复杂权限系统。

## Trust Boundaries

- repo 不是 vault runtime target
- `repo_roots` 必须显式确认，禁止自动猜测
- repo-aware 入口只连：
  - `PROJECT.md`
  - `README.md`
  - `docs/index.md`

## Viewer

- 本地 viewer 默认是开发辅助面
- 如果绑定到非 loopback 地址，应使用 auth 保护
- 不要让 viewer 成为修改 canonical truth 的主入口

## Plugin Local State

- `plugins/obsidian-audit/data.json` 是本地状态
- 它不属于版本化配置
- 不要把本机 vault 路径或个人状态提交进仓库

## Docs Hygiene

- 不在 repo 中存放私人凭据或非必要本地路径
- design / plan / spec 应以 repo-local markdown 形式沉淀
- 运行时 secrets 与个人环境状态留在 repo 外
