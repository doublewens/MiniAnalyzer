"""M1/M2 observational-equivalence, directional and snapshot tests."""
import io
import json
from pathlib import Path

from analyzer.analysis.live_variable import LiveVariableAnalysis
from analyzer.cfg.builder import CFGBuilder
from analyzer.dataflow.analysis import DataflowAnalysis, Direction
from analyzer.dataflow.fact import SetFact
from analyzer.dataflow.solver import WorklistSolver
from analyzer.dataflow.trace import TraceCollector, JSONLTraceWriter, TextTraceWriter
from analyzer.ir.reader import IRReader

ROOT = Path(__file__).resolve().parents[1]


def load(filename):
    p = IRReader.read(ROOT / 'examples/ir' / filename)
    return p, CFGBuilder.build(p)


def test_trace_opt_in_does_not_change_dataflow_result():
    for filename in ('assign.ir', 'branch.ir', 'loop.ir', 'live.ir', 'live_loop.ir'):
        program, cfg = load(filename)
        analysis = LiveVariableAnalysis(program, cfg)
        plain = WorklistSolver().solve(analysis).to_dict()
        collector = TraceCollector()
        traced = WorklistSolver().solve(analysis, observer=collector).to_dict()
        assert plain == traced, filename
        assert len(collector.events) == plain['statistics']['iterations']
        assert [e['step'] for e in collector.events] == list(range(1, len(collector.events) + 1))
        assert sum(e['changed'] for e in collector.events) == plain['statistics']['updates']


def test_backward_trace_has_direction_sources_and_real_queue_reenqueue():
    program, cfg = load('live_loop.ir')
    trace = TraceCollector()
    result = WorklistSolver().solve(LiveVariableAnalysis(program, cfg), observer=trace)
    assert result.in_facts[3] == SetFact({'x', 'y'})
    assert trace.events[0]['node'] == 6
    assert trace.events[0]['sources'] == [{'source': 'boundary', 'node': None, 'fact': []}]
    node3 = next(e for e in trace.events if e['node'] == 3)
    assert node3['direction'] == 'backward'
    assert node3['merged'] == ['x']  # OUT[3] is obtained from successors.
    assert node3['transferred'] == ['x', 'y']  # IN[3] = USE U (OUT-DEF).
    assert len(trace.events) > len(cfg.nodes)  # loop caused reprocessing
    for event in trace.events:
        assert event['queue_before'][0] == event['node']
        assert len(event['queue_after']) == len(set(event['queue_after']))
        assert set(event['enqueued']).issubset(set(event['queue_after']))


class TinyForwardAnalysis(DataflowAnalysis):
    """A test analysis with GEN at assignments, not part of v0.4 release features."""
    @property
    def name(self):
        return 'test-forward'

    @property
    def direction(self):
        return Direction.FORWARD

    def new_initial_fact(self):
        return SetFact()

    def new_boundary_fact(self):
        return SetFact({'START'})

    def meet(self, facts):
        merged = set()
        for f in facts:
            merged |= f.values
        return SetFact(merged)

    def transfer_node(self, node, input_fact):
        inst = self.program.get(node)
        return SetFact(input_fact.values | {f'd{node}'}) if inst.def_vars() else input_fact.copy()


def test_forward_trace_and_boundary():
    program, cfg = load('branch.ir')
    analysis = TinyForwardAnalysis(program, cfg)
    trace = TraceCollector()
    result = WorklistSolver().solve(analysis, observer=trace)
    assert trace.events[0]['node'] == 1
    assert trace.events[0]['sources'] == [{'source': 'boundary', 'node': None, 'fact': ['START']}]
    assert trace.events[0]['merged'] == ['START']
    assert 'START' in result.in_facts[1].values
    assert WorklistSolver().solve(analysis).to_dict() == result.to_dict()


def test_observer_mutating_event_cannot_change_solver_internal_facts():
    program, cfg = load('live_loop.ir')
    a = LiveVariableAnalysis(program, cfg)
    expected = WorklistSolver().solve(a).to_dict()

    def noisy_observer(event):
        # Deliberately vandalize the detached event payload.
        event.sources[0]['fact'].append('INJECTED')
        event.new_in.append('INJECTED')

    assert WorklistSolver().solve(a, observer=noisy_observer).to_dict() == expected


def test_trace_formatters_roundtrip_json_and_text():
    program, cfg = load('live_loop.ir')
    analysis = LiveVariableAnalysis(program, cfg)
    sink = io.StringIO()
    result = WorklistSolver().solve(analysis, observer=JSONLTraceWriter(sink))
    data = [json.loads(line) for line in sink.getvalue().splitlines()]
    assert len(data) == result.iterations
    assert data[0]['node'] == 6
    assert data[0]['queue_before'][0] == 6
    text = io.StringIO()
    WorklistSolver().solve(analysis, observer=TextTraceWriter(text))
    assert 'worklist before:' in text.getvalue()
    assert 'transfer -> IN[' in text.getvalue()


def test_cfg_accessors_and_reachable_nodes_unchanged_schema():
    program, cfg = load('live_loop.ir')
    schema = cfg.to_dict()
    assert schema['entry'] == cfg.entry == 1
    assert schema['exits'] == cfg.exits == [6]
    assert cfg.reachable_nodes() == set(cfg.nodes)
    # M1 does not remove unreachable nodes from v0.3's scheduling policy.
    p2 = IRReader.read(ROOT / 'examples/ir/trace_unreachable.ir')
    c2 = CFGBuilder.build(p2)
    assert 3 not in c2.reachable_nodes()
    assert 3 in c2.nodes
    assert set(c2.to_dict()) == set(schema)
