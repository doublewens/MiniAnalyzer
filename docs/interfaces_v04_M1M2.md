# MiniAnalyzer v0.4 M1/M2 — 接口契约（首轮落地）

> 状态：**M1、M2已实现；M3、M4尚未实现**。本文件描述实际代码行为，不是最终v0.4全部能力。

## 兼容基线（v0.3）

- 原入口 `WorklistSolver().solve(analysis)` 完全保留；新增可选关键字参数 `observer=None`。
- 原命令 `--analysis ir|cfg|live`、`--output` 保留；输出JSON的字段及语义保持不变。
- `DataflowAnalysis` 原有六个主要成员（`name`、`direction`、`new_initial_fact`、`new_boundary_fact`、`meet`、`transfer_node`）无需迁移。
- `DataflowFact.copy()` / `to_dict()` 保持不变；集合事实以稳定排序的列表序列化。
- `Worklist.push(node)` 新增布尔返回值（确实入队为`True`），此前不使用返回值的调用保持正常。
- CFG增加`entry`、`exits`、`reachable_nodes()`只读属性/方法，`to_dict()`字段保持不变。
- 仍与v0.3一致：入口为**最小编号**，全部CFG节点（含不可达节点）参与调度。`reachable_nodes()`只用于识别、说明，不改变本版本求解策略。后续若改为仅求解可达节点，需做独立设计并发布迁移说明。

## 抽象分析语义

**Forward**：`IN[n]=meet(OUT[pred(n)], boundary_if_entry)`，`OUT[n]=transfer(n,IN[n])`。

**Backward**：`OUT[n]=meet(IN[succ(n)], boundary_if_exit)`，`IN[n]=transfer(n,OUT[n])`。

`meet`是兼容保留的方法名，表示*汇合路径信息*，不承诺数学格意义下一定是meet运算；本例的Live Variables使用集合并集。实现必须定义空集合合并、边界事实、事实相等和收敛条件。

`new_initial_fact()`必须返回彼此独立的事实值；`meet()`、`transfer_node()`应避免原地修改传入事实（否则可能造成别的节点事实遭污染）；使用非单调转移、无限高度格且缺少Widening时不保证终止。该版本只保障现有经典有限集合分析的行为，不声称支持抽象解释所有复杂场景。

## 追踪API

```python
from analyzer.dataflow.trace import TraceCollector, TextTraceWriter, JSONLTraceWriter
from analyzer.dataflow.solver import WorklistSolver

observer = TraceCollector()
result = WorklistSolver().solve(analysis, observer=observer)
print(observer.events[0])
```

也可传入Python函数 `observer(event)`，或者带 `on_step(event)` 方法的对象。

每处理**一个节点**，发送一个 `TraceEvent`：

| 字段 | 含义 |
|---|---|
| `step`, `node`, `instruction` | 节点处理次数及当前IR |
| `analysis`, `direction` | 分析名称及前向/后向 |
| `queue_before`, `queue_after` | 本步前后的FIFO队列快照 |
| `sources` | 当前节点接收的前驱OUT或后继IN，以及可能的边界事实 |
| `old_in`, `old_out` | 节点旧事实 |
| `merged` | 通过路径合并得到的事实；前向为新IN，后向为新OUT |
| `transferred` | 转移计算结果；前向为新OUT，后向为新IN |
| `new_in`, `new_out` | 本步计算得到的完整新事实 |
| `changed` | 本步事实是否发生变化 |
| `enqueued` | 因本步更新而**实际新加入**的节点（已在队列中则不重复入队） |

事件只包含**脱离Fact对象的序列化快照**，Observer无法通过事件修改求解器中的变量集合。Observer设计为读取/打印/保存，不得作为调度或收敛控制的入口；如果Observer主动抛错，分析会中断并报告异常，便于定位教学工具自身问题。

### CLI

```bash
python main.py examples/ir/live_loop.ir --analysis live --trace text
python main.py examples/ir/live_loop.ir --analysis live --trace jsonl --trace-output trace.jsonl --output result.json
```

- `--trace text|jsonl`：可选，只对Worklist分析(`--analysis live`)生效。
- `--trace-output PATH`：单独保存跟踪文件；省略时写**stderr**，分析JSON仍写stdout（兼容机器读取）。
- `--output PATH`：保持原v0.3含义，只保存分析结果JSON。拒绝分析结果与跟踪输出使用同一文件。
- `--trace jsonl`：一行一个独立JSON对象，适合课堂回放与学生分析。
- 未启用Trace时，不构造节点事件和事实序列化快照；关闭Trace不会改变IN/OUT及求解统计。

## 仍待完成

未提供Reference/Student注册、Reaching Definitions正式实现、Student算法模板、基本块级CFG或Mini-C前端；这些属于下一里程碑M3/M4。本轮对旧代码只做M1/M2兼容式增强。
