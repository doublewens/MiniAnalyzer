class CFG:
    def __init__(self):
        self.nodes = []
        self.successors = {}
        self.predecessors = {}

    def add_node(self, index):
        if index not in self.nodes:
            self.nodes.append(index)
        self.successors.setdefault(index, [])
        self.predecessors.setdefault(index, [])

    def add_edge(self, src, dst):
        self.add_node(src)
        self.add_node(dst)
        if dst not in self.successors[src]:
            self.successors[src].append(dst)
        if src not in self.predecessors[dst]:
            self.predecessors[dst].append(src)

    @property
    def entry(self):
        """v0.3 compatible: smallest instruction index is the entry point."""
        return min(self.nodes) if self.nodes else None

    @property
    def exits(self):
        """Nodes with no outgoing edge (an infinite loop may have none)."""
        return sorted(node for node in self.nodes if not self.successors[node])

    def reachable_nodes(self):
        """Return nodes reachable from entry; does not change solver behavior."""
        if self.entry is None:
            return set()
        reached = {self.entry}
        frontier = [self.entry]
        while frontier:
            current = frontier.pop()
            for next_node in self.successors[current]:
                if next_node not in reached:
                    reached.add(next_node)
                    frontier.append(next_node)
        return reached

    def to_dict(self):
        # Keep v0.3 JSON schema unchanged.
        return {
            "nodes": sorted(self.nodes),
            "entry": self.entry,
            "exits": self.exits,
            "edges": [
                {"from": src, "to": dst}
                for src in sorted(self.successors)
                for dst in sorted(self.successors[src])
            ],
            "successors": {str(k): sorted(v) for k, v in sorted(self.successors.items())},
            "predecessors": {str(k): sorted(v) for k, v in sorted(self.predecessors.items())},
        }
