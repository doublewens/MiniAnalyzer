from __future__ import annotations
from dataclasses import dataclass
from abc import ABC
from typing import Optional

from .operand import Operand, Variable


@dataclass
class Instruction(ABC):
    index: int

    @property
    def kind(self) -> str:
        return self.__class__.__name__.replace("Instruction", "").lower()

    def use_vars(self) -> set[str]:
        return set()

    def def_vars(self) -> set[str]:
        return set()

    def jump_targets(self) -> list[int]:
        return []

    def to_dict(self):
        return {
            "index": self.index,
            "kind": self.kind,
            "use": sorted(self.use_vars()),
            "def": sorted(self.def_vars()),
            "targets": self.jump_targets(),
            "text": str(self),
        }


@dataclass
class AssignInstruction(Instruction):
    target: Variable
    value: Operand

    def use_vars(self):
        return {self.value.name} if isinstance(self.value, Variable) else set()

    def def_vars(self):
        return {self.target.name}

    def __str__(self):
        return f"{self.target} = {self.value}"


@dataclass
class BinaryOpInstruction(Instruction):
    target: Variable
    left: Operand
    operator: str
    right: Operand

    def use_vars(self):
        result = set()
        if isinstance(self.left, Variable):
            result.add(self.left.name)
        if isinstance(self.right, Variable):
            result.add(self.right.name)
        return result

    def def_vars(self):
        return {self.target.name}

    def __str__(self):
        return f"{self.target} = {self.left} {self.operator} {self.right}"


@dataclass
class UnaryOpInstruction(Instruction):
    target: Variable
    operator: str
    operand: Operand

    def use_vars(self):
        return {self.operand.name} if isinstance(self.operand, Variable) else set()

    def def_vars(self):
        return {self.target.name}

    def __str__(self):
        return f"{self.target} = {self.operator}{self.operand}"


@dataclass
class BranchInstruction(Instruction):
    left: Operand
    operator: str
    right: Operand
    target: int

    def use_vars(self):
        result = set()
        if isinstance(self.left, Variable):
            result.add(self.left.name)
        if isinstance(self.right, Variable):
            result.add(self.right.name)
        return result

    def jump_targets(self):
        return [self.target]

    def __str__(self):
        return f"if {self.left} {self.operator} {self.right} goto {self.target}"


@dataclass
class GotoInstruction(Instruction):
    target: int

    def jump_targets(self):
        return [self.target]

    def __str__(self):
        return f"goto {self.target}"


@dataclass
class CallInstruction(Instruction):
    function: str
    arguments: list[Operand]
    result: Optional[Variable] = None

    def use_vars(self):
        return {
            arg.name
            for arg in self.arguments
            if isinstance(arg, Variable)
        }

    def def_vars(self):
        return {self.result.name} if self.result is not None else set()

    def __str__(self):
        args = ", ".join(str(arg) for arg in self.arguments)
        call = f"call {self.function}({args})"
        if self.result is not None:
            return f"{self.result} = {call}"
        return call


@dataclass
class ReturnInstruction(Instruction):
    value: Optional[Operand] = None

    def use_vars(self):
        if isinstance(self.value, Variable):
            return {self.value.name}
        return set()

    def __str__(self):
        return "return" if self.value is None else f"return {self.value}"


@dataclass
class ExitInstruction(Instruction):
    def __str__(self):
        return "exit"
