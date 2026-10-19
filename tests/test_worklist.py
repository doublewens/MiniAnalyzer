from analyzer.dataflow.worklist import Worklist

def test_worklist():
    w = Worklist([1, 2])
    w.push(2)
    w.push(3)
    assert len(w) == 3
    assert [w.pop(), w.pop(), w.pop()] == [1, 2, 3]
