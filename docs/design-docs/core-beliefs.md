# Core Beliefs

这些信念用于约束 `llm-wiki-skill` 这个项目如何作为 harness workspace 演进。

## Humans Steer, Agents Execute

- 人类负责边界、优先级、验收标准
- agent 负责实现、整理、验证、回写
- 当 agent 表现不稳定时，优先补环境与约束，而不是要求“更努力”

## Repo-Local Knowledge Is A System Of Record

- 长期有效的上下文要进入 repo
- 入口要短，深层内容要可发现
- 文档应该能被另一个 agent 独立消费

## Clear Boundary Beats Clever Coupling

- harness repo 与 runtime vault 必须分开
- viewer / plugin 是次级界面
- repo-aware 跳转必须显式，不做自动猜测

## Mechanical Checks Scale Better Than Long Manuals

- 能被脚本验证的结构，不靠口头约定维护
- generated inventories 和 workspace lint 用来降低文档漂移
- 质量改进优先沉淀成脚本、规则或稳定入口

## Chinese-First Vault, English-Stable Naming

- vault-facing 内容优先中文
- 稳定命名层保持英文
- repo docs 也尽量中文优先，但保留稳定文件名与接口名
