# 教师15分钟课堂演示脚本：从GEN/KILL到Worklist不动点

**前置条件**：授课电脑安装Python 3.10+；讲授前在解压的项目根目录测试命令是否运行。可先使用准备好的输出文件，无须课堂临时安装依赖。

### 第0—3分钟：把“定义”说成“值的来源”

展示`examples/ir/rd_branch.ir`。向学生提问：“运行到第7条`y=x+1`时，x的值可能由哪一条赋值产生？”

解释静态定义标记`x@4`、`x@6`的意义：**x的赋值语句位置，而非值**。强调这是前向may分析。

### 第3—6分钟：手工列GEN/KILL

板书：`GEN[4]={x@4}`，`KILL[4]={x@2,x@6}`。

解释两个被KILL的定义是整份程序中其他给x赋值的静态指令；分析执行节点4时，来自节点6的定义不必当前已经到达。真正的转移效果由`IN[4]-KILL[4]`决定。

### 第6—10分钟：运行分支分析

```bash
python main.py examples/ir/rd_branch.ir --analysis cfg
python main.py examples/ir/rd_branch.ir --analysis rd
```

让学生查找节点7：`IN[7]={c@1,x@4,x@6}`。追问：“为什么没有x@2？为什么没有具体常量1和2？” 分别讲解重定义覆盖和抽象信息层次。

### 第10—13分钟：运行循环并观察Worklist

```bash
python main.py examples/ir/rd_loop.ir --analysis rd \
  --trace text --trace-output rd_loop_trace.txt --output rd_loop_result.json
```

打开文本日志，查找`Node 3`的两次处理；比较第一次与第二次的IN集合，说明回边将`x@4`传播到循环入口，从而触发再次计算。提醒：`statistics.iterations`是**处理节点次数**，不是整个图扫描轮数。

### 第13—15分钟：两种算法并排对照

```bash
python main.py examples/ir/rd_loop.ir --analysis live
python main.py examples/ir/rd_loop.ir --analysis rd
```

**同一个IR和CFG、同一个Worklist**；Live Variables后向传播“未来还需要哪些值”，Reaching Definitions前向传播“当前值可能来自哪些赋值”。框架求解逻辑不变，变化的是抽象事实和transfer函数。

**收束语**：“MiniAnalyzer不是为了省去思考，而是让我们能观察数学定义如何变成运行中的算法。”
