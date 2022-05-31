class Coloring:
    def __init__(self, graph):
        self.graph = graph
        self.V = len(graph)
    def greedyColoring(self):
        self.result = [-1] * self.V

        self.result[0] = 0;

        available = [False] * self.V

        for u in range(1, self.V):
            for i in self.graph[u]:
                if (self.result[i] != -1):
                    available[self.result[i]] = True

            cr = 0
            while cr < self.V:
                if (available[cr] == False):
                    break

                cr += 1

            self.result[u] = cr
            for i in self.graph[u]:
                if (self.result[i] != -1):
                    available[self.result[i]] = False
        return self.result
