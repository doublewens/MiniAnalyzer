"""v0.3-compatible generic Worklist solver with optional v0.4 teaching trace."""
from copy import deepcopy

from .analysis import Direction
from .result import AnalysisResult
from .trace import TraceEvent, notify
from .worklist import Worklist


class WorklistSolver:
    def solve(self, analysis, *, observer=None):
        """Solve the equations. Observer is optional and cannot control scheduling.

        v0.4 M1/M2 preserves v0.3's policy of scheduling *all* CFG nodes,
        including unreachable nodes. Its limits are explained in docs.
        """
        nodes = sorted(analysis.cfg.nodes)
        if not nodes:
            raise ValueError('CFG contains no nodes')
        in_facts = {node: analysis.new_initial_fact() for node in nodes}
        out_facts = {node: analysis.new_initial_fact() for node in nodes}
        if analysis.direction == Direction.FORWARD:
            return self._solve_forward(analysis, nodes, in_facts, out_facts, observer)
        if analysis.direction == Direction.BACKWARD:
            return self._solve_backward(analysis, nodes, in_facts, out_facts, observer)
        raise ValueError(f"unknown analysis direction: {analysis.direction}")

    @staticmethod
    def _snapshot(fact):
        return deepcopy(fact.to_dict())

    def _emit(self, observer, *, analysis, step, node, queue_before,
              sources, old_in, old_out, merged, transferred, new_in,
              new_out, changed, enqueued, worklist):
        if observer is None:
            return
        event = TraceEvent(
            step=step, analysis=analysis.name, direction=analysis.direction.value,
            node=node, instruction=str(analysis.program.get(node)),
            queue_before=queue_before, queue_after=worklist.snapshot(),
            sources=tuple(sources),
            old_in=self._snapshot(old_in), old_out=self._snapshot(old_out),
            merged=self._snapshot(merged), transferred=self._snapshot(transferred),
            new_in=self._snapshot(new_in), new_out=self._snapshot(new_out),
            changed=changed, enqueued=tuple(enqueued),
        )
        notify(observer, event)

    def _solve_forward(self, analysis, nodes, in_facts, out_facts, observer):
        entry = analysis.cfg.entry
        boundary = analysis.new_boundary_fact()
        worklist = Worklist(nodes)
        iterations = 0
        updates = 0

        while worklist:
            queue_before = worklist.snapshot() if observer is not None else ()
            node = worklist.pop()
            iterations += 1
            old_in, old_out = in_facts[node], out_facts[node]
            source_nodes = analysis.cfg.predecessors[node]
            incoming = [out_facts[pred] for pred in source_nodes]
            if node == entry:
                incoming.append(boundary)

            # Detached snapshots: observer cannot mutate the live facts.
            sources = []
            if observer is not None:
                sources = [
                    {'source': 'predecessor', 'node': pred, 'fact': self._snapshot(out_facts[pred])}
                    for pred in source_nodes
                ]
                if node == entry:
                    sources.append({'source': 'boundary', 'node': None,
                                    'fact': self._snapshot(boundary)})

            new_in = analysis.meet(incoming)
            new_out = analysis.transfer_node(node, new_in)
            changed = new_in != old_in or new_out != old_out
            enqueued = []
            if changed:
                in_facts[node], out_facts[node] = new_in, new_out
                updates += 1
                for succ in analysis.cfg.successors[node]:
                    if worklist.push(succ):
                        enqueued.append(succ)
            self._emit(observer, analysis=analysis, step=iterations, node=node,
                       queue_before=queue_before, sources=sources,
                       old_in=old_in, old_out=old_out, merged=new_in,
                       transferred=new_out, new_in=new_in, new_out=new_out,
                       changed=changed, enqueued=enqueued, worklist=worklist)

        return AnalysisResult(analysis.name, analysis.direction, in_facts,
                              out_facts, iterations, updates)

    def _solve_backward(self, analysis, nodes, in_facts, out_facts, observer):
        exits = set(analysis.cfg.exits)
        boundary = analysis.new_boundary_fact()
        worklist = Worklist(reversed(nodes))
        iterations = 0
        updates = 0

        while worklist:
            queue_before = worklist.snapshot() if observer is not None else ()
            node = worklist.pop()
            iterations += 1
            old_in, old_out = in_facts[node], out_facts[node]
            source_nodes = analysis.cfg.successors[node]
            outgoing = [in_facts[succ] for succ in source_nodes]
            if node in exits:
                outgoing.append(boundary)

            sources = []
            if observer is not None:
                sources = [
                    {'source': 'successor', 'node': succ, 'fact': self._snapshot(in_facts[succ])}
                    for succ in source_nodes
                ]
                if node in exits:
                    sources.append({'source': 'boundary', 'node': None,
                                    'fact': self._snapshot(boundary)})

            new_out = analysis.meet(outgoing)
            new_in = analysis.transfer_node(node, new_out)
            changed = new_in != old_in or new_out != old_out
            enqueued = []
            if changed:
                in_facts[node], out_facts[node] = new_in, new_out
                updates += 1
                for pred in analysis.cfg.predecessors[node]:
                    if worklist.push(pred):
                        enqueued.append(pred)
            self._emit(observer, analysis=analysis, step=iterations, node=node,
                       queue_before=queue_before, sources=sources,
                       old_in=old_in, old_out=old_out, merged=new_out,
                       transferred=new_in, new_in=new_in, new_out=new_out,
                       changed=changed, enqueued=enqueued, worklist=worklist)

        return AnalysisResult(analysis.name, analysis.direction, in_facts,
                              out_facts, iterations, updates)
