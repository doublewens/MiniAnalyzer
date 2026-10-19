"""M4 student lab: complete an independent reaching-definitions analyzer.

Teaching IR instruction indices identify static definitions as 'x@4'.
This is a forward may-analysis over a finite powerset domain.

Equations:
  IN[n]  = UNION(OUT[p] for p in predecessors(n))
  OUT[n] = GEN[n] UNION (IN[n] - KILL[n])

Read docs/lab_M4_student_rd.md. Do NOT import the teacher reference
implementation: the aim is to implement the transfer function yourself.
"""
from analyzer.dataflow.analysis import DataflowAnalysis, Direction
from analyzer.dataflow.fact import SetFact


class StudentReachingDefinitionsAnalysis(DataflowAnalysis):
    def __init__(self, program, cfg):
        super().__init__(program, cfg)
        # TODO: index *static definitions* (variable, instruction index),
        #       then derive GEN and KILL for every instruction.

    @property
    def name(self):
        return "reaching-definitions"

    @property
    def direction(self):
        return Direction.FORWARD

    def new_initial_fact(self):
        return SetFact()

    def new_boundary_fact(self):
        # Teaching IR models no implicit definitions of procedure inputs.
        return SetFact()

    def meet(self, facts):
        # TODO: combine facts from multiple incoming CFG edges.
        raise NotImplementedError(
            "Student RD lab unfinished: implement meet() in "
            "labs/student/reaching_definitions.py"
        )

    def transfer_node(self, node, in_fact):
        # TODO: implement GEN/KILL and OUT[n]. Return a NEW SetFact.
        raise NotImplementedError(
            "Student RD lab unfinished: implement transfer_node() in "
            "labs/student/reaching_definitions.py"
        )
