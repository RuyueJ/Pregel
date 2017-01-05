Pregel
======

This is a toy single-machine implementation of *Pregel*, Google's system
for running large-scale graph algorithms on a large cluster of
machines.

For the original paper, see http://dl.acm.org/citation.cfm?id=1807184

For an illustration of how to use this implementation of *Pregel*, see
the example code in `pagerank.py`.

This repo is forked from https://github.com/mnielsen/Pregel, and a few
additions have been made. A `tutorial.ipynb` Jupyter notebook has been
added.

For information on the original toy implementation, see
http://michaelnielsen.org/ddi/pregel/


TODO
---

Examples:
* clustering
* partition, as in https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/Partition.pdf (they say "pure label propagation can be implement- ed using the vertex-centric computation model in 2 lines of code")
* semi-clustering

Features:
* aggregators
* combiners
* edge weights

Fixes:
* bug mentioned in PageRank
