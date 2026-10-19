from abc import ABC, abstractmethod
from enum import Enum


class Direction(str, Enum):
    FORWARD = "forward"
    BACKWARD = "backward"


class DataflowAnalysis(ABC):
    def __init__(self, program, cfg):
        self.program = program
        self.cfg = cfg

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def direction(self):
        raise NotImplementedError

    @abstractmethod
    def new_initial_fact(self):
        raise NotImplementedError

    @abstractmethod
    def new_boundary_fact(self):
        raise NotImplementedError

    @abstractmethod
    def meet(self, facts):
        raise NotImplementedError

    @abstractmethod
    def transfer_node(self, node, input_fact):
        raise NotImplementedError
