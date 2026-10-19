# M4 统一实现接口与行为契约

## 1. 接口冻结范围

M4只新增**注册与比较**，不修改 M3 的 `DataflowAnalysis` / `DataflowFact` / `WorklistSolver().solve(analysis, *, observer=None)` 现有方法签名与求解语义。

`DataflowAnalysis` 必须实现：`name`、`direction`、`new_initial_fact()`、`new_boundary_fact()`、`meet(facts)` 和 `transfer_node(node, input_fact)`。输入为 `program` + `cfg`；`transfer_node` 只能返回新的分析事实，不要就地修改共享对象。

- 前向：`IN[n] = meet(OUT[pred])`，`OUT[n] = transfer_node(n, IN[n])`。
- 后向：`OUT[n] = meet(IN[succ])`，`IN[n] = transfer_node(n, OUT[n])`。
- `meet` 是 v0.3 沿用的方法名，泛指路径合并；不同格上的运算未必对应数学格论的 meet。
- `new_initial_fact()` 定义迭代初始化，`new_boundary_fact()` 定义入口（前向）或出口（后向）的边界事实。迭代收敛依赖分析事实的偏序、单调性和有限高度等条件；未来无限高度抽象域需要进一步设计 widening。
- 目前 v0.3 兼容策略：CFG中所有节点都参与求解，包括从入口不可达的节点；这些节点可能导致保守结果，不应理解为真实可行执行轨迹。

## 2. 显式注册 + 延迟加载

- 参考注册位于 `analyzer/registry.py` 的 `REFERENCE_ANALYSES`；教师负责维护。
- 学生注册位于 `labs/student/registry.py` 的 `STUDENT_ANALYSES`；学生可以在该处增加新名称。
- 注册值是字符串 `package.module:ClassName`，类必须继承 `DataflowAnalysis`。
- 教师的 reference 运行**不导入学生算法模块**。学生插件发生 `NotImplementedError` 时，程序清楚地报错；绝不会静默运行参考实现。
- `--analysis ir/cfg` 只使用教师共享基础设施，不支持 `--impl student`。

## 3. 命令与输出

```bash
python main.py --list-analyses
python main.py examples/ir/rd_branch.ir --analysis rd --impl reference
python main.py examples/ir/live_loop.ir --analysis live --impl student --trace jsonl
python main.py examples/ir/live_loop.ir --analysis live --compare
```

- `--impl` 缺省值为 `reference`，确保v0.3/M3命令输出结构兼容。
- `--compare` 自动运行两套实现；目前不接受 `--trace` 同时使用（避免混合两份跟踪日志）。
- 对比结果为JSON：`analysis`、`equivalent`、`differences`、`reference`、`student`、`comparison_scope`、`note`。
- `differences` 逐节点逐字段报告 `in` / `out` 差异，并包含节点缺失、方向错误差异；**不拿处理次数/更新次数作正确性判据**。
- 无差异返回状态码0，有差异返回1；未注册、实验未完成或参数错误返回非零状态码。

## 4. 实验完成标准

最基础的学生算法至少通过三个层次的验证：

1. **数学定义**：清楚写出分析方向、抽象域、偏序、初始/边界事实、路径合并、转移函数。
2. **人工可核查**：对至少一个分支和一个循环例题逐步推导标准IN/OUT（参考 `docs/reaching_definitions.md`）。
3. **自动测试与结果解释**：使用相同IR运行两种实现并比较输出；说明为何相同、是否有可能出现精度损失，以及局限性。

开放拓展算法也必须提交说明文档、测试、样例和结果解释，且不得破坏 Reference 的既有运行。

## 5. 信任与隔离边界

M4没有做系统级沙箱，注册插件就是运行Python代码。仅适合可信的教学开发环境；若今后进行统一在线评测，应另设计容器、资源限制和提交隔离，不应直接在教师机器加载不可信学生模块。
