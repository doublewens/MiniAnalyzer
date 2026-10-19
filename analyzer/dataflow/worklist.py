from collections import deque


class Worklist:
    def __init__(self, nodes=()):
        self._queue = deque()
        self._present = set()
        for node in nodes:
            self.push(node)

    def push(self, node):
        """Queue a node at most once; return whether it was actually queued."""
        if node in self._present:
            return False
        self._queue.append(node)
        self._present.add(node)
        return True

    def pop(self):
        node = self._queue.popleft()
        self._present.remove(node)
        return node

    def snapshot(self) -> tuple[int, ...]:
        """Read-only snapshot of queue order for teaching and debugging."""
        return tuple(self._queue)

    def __bool__(self):
        return bool(self._queue)

    def __len__(self):
        return len(self._queue)
