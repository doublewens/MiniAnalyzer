# MiniAnalyzer v0.4 M1/M2/M3/M4 — 教学预览版

从 v0.3 渐进开发，**保留原功能**并支持经典参考算法与学生独立开发：

- **M1**：保持 Teaching IR、指令级 CFG、原 DataflowAnalysis / WorklistSolver 接口兼容。
- **M2**：Worklist 文本或 JSONL 逐步跟踪，默认不影响分析结果。
- **M3**：经典参考算法：`live`（活跃变量，后向 May）和 `rd`（可达定义，前向 May）。
- **M4（本次新增）**：`reference` / `student` 算法注册、独立加载、实验模板、同题结果比较、相关测试与实验讲义。

当前仍为**教学预览版**，尚不包括完整 Mini-C 前端、基本块 CFG、常量传播、区间分析或真实软件安全工具的完整功能。

## 运行要求

Python **3.10+**；分析器运行仅需标准库；运行测试另需 `pytest`：

```bash
python -m pytest -q
```

## 最快开始

请在**项目根目录**运行以下命令：

```bash
# 与早期版本保持一致：缺省使用参考实现；不传 --analysis 时默认输出 CFG
python main.py examples/ir/live_loop.ir --analysis live
python main.py examples/ir/rd_branch.ir --analysis rd

# 列举算法（无需 IR 文件）
python main.py --list-analyses

# 显式运行教师的可达定义参考实现
python main.py examples/ir/rd_branch.ir --analysis rd --impl reference

# 运行完整、独立的“学生侧活跃变量示例”
python main.py examples/ir/live_loop.ir --analysis live --impl student

# 同一道题比较学生和教师的分析事实（不比较迭代次数）
python main.py examples/ir/live_loop.ir --analysis live --compare

# 结合已实现的教学跟踪
python main.py examples/ir/live_loop.ir --analysis live --impl student --trace text

# 学生可达定义实验目前是有意留空的模板：会明确报错，不自动调用参考答案
python main.py examples/ir/rd_branch.ir --analysis rd --impl student
```

> `student/live` 是**已经完成、可运行的示例**；`student/rd` 是**学生需要自行补全的作业模板**，目前不可运行。教师的 `reference/rd` 始终保持可运行。

## 推荐的教学使用方式

- **教师现场**：默认 `--impl reference`，先讲 IR、CFG，再用 `--trace text` 展示求解过程。
- **学生入门**：阅读 `labs/student/live_variable.py` 了解如何实现接口，无需更改 CFG / Solver。
- **学生实验**：补全 `labs/student/reaching_definitions.py` 里的 GEN/KILL、`meet` 和 `transfer_node`。
- **学生检验**：运行 `--impl student`，再使用 `--compare` 与教师参考事实逐节点比较；同时写手工推导和边界测试。
- **拓展项目**：新增 `labs/student/<module>.py`，再到 `labs/student/registry.py` 添加 `name: module:Class` 显式注册。

## 目录中的教学材料

- [M4 教师课堂演示脚本](docs/teacher_demo_M4.md)
- [M4 学生实验手册（可达定义）](docs/lab_M4_student_rd.md)
- [M4 接口与行为契约](docs/interfaces_v04_M4.md)
- [原 M3 可达定义详细讲义](docs/reaching_definitions.md)
- [原 M1/M2 实验接口契约](docs/interfaces_v04_M1M2.md)

## 重要限制和安全说明

1. `--compare` 对比的是**给定教学IR上、同一程序点最终IN/OUT事实**。相同不意味着算法对所有程序都正确；不同需要调查是算法错误还是分析语义约定不一致。节点处理次数不影响等价判定。
2. `--compare` 返回码：结果一致时 `0`；事实不一致时输出带 `differences` 的 JSON 并返回 `1`；参数错误、算法未完成等返回非零错误码。
3. Reference 运行时**不会加载学生算法模块**。学生模块未完成，不影响教师演示；只有显式 `--impl student` 或 `--compare` 才会运行学生代码。
4. 插件是普通 Python 源码，没有沙箱隔离：**只运行可信的本地学生代码**；不应把他人提交的代码放到教师主机直接执行。
5. 求解器为兼容旧版，仍会处理CFG中不可达节点；过程间语义、调用副作用和路径条件可行性未建模。不要把课程输出当作生产级程序安全证明。
6. Reference 算法目前直接位于 `analyzer/analysis/`，学生算法位于 `labs/student/`。两者使用同一 `DataflowAnalysis` API；不需要复制整个 MiniAnalyzer。
