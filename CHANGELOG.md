# Change Log

## v0.4-M1/M2/M3/M4（当前）

- 新增 `analyzer/registry.py`：明确的参考算法注册、学生算法延迟加载，保留原有数据流接口。
- 新增 `labs/student/` 与 `labs/templates/`：完整的学生活跃变量示例、待实现的可达定义实验模板和自选算法模板。
- 扩展命令行：`--impl reference|student`、`--compare`、`--list-analyses`，原CLI缺省保持reference行为。
- 新增 `analyzer/comparison.py`：按方向和逐节点最终IN/OUT事实比较，差异JSON可自动处理；不同Worklist处理次数不作正确性判据。
- 增加 M4 教师演示脚本、学生实验手册、接口说明和测试；拒绝覆盖输入IR文件。
- 保留M1/M2/M3已有IR、CFG、Worklist跟踪、活跃变量和可达定义算法。

## M1/M2/M3 历史说明

见 `docs/M3_开发与验收记录.md`、`docs/验收记录.md` 与 `docs/interfaces_v04_M3.md`。
