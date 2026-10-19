class Program:
    def __init__(self):
        self.instructions = []
        self._by_index = {}

    def add(self, inst):
        if inst.index in self._by_index:
            raise ValueError(f"duplicate instruction index: {inst.index}")
        self.instructions.append(inst)
        self._by_index[inst.index] = inst

    def finalize(self):
        self.instructions.sort(key=lambda i: i.index)

    def get(self, index):
        return self._by_index[index]

    def indices(self):
        return [inst.index for inst in self.instructions]

    def to_dict(self):
        return {
            "instructions": [inst.to_dict() for inst in self.instructions]
        }
