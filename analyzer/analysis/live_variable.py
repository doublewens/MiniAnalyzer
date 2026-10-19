from analyzer.dataflow.analysis import DataflowAnalysis, Direction
from analyzer.dataflow.fact import SetFact


class LiveVariableAnalysis(DataflowAnalysis):
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
        result = set()
        for fact in facts:
            result |= fact.values
        return SetFact(result)

    def transfer_node(self, node, out_fact):
        inst = self.program.get(node)
        result = (
            out_fact.values - inst.def_vars()
        ) | inst.use_vars()
        return SetFact(result)
