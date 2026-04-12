# Prompt Pack

下面这些模板默认面向中文工作流。

## 1. Session Bootstrap

```text
以 <workbench-root> 为 canonical research workbench。
先阅读：
1. WORKBENCH.md
2. indexes/Home.md
3. compiled/_meta/registry.json
4. compiled/_meta/ops.json（如果存在）

先判断当前是否 blocked。
如果 blocked，只汇报缺失输入与允许的有限操作；
如果 ready，再提出本轮最合理的维护顺序。
```

## 2. Daily Maintenance

```text
以 <workbench-root> 为 canonical workbench。
严格按闭环执行：
1. 检查 Current Focus
2. 读取近期 raw delta
3. 做一轮 ingest -> compile
4. 更新 indexes 与 registry
5. 追加 log
6. 跑 lint

不要覆盖 Home 的 Current Focus，也不要覆盖任何 My Notes。
```

## 3. Weekly Review

```text
以 <workbench-root> 为基础做 weekly review。
1. 阅读 knowledge pages、registry、Review
2. 更新 compiled/review/Review.md
3. 重新分配 noticed / organized / retained / deferred
4. 明确下一轮最值得推进的对象
5. 追加 log
6. 跑 lint
```

## 4. Promote Candidate Review

```text
请只做 promote candidate review，不要直接 promote。
1. 检查 outputs/queries/ 中的候选
2. 判断它们是否满足 promote 门槛：
   - 来源稳定
   - related objects 明确
   - provenance 可写
   - 用途清楚
3. 输出推荐、反对或暂缓理由
```

## 5. Audit Cleanup

```text
请处理 open audits。
1. 阅读 audit/ 下的 open files
2. 根据 anchor window 找到目标页位置
3. 做最小修复
4. 写 resolution note
5. 移到 audit/resolved/
6. 追加 log
```
