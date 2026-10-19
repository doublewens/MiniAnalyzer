from pathlib import Path
from analyzer.ir.reader import IRReader
from analyzer.cfg.builder import CFGBuilder
from analyzer.dataflow.solver import WorklistSolver
from analyzer.analysis.live_variable import LiveVariableAnalysis
from analyzer.dataflow.fact import SetFact

ROOT = Path(__file__).resolve().parents[1]

def analyze(name):
    program = IRReader.read(ROOT / "examples/ir" / name)
    cfg = CFGBuilder.build(program)
    return WorklistSolver().solve(LiveVariableAnalysis(program, cfg))

def test_live_variable_branch():
    result = analyze("live.ir")
    assert result.in_facts[1] == SetFact()
    assert result.out_facts[1] == SetFact({"x"})
    assert result.in_facts[8] == SetFact({"y"})
    assert result.out_facts[8] == SetFact()

def test_live_variable_loop_converges():
    result = analyze("live_loop.ir")
    assert result.in_facts[3] == SetFact({"x", "y"})
    assert result.in_facts[6] == SetFact({"x"})
