from pathlib import Path
from analyzer.ir.reader import IRReader
from analyzer.cfg.builder import CFGBuilder

ROOT = Path(__file__).resolve().parents[1]

def test_loop_cfg():
    program = IRReader.read(ROOT / "examples/ir/loop.ir")
    cfg = CFGBuilder.build(program)
    assert set(cfg.successors[2]) == {3, 5}
    assert cfg.successors[4] == [2]
