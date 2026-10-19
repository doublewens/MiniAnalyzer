from analyzer.ir.instruction import (
    BranchInstruction,
    GotoInstruction,
    ReturnInstruction,
    ExitInstruction,
)

from .cfg import CFG


class CFGBuilder:
    @staticmethod
    def build(program):
        cfg = CFG()
        indices = program.indices()
        valid = set(indices)

        for index in indices:
            cfg.add_node(index)

        for pos, inst in enumerate(program.instructions):
            next_index = indices[pos + 1] if pos + 1 < len(indices) else None

            if isinstance(inst, (ReturnInstruction, ExitInstruction)):
                continue

            if isinstance(inst, GotoInstruction):
                CFGBuilder._check_target(inst.index, inst.target, valid)
                cfg.add_edge(inst.index, inst.target)
                continue

            if isinstance(inst, BranchInstruction):
                CFGBuilder._check_target(inst.index, inst.target, valid)
                if next_index is not None:
                    cfg.add_edge(inst.index, next_index)
                cfg.add_edge(inst.index, inst.target)
                continue

            if next_index is not None:
                cfg.add_edge(inst.index, next_index)

        return cfg

    @staticmethod
    def _check_target(src, target, valid):
        if target not in valid:
            raise ValueError(
                f"instruction {src} jumps to missing target {target}"
            )
