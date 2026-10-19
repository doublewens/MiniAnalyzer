class AnalysisResult:
    def __init__(
        self,
        analysis_name,
        direction,
        in_facts,
        out_facts,
        iterations,
        updates,
    ):
        self.analysis_name = analysis_name
        self.direction = direction
        self.in_facts = in_facts
        self.out_facts = out_facts
        self.iterations = iterations
        self.updates = updates

    def to_dict(self):
        nodes = sorted(set(self.in_facts) | set(self.out_facts))
        return {
            "analysis": self.analysis_name,
            "direction": self.direction.value,
            "statistics": {
                "iterations": self.iterations,
                "updates": self.updates,
            },
            "nodes": [
                {
                    "index": node,
                    "in": self.in_facts[node].to_dict(),
                    "out": self.out_facts[node].to_dict(),
                }
                for node in nodes
            ],
        }
