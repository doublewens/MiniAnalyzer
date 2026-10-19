# MiniAnalyzer M4：教师15分钟课堂演示脚本

**教学目标**：让学生知道经典分析算法有统一基础设施，独立算法如何接入，以及如何比较两种实现，而不是一上来讲插件开发细节。

### 第1—3分钟：先运行教师Reference

```bash
python main.py examples/ir/rd_branch.ir --analysis rd --impl reference
```

课堂问：第7条`y=x+1`处，x可能由哪条语句定义？让学生给出`x@4`和`x@6`。说明`x@2`已被两条分支上的重新定义覆盖。

### 第4—7分钟：展示后向分析与前向分析共用求解器

```bash
python main.py examples/ir/live_loop.ir --analysis live --impl reference --trace text
python main.py examples/ir/rd_loop.ir --analysis rd --impl reference --trace text
```

讲解：活跃变量的`OUT`由后继提供，向前传播；可达定义的`IN`由前驱提供，向后传播。两者使用同一个`WorklistSolver`，数学定义由`DataflowAnalysis`各自实现。

### 第8—11分钟：演示独立的学生实现和结果对比

```bash
python main.py --list-analyses
python main.py examples/ir/live_loop.ir --analysis live --impl student
python main.py examples/ir/live_loop.ir --analysis live --compare
```

讲解：学生侧的活跃变量算法是单独编写的完整示例，与Reference共享IR、CFG、Solver。比较只检查方向和每个程序点的最终IN/OUT；不同合法调度可能有不同处理次数。

### 第12—15分钟：解释学生实验的起点

```bash
python main.py examples/ir/rd_branch.ir --analysis rd --impl student
```

这条命令当前**预期失败**，提示补全`meet()`和`transfer_node()`。请说明：教师参考算法仍能正常运行，学生只需补全`labs/student/reaching_definitions.py`，即可接入现有基础设施。

### 教学提醒

- 学生独立完成的不是另一个解析器或CFG，而是一个真实可运行的分析算法。
- 一次案例对比一致**不等于**对所有程序都已证明正确。
- 当前平台是简化Teaching IR、指令级CFG、路径不敏感分析，不能替代生产级程序安全工具。
- M4的学生代码属于普通Python程序；教师演示时应使用可信的教学示例，不直接加载陌生代码。
