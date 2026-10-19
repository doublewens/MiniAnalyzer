"""Illustrative template for *new* student algorithms; not registered.

Copy this file under labs/student/, rename the class, fill the TODOs,
and register it in labs/student/registry.py.
"""
from analyzer.dataflow.analysis import DataflowAnalysis, Direction
from analyzer.dataflow.fact import SetFact


class NewAnalysisTemplate(DataflowAnalysis):
    @property
    def name(self):
        return "rename-me"

    @property
    def direction(self):
        return Direction.FORWARD  # TODO: choose FORWARD / BACKWARD

    def new_initial_fact(self):
        return SetFact()  # TODO: adapt to your analysis lattice

    def new_boundary_fact(self):
        return SetFact()  # TODO: specify your boundary condition

    def meet(self, facts):
        raise NotImplementedError("Implement the path-merge operation")

    def transfer_node(self, node, input_fact):
        raise NotImplementedError("Implement your abstract transfer")
