"""Runnable student-side *example* implementation of live-variable analysis.

This example is intentionally simple and uses only the public contract.
Students can inspect it before writing a different analysis of their own.
"""
from analyzer.dataflow.analysis import DataflowAnalysis, Direction
from analyzer.dataflow.fact import SetFact


class StudentLiveVariableAnalysis(DataflowAnalysis):
    @property
    def name(self):
        return "live-variable"

    @property
    def direction(self):
        return Direction.BACKWARD

    def new_initial_fact(self):
        return SetFact()

    def new_boundary_fact(self):
        return SetFact()

    def meet(self, facts):
        all_live = set()
        for fact in facts:
            all_live.update(fact.values)
        return SetFact(all_live)

    def transfer_node(self, node, out_fact):
        instr = self.program.get(node)
        return SetFact(instr.use_vars() | (out_fact.values - instr.def_vars()))
