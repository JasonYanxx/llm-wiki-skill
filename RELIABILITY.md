# RELIABILITY.md

这个文件描述仓库级与 runtime 级的最小可靠性检查路径。

## Repo Workspace Checks

```bash
python3 llm-wiki/scripts/generate_repo_inventory.py .
python3 llm-wiki/scripts/lint_repo_workspace.py .
python3 -m py_compile llm-wiki/scripts/*.py
```

## Build Checks

```bash
cd audit-shared && npm run build
cd web && npm run build
cd plugins/obsidian-audit && npm run build
```

## Runtime Smoke Checks

对真实 workbench root 做只读验证：

```bash
python3 llm-wiki/scripts/harness.py health <workbench-root>
python3 llm-wiki/scripts/lint_wiki.py <workbench-root>
```

如果需要闭环验证，再补：

```bash
python3 llm-wiki/scripts/harness.py preflight <workbench-root>
python3 llm-wiki/scripts/harness.py postflight <workbench-root>
```

## Failure Loop

1. 先确定失败属于 repo workspace、runtime harness、viewer 还是 plugin
2. 优先修文档映射、结构约束、脚本入口，而不是增加口头说明
3. 能机械化的规则尽量推进到脚本检查
4. 修复后至少回跑对应层级的最小检查
