# MiniAnalyzer M4 学生实验：从零实现可达定义分析模块

## 实验定位

学生**不需要重写IR解析、CFG或Worklist**。教师已经提供全部基础设施及运行良好的Reference算法。你的工作是独立实现一个遵循统一接口的可达定义算法，并用自己的测试和推导验证它。

### 学习目标

理解程序中“定义”的含义，区分“定义能到达”与“变量具有确定值”；能把GEN/KILL形式化定义变成`meet()`和`transfer_node()`代码；能证明循环通过迭代得到不动点；能解释分析器的假阳性来源与适用范围。

## 一、先运行可用基线

在项目根目录执行：

```bash
python main.py examples/ir/rd_branch.ir --analysis rd --impl reference
python main.py examples/ir/rd_branch.ir --analysis rd --impl reference --trace text
python main.py examples/ir/live_loop.ir --analysis live --impl student
```

前两条是教师算法；第三条是已经完成的学生侧**独立活跃变量示例**，可用于学习统一接口如何接入。

## 二、要实现的方程

前向、路径不敏感的May分析（定义是静态指令位置）：

```text
IN[n]   = union(OUT[p] for p in pred(n))
OUT[n]  = GEN[n] union (IN[n] - KILL[n])
```

- 定义`x@4`是第4条静态指令给x赋值，**不是**“x等于4”。
- `GEN[n]`是当前指令生成的定义集合。
- `KILL[n]`是程序中**其他**对同一变量的静态定义（被当前定义覆盖）。
- 每条控制流路径有可能携带不同定义，合并采用集合并集。
- 没有定义的指令不生成/杀死局部变量定义；`call`如果有赋给局部返回变量，就定义该变量；不追踪别名、堆或外部副作用。

## 三、修改位置

只需修改 `labs/student/reaching_definitions.py`。该文件已正确继承`DataflowAnalysis`并实现`name`、`direction`、初始事实、边界事实。请补齐：

1. 在`__init__`中按变量维护所有静态定义标识，并为每条指令计算GEN与KILL。建议分两次遍历：先搜集所有定义，再计算KILL。
2. `meet(facts)`：对输入的`SetFact`求并集；空输入返回空集合事实。
3. `transfer_node(node, in_fact)`：按GEN/KILL计算并返回新的`SetFact`，不得修改传入事实。

不应导入`analyzer.analysis.reaching_definitions.ReachingDefinitionsAnalysis`来代替作业实现，也不应修改`analyzer/dataflow/solver.py`绕开实验任务。

## 四、手工例题A：分支

```text
1: c = call input()
2: x = 0
3: if c > 0 goto 6
4: x = 1
5: goto 7
6: x = 2
7: y = x + 1
8: return y
```

先写出针对x的静态定义：`x@2`、`x@4`、`x@6`。

- 第4条：`GEN[4]={x@4}`、`KILL[4]={x@2,x@6}`。
- 第6条：`GEN[6]={x@6}`、`KILL[6]={x@2,x@4}`。
- 由于两条路径都重定义x，第7条的输入集合应当是：

```text
IN[7] = {c@1, x@4, x@6}
```

为什么没有`x@2`？因为它在两条路径上都被后来的x定义杀死。

## 五、手工例题B：循环

运行 `examples/ir/rd_loop.ir`。在循环入口第3条：

```text
IN[3] = {x@1, x@4, y@2}
```

`x@1`来自第一次入环的初始化定义；`x@4`来自之后的循环回边。二者是不同的**潜在到达定义**，并不代表真实某一次执行中x同时来自两个赋值。

## 六、完成后自行测试

```bash
python main.py examples/ir/rd_branch.ir --analysis rd --impl student
python main.py examples/ir/rd_loop.ir --analysis rd --impl student --trace text
python main.py examples/ir/rd_branch.ir --analysis rd --compare
python main.py examples/ir/rd_loop.ir --analysis rd --compare
python -m pytest -q
```

初始模板中`meet()`与`transfer_node()`故意抛出`NotImplementedError`；这是作业尚未完成的预期现象。补全后才能进行比较。**对比一致只说明在这些案例上结果一致，不能替代算法数学证明和更充分的测试。**

## 七、交付要求与评价建议

提交学生算法文件、两份以上IR测试（覆盖分支与循环）、手工GEN/KILL及IN/OUT推导、自动比较结果和分析局限性说明。建议评价时分别考察：数学定义与推导、算法实现及测试质量、结果解释；进阶加分可以通过工作队列优化、新算法或可视化完成，但不应把这些作为全部学生的基础要求。

## 八、可选自主扩展

复制`labs/templates/new_analysis_template.py`到`labs/student/`，重命名并实现新算法；然后在`labs/student/registry.py`增加一个`"short-name": "labs.student.module_name:ClassName"`。通过`python main.py --list-analyses`检查注册是否成功。不必修改`main.py`或`WorklistSolver`。如果没有同名教师Reference，仍可单独运行学生模块，但不能使用`--compare`。
