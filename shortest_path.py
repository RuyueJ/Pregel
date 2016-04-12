"""shortest_path.py illustrates how to use the pregel.py library, and
tests that the library works.

It illustrates pregel.py by computing the single-source shortest path,
for a randomly-created 10-vertex graph. Edges have weight 1. (TODO:
extend pregel.py to allow weighted edges.)

It tests pregel.py by computing the SSSP for the same graph using the
method built in to NetworkX, and showing that the two outputs are
identical.

"""

from __future__ import print_function

from pregel import Vertex, Pregel

import numpy as np

# The next two imports are only needed for the test.
import networkx as nx
import random

num_workers = 4
num_vertices = 10

source = 0

def main():
    # vertices start with infinite distance
    vertices = [ShortestPathVertex(j, np.inf, [])
                for j in range(num_vertices)]
    create_edges(vertices)

    sp_test = shortest_path_test(vertices)
    print("NetworkX computation of SP:\n%s" % sp_test)

    sp_pregel = shortest_path_pregel(vertices)
    print("Pregel computation of SP:\n%s" % sp_pregel)

    assert(sp_test == sp_pregel)

def create_edges(vertices):
    """Generates 3 randomly chosen outgoing edges from each vertex in
    vertices."""
    for vertex in vertices:
        vertex.out_vertices = random.sample(vertices, 3)

def shortest_path_test(vertices):
    """Computes the single-source shortest path using NetworkX."""
    G = nx.DiGraph()
    for u in vertices:
        for v in u.out_vertices:
            G.add_edge(u.id, v.id)
    sp = nx.single_source_shortest_path_length(G, source)
    return sp

def shortest_path_pregel(vertices):
    """Computes the single-source shortest path using Pregel."""
    p = Pregel(vertices,num_workers)
    p.run()
    # We present our result as a dict to conform to NetworkX.
    # NetworkX will only include values for the reachable nodes so we
    # check for finite values
    return {vertex.id: vertex.value for vertex in p.vertices
            if np.isfinite(vertex.value)}

class ShortestPathVertex(Vertex):
    # See Fig 5 in the Pregel paper
    def update(self):
        if self.id == source:
            mindist = 0
        else:
            mindist = np.inf
        for vertex, wt, val in self.incoming_messages:
            mindist = min(mindist, val)
        if mindist < self.value:
            self.value = mindist
            self.outgoing_messages = [(vertex, 1, self.value + 1)
                                      for vertex in self.out_vertices]
        else:
            self.active = False

if __name__ == "__main__":
    main()
