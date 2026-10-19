from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable


class DataflowFact(ABC):
    @abstractmethod
    def copy(self) -> "DataflowFact":
        raise NotImplementedError

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError


@dataclass
class SetFact(DataflowFact):
    values: set[str] = field(default_factory=set)

    def copy(self) -> "SetFact":
        return SetFact(set(self.values))

    def union(self, other: "SetFact") -> "SetFact":
        return SetFact(self.values | other.values)

    def difference(self, values: Iterable[str]) -> "SetFact":
        return SetFact(self.values - set(values))

    def add_all(self, values: Iterable[str]) -> "SetFact":
        return SetFact(self.values | set(values))

    def to_dict(self):
        return sorted(self.values)
