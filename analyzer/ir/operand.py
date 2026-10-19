from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re

_VAR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_INT_RE = re.compile(r"^-?\d+$")


class Operand(ABC):
    @abstractmethod
    def to_dict(self):
        raise NotImplementedError

    @staticmethod
    def parse(token: str) -> "Operand":
        token = token.strip()

        if _INT_RE.fullmatch(token):
            return Constant(int(token))

        if token in {"true", "false"}:
            return Constant(token == "true")

        if _VAR_RE.fullmatch(token):
            return Variable(token)

        raise ValueError(f"invalid operand: {token}")


@dataclass(frozen=True)
class Variable(Operand):
    name: str

    def __post_init__(self):
        if not _VAR_RE.fullmatch(self.name):
            raise ValueError(f"invalid variable name: {self.name}")

    def to_dict(self):
        return {"kind": "variable", "name": self.name}

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Constant(Operand):
    value: int | bool

    def to_dict(self):
        return {"kind": "constant", "value": self.value}

    def __str__(self):
        if isinstance(self.value, bool):
            return "true" if self.value else "false"
        return str(self.value)
