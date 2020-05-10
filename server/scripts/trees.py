import networkx as nx
from graphviz import Digraph
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv
import time


t1 = time.time()
G = nx.DiGraph()
G.add_node(1, data='3')
G.add_edge(1, 2)
G.add_edge(2, 3)
G.add_edge(3, 4)
G.add_edge(4, 1)
G.add_edge(1, 3)
G.add_edge(2, 4)
print(G.edges(data=True))
for u, v, d in G.edges(data=True):
    d['label'] = d.get('weight', '')

A = to_agraph(G)
A.layout(prog='dot')
A.draw('test-output/test.png')
print(time.time() - t1)

#
# import networkx as nx
#
# G = nx.Graph()
# G.add_node(1)
# G.add_node(2)
# G.add_edge(1, 2)
# G.add_edge(2, 4)
# G.add_edge(2, 5)
# G.add_edge(2, 5)
#
# H = nx.Graph()
# H.add_edge(1, 2)
# H.add_edge(1, 3)
# H.add_edge(5, 8)
#
# F = nx.compose(G, H)
# A = to_agraph(F)
# print(A)
# A.layout('dot')
# A.draw('test-output/abcd.png')
#
# G = nx.DiGraph()
# G.add_node(1)
# G.add_node(2)
# G.add_node(3)
# G.add_edge(1, 3)
# G.add_edge(2, 3)
#
# H = nx.DiGraph()
# H.add_node(4)
# H.add_node(5)
# G.add_edge(3,5)
# G.add_edge(4,5)
# F = nx.compose(G,H)
# A = to_agraph(F)
# print(A)
# A.layout('dot')
# A.draw('test-output/abcd.png')
