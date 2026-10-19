# 教师演示指南：数据流分析中的Worklist如何达到不动点

适用：当前学期数据流分析课程中的**10—15分钟辅助演示**。以旧版教学内容为主，不要求学生临时完成MiniAnalyzer项目。

## 课前（1分钟）

Python 3.10+，在项目根目录执行：

```bash
python -m pytest -q
python main.py examples/ir/live_loop.ir --analysis cfg
```

## 课堂片段（建议约12分钟）

**0—2分钟：展示IR与CFG。**

```bash
python main.py examples/ir/live_loop.ir --analysis ir
python main.py examples/ir/live_loop.ir --analysis cfg
```

强调`if`有两条后继、`goto`形成回边。提出问题：不真正执行程序，如何确定在循环条件处变量是否仍会被使用？

**2—4分钟：先看最后的分析结果。**

```bash
python main.py examples/ir/live_loop.ir --analysis live
```

讲`IN[n]`是执行该指令**之前**活跃的变量集合，`OUT[n]`是执行**之后**活跃的集合；活跃变量是“某条可能的后续路径上，在重新定义前仍会读取其当前值”。

**4—10分钟：打开Worklist跟踪。**

```bash
python main.py examples/ir/live_loop.ir --analysis live --trace text --trace-output trace.txt --output result.json
```

打开`trace.txt`，先看`Node 6: return x`：出口的OUT为空，读取x使IN={x}。再看`Node 3: if x >= y goto 6`：后继提供的IN合并得到OUT，并通过条件表达式USE={x,y}使IN={x,y}。对比`Node 5: goto 3`：回边会使已有节点需要重新计算。

讲授公式（后向）：

```text
OUT[n] = union(IN[s] for s in successors[n])
IN[n]  = USE[n] union (OUT[n] - DEF[n])
```

**10—12分钟：用统计收束。**`statistics.iterations`是“从Worklist取出并处理节点的次数”，不是完成了多少轮全图遍历。事实稳定后不会再产生新的入队动作，因此Worklist清空，算法结束。

最后强调：**可观察的迭代过程是教学特色；真实工具常省略它直接输出最终分析结果。**

## 三个检查问题

1. 为什么活跃变量分析要逆着控制流传播信息？
2. 为什么循环在静态分析中不必逐次执行？
3. 哪个步骤决定了“有多个可能后继”的信息如何汇合？

## 课堂注意事项

- 本版本只实现了活跃变量这一种参考分析，`--trace`不能与`--analysis cfg`同时使用。
- 原本v0.3已调度全部节点，即使不可达节点也可能出现在跟踪中；请使用自带`live_loop.ir`避免此问题分散教学注意力。
- 不需网络、不需Docker、不需图形界面；纯Python即可演示。
