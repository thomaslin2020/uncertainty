# TODO: Unit Conversion
# TODO: NLP processing
import sys
import math

# TODO: Add different levels of verbosity
# group functions, self-defined functions, visualize uncertainty propagation
from contextlib import contextmanager

from graphviz import Digraph


def temp_node(o, name):
    node = str(next(num))
    dot.node(node, name)
    dot.edge(o.node, node)
    return node


def create_temp_node(s, o, operator):
    if not isinstance(o, (int, float)):
        o = o.node
    operator_node = str(next(num))
    dot.node(operator_node, operator)
    dot.edge(s.node, operator_node)
    dot.edge(o, operator_node)
    return operator_node


def binary_node(s, o, operator):
    global level
    operator_node = str(next(num))
    dot.node(operator_node, operator)
    dot.edges([(s.node, operator_node), (o.node, operator_node)])
    if level == 2:
        return operator_node
    temp_node_1 = str(next(num))
    temp_node_2 = str(next(num))
    dot.node(temp_node_1, '%.2g %s %.2g' % (s.value, operator, o.value))
    dot.node(temp_node_2, 'Δ: %.2g + %.2g' % (s.uncertainty, o.uncertainty))
    dot.edge(operator_node, temp_node_1)
    dot.edge(operator_node, temp_node_2)
    if level == 3:
        return temp_node_1, temp_node_2
    return temp_node_1, temp_node_2, s.node, o.node


def sin(o):
    value = math.sin(o.value)
    uncertainty = math.cos(o.value) * o.uncertainty
    return SimpleUncertainty(value, abs(uncertainty), temp_node(o, 'sin'))


class SimpleUncertainty:
    def __init__(self, value, uncertainty, *nodes):
        self.value = value
        self.uncertainty = uncertainty
        self.node = str(next(num))
        dot.node(self.node, '(%.3g±%.3g)' % (self.value, self.uncertainty))
        dot.edges([(i, self.node) for i in nodes])

    def __add__(self, other):
        if isinstance(other, (int, float)):
            node = str(next(num))
            dot.node(node, '%.3g' % other)
            return SimpleUncertainty(self.value + other, self.uncertainty, create_temp_node(self, other, '+'))
        return SimpleUncertainty(self.value + other.value, self.uncertainty + other.uncertainty,
                                 *binary_node(self, other, '+'))


def start_session(verbose=2):
    n = iter(range(sys.maxsize))
    d = Digraph(strict=True, comment='Computational Graph')
    return n, d, verbose


def process(string, name=None):
    print('Solution: %s' % eval(string))
    print(str(dot))
    if name:
        dot.save(name)


num, dot, level = start_session(3)
process('SimpleUncertainty(1, 2) + SimpleUncertainty(3, 4)', 'file.gv')
