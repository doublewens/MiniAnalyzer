"""Hand-derived ground-truth checks, plus solver contracts, for M3."""
from pathlib import Path

from analyzer.analysis.reaching_definitions import ReachingDefinitionsAnalysis
from analyzer.cfg.builder import CFGBuilder
from analyzer.dataflow.analysis import Direction
from analyzer.dataflow.fact import SetFact
from analyzer.dataflow.solver import WorklistSolver
from analyzer.dataflow.trace import TraceCollector
from analyzer.ir.reader import IRReader

ROOT = Path(__file__).resolve().parents[1]


def setup_analysis(filename):
    program = IRReader.read(ROOT / "examples/ir" / filename)
    cfg = CFGBuilder.build(program)
    analysis = ReachingDefinitionsAnalysis(program, cfg)
    return analysis, cfg


def test_branch_join_and_killed_initial_definition():
    analysis, cfg = setup_analysis("rd_branch.ir")
    result = WorklistSolver().solve(analysis)
    assert analysis.direction == Direction.FORWARD
    assert analysis.name == "reaching-definitions"
    assert cfg.predecessors[7] == [5, 6]
    assert result.in_facts[7] == SetFact({"c@1", "x@4", "x@6"})
    assert "x@2" not in result.in_facts[7].values
    assert result.out_facts[7] == SetFact({"c@1", "x@4", "x@6", "y@7"})
    assert result.out_facts[1] == SetFact({"c@1"})
    assert analysis.gen(4) == {"x@4"}
    assert analysis.kill(4) == {"x@2", "x@6"}
    assert analysis.gen(3) == set() and analysis.kill(3) == set()
    assert result.to_dict()["direction"] == "forward"


def test_loop_fixed_point_uses_back_edge():
    analysis, cfg = setup_analysis("rd_loop.ir")
    result = WorklistSolver().solve(analysis)
    assert cfg.predecessors[3] == [2, 5]
    assert result.in_facts[3] == SetFact({"x@1", "x@4", "y@2"})
    assert result.out_facts[4] == SetFact({"x@4", "y@2"})
    assert result.in_facts[6] == SetFact({"x@1", "x@4", "y@2"})
    assert result.iterations > len(cfg.nodes)  # node reprocessed after back edge

    # Verify the *equations* at each program point, independent of queue order.
    for node in cfg.nodes:
        from_preds = [result.out_facts[p] for p in cfg.predecessors[node]]
        if node == cfg.entry:
            from_preds.append(analysis.new_boundary_fact())
        assert result.in_facts[node] == analysis.meet(from_preds)
        assert result.out_facts[node] == analysis.transfer_node(node, result.in_facts[node])


def test_sequential_overwrite_unary_and_calls():
    analysis, _ = setup_analysis("rd_kill.ir")
    result = WorklistSolver().solve(analysis)
    assert analysis.gen(1) == {"x@1"}
    assert analysis.gen(2) == {"x@2"}
    assert analysis.gen(3) == {"x@3"}
    assert analysis.gen(4) == set()  # result-less call creates no local definition
    assert analysis.kill(2) == {"x@1", "x@3"}
    assert result.in_facts[3] == SetFact({"x@2"})
    assert result.out_facts[3] == SetFact({"x@3"})
    assert result.out_facts[4] == SetFact({"x@3"})


def test_transfer_does_not_mutate_or_share_and_introspection_is_safe():
    analysis, _ = setup_analysis("rd_branch.ir")
    incoming = SetFact({"x@2", "c@1"})
    after = analysis.transfer_node(4, incoming)
    assert incoming == SetFact({"x@2", "c@1"})
    assert after == SetFact({"x@4", "c@1"})
    generated = analysis.gen(4)
    generated.clear()
    killed = analysis.kill(4)
    killed.clear()
    assert analysis.gen(4) == {"x@4"}
    assert analysis.kill(4) == {"x@2", "x@6"}
    assert analysis.new_initial_fact() is not analysis.new_initial_fact()


def test_observer_snapshots_match_nontraced_result():
    analysis, _ = setup_analysis("rd_loop.ir")
    collector = TraceCollector()
    traced = WorklistSolver().solve(analysis, observer=collector)
    plain = WorklistSolver().solve(analysis)
    assert traced.to_dict() == plain.to_dict()
    assert len(collector.events) == traced.iterations
    assert all(e["analysis"] == "reaching-definitions" for e in collector.events)
    assert all(e["direction"] == "forward" for e in collector.events)
    assert all(e["merged"] == e["new_in"] for e in collector.events)
    assert all(e["transferred"] == e["new_out"] for e in collector.events)
    assert any(e["node"] == 3 and "x@4" in e["new_in"] for e in collector.events)
    collector.events[0]["new_out"].append("bogus@999")
    assert "bogus@999" not in traced.out_facts[1].values
