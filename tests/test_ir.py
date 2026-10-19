from pathlib import Path
from analyzer.ir.reader import IRReader

ROOT = Path(__file__).resolve().parents[1]

def test_ir_reader():
    program = IRReader.read(ROOT / "examples/ir/assign.ir")
    assert program.indices() == [1, 2, 3, 4]
    assert program.get(3).use_vars() == {"x", "y"}
    assert program.get(3).def_vars() == {"z"}
