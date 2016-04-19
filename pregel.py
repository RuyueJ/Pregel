"""pregel.py is a python 2.6 module implementing a toy single-machine
version of Google's Pregel system for large-scale graph processing."""

import collections
import threading
import multiprocessing

class Vertex():

    def __init__(self,id,value,out_vertices,out_weights=None):
        # This is mostly self-explanatory, but has a few quirks:
        #
        # self.id is included mainly because it's described in the
        # Pregel paper.  It is used briefly in the pagerank example,
        # but not in any essential way, and I was tempted to omit it.
        #
        # Each vertex stores the current superstep number in
        # self.superstep.  It's arguably not wise to store many copies
        # of global state in instance variables, but Pregel's
        # synchronous nature lets us get away with it.
        self.id = id
        self.value = value
        self.out_vertices = out_vertices
        self.out_weights = out_weights
        self.incoming_messages = []
        self.outgoing_messages = []
        self.active = True
        self.superstep = 0

class Pregel():

    def __init__(self,vertices,num_workers=None,stats_fn=None):
        self.vertices = vertices
        if num_workers:
            self.num_workers = num_workers
        else:
            self.num_workers = multiprocessing.cpu_count()
        if stats_fn:
            self.stats = stats_fn
        else:
            self.stats = lambda vs: vs[0].superstep

    def run(self):
        """Runs the Pregel instance."""
        self.partition = self.partition_vertices()
        self.data = []
        while self.check_active():
            # save the data at this step
            self.data.append(self.superstep())
            self.redistribute_messages()

    def partition_vertices(self):
        """Returns a dict with keys 0,...,self.num_workers-1
        representing the worker threads.  The corresponding values are
        lists of vertices assigned to that worker."""
        partition = collections.defaultdict(list)
        for vertex in self.vertices:
            partition[self.worker(vertex)].append(vertex)
        return partition

    def worker(self,vertex):
        """Returns the id of the worker that vertex is assigned to."""
        return hash(vertex) % self.num_workers

    def superstep(self):
        """Completes a single superstep.

        Note that in this implementation, worker threads are spawned,
        and then destroyed during each superstep.  This creation and
        destruction causes some overhead, and it would be better to
        make the workers persistent, and to use a locking mechanism to
        synchronize.  The Pregel paper suggests that this is how
        Google's Pregel implementation works."""
        workers = []
        for vertex_list in self.partition.values():
            worker = Worker(vertex_list)
            workers.append(worker)
            worker.start()
        for worker in workers:
            worker.join()
        return self.stats(self.vertices)

    def redistribute_messages(self):
        """Updates the message lists for all vertices."""
        for vertex in self.vertices:
            vertex.superstep +=1
            vertex.incoming_messages = []
        for vertex in self.vertices:
            for (receiving_vertex,wt,message) in vertex.outgoing_messages:
                receiving_vertex.incoming_messages.append((vertex,wt,message))
                # Fig 1 in Pregel paper
                receiving_vertex.active = True
            # otherwise we keep sending old messages!
            vertex.outgoing_messages = []

    def check_active(self):
        """Returns True if there are any active vertices, and False
        otherwise."""
        return any([vertex.active for vertex in self.vertices])

class Worker(threading.Thread):

    def __init__(self,vertices):
        threading.Thread.__init__(self)
        self.vertices = vertices

    def run(self):
        self.superstep()

    def superstep(self):
        """Completes a single superstep for all the vertices in
        self."""
        for vertex in self.vertices:
            if vertex.active:
                vertex.update()
