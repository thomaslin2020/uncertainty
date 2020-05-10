import pygraphviz as pgv
import sys
import math

g = iter(range(sys.maxsize))
graph = pgv.AGraph(directed=True, strict=True, rankdir='UD')


def sin(o):
    node = str(next(g))
    graph.add_node(node, label="sin")
    graph.add_edge(o.node, node)
    value = math.sin(o.value)
    uncertainty = math.cos(o.value) * o.uncertainty
    return SimpleUncertainty(value, abs(uncertainty), node)


class SimpleUncertainty:
    def __init__(self, value, uncertainty, node1=None, node2=None):
        self.value = value
        self.uncertainty = uncertainty
        self.node = str(next(g))
        graph.node_attr['color'] = 'blue'
        graph.add_node(self.node, label='(%.3g±%.3g)' % (self.value, self.uncertainty))
        if node1 is not None:
            if node2 is not None:
                graph.add_edge(node1, self.node)
                graph.add_edge(node2, self.node)
            else:
                graph.add_edge(node1, self.node)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            node = str(next(g))
            graph.add_node(node, label='%.3g' % other)
            return SimpleUncertainty(self.value + other, self.uncertainty, node, self.node)
        return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty, self.node, other.node)


from time import time

t = time()
# t1 =  SimpleUncertainty(3, 5)
# for i in range(100):
#     t1 += SimpleUncertainty(3,5)
sin(sin(SimpleUncertainty(1, 2)) + sin(SimpleUncertainty(1, 2))) + SimpleUncertainty(3, 5)
print(graph.string())