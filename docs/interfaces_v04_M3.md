# MiniAnalyzer v0.4 M3：增量接口契约及教学边界

**基线**：完全继承M1/M2定义，不修改`WorklistSolver.solve(analysis, *, observer=None)`、`DataflowAnalysis`、`DataflowFact`、`TraceEvent`或既有CFG接口。

## M3新增接口

```python
from analyzer.analysis.reaching_definitions import ReachingDefinitionsAnalysis
analysis = ReachingDefinitionsAnalysis(program, cfg)
analysis.gen(4)   # 返回可修改的复制集合，而非内部集引用
analysis.kill(4)  # 同上
result = WorklistSolver().solve(analysis)
```

`analysis.name = "reaching-definitions"`，`analysis.direction = Direction.FORWARD`。事实复用`SetFact`，定义ID形如`x@4`；同一指令执行多次仍只有一个静态定义ID。

执行语义：

```text
GEN[n]  = {f"{v}@{n}" for v in DEF(n)}
KILL[n] = {f"{v}@{m}" for m != n and v in DEF(m), v in DEF(n)}
IN[n]   = union(OUT[p] for p in pred(n))  # entry boundary = empty
OUT[n]  = GEN[n] union (IN[n] - KILL[n])
```

`GEN`、`KILL`均为局部静态预计算集合；公开的`gen()`、`kill()`返回拷贝，学生更改返回值不会污染分析器。`transfer_node`创建新`SetFact`而不原地修改旧事实。

CLI新增`--analysis rd`；`--trace text|jsonl`现在对`live`和`rd`都有效，`--analysis ir|cfg|live`、原结果JSON字段、原M2日志结构保持兼容。

## 本次特意不做的事

- 没有Reference/Student算法注册和学生版模板：属于M4。
- 没有Mini-C语法解析、基本块CFG或SSA转换。
- 不进行具体条件求值、路径可行性分析、过程间调用、别名与堆副作用分析。
- 保留v0.3“调度全部CFG节点”行为；在含不可达CFG节点的特殊图上，可达定义可能污染实际可达点，需明确课堂范围。修正应作为独立的下一阶段变更并验收。

## 验收标准

1. 旧版本`ir|cfg|live`JSON与M1/M2基线一致；
2. 分支例子在7处保留两条分支定义并杀死旧定义；
3. 循环入口形成包含回边定义的不动点；
4. 连续赋值与带结果调用的GEN/KILL正确；
5. 无跟踪与文本/JSONL跟踪结果一致，且观察器拿不到可变Fact对象；
6. 所有自动测试通过，ZIP解压后可独立复现。
