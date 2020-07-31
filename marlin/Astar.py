import numpy as np
from sortedcontainers import SortedList


class Node:
    def __init__(self, x, y, lat=None, lng=None):
        self.x = x
        self.y = y
        self.lat = lat
        self.lng = lng
        self.distance = float('inf')

    def get_distance(self, b):
        d = (self.x - b.x)**2 + (self.y - b.y)**2
        return np.sqrt(d)

    def get_neighbours(self, graph):
        neighbours_coordinates = np.array([[-1, 0], [0, 0], [1, 0], [-1, 1],
                                           [0, 1], [1, 1], [-1, -1], [0, -1],
                                           [1, -1]])
        neighbours = []
        for i in neighbours_coordinates:
            point = graph[self.x+i[0]][self.y+i[1]]
            if point is not None:
                neighbours.append(point)

        neighbours.remove(self)
        return neighbours

    def __eq__(self, b):
        return b.x == self.x and b.y == self.y

    def __repr__(self):
        return '[x: {}, y: {}, distance: {}, obj: {}]'.format(self.x, self.y,
                                                              self.distance,
                                                              self.__hash__)


class Path:
    def __init__(self, node_list, length, end):
        self.node_list = node_list
        self.length = length
        self.end = end
        self.euristic_length = length + end.get_distance(self.node_list[-1])

    def expand(self, graph):
        paths = []
        last_node = self.node_list[-1]
        for node in last_node.get_neighbours(graph):
            node_distance = self.length + last_node.get_distance(node)
            if node_distance < node.distance:
                paths.append(Path(self.node_list + [node],
                                  node_distance,
                                  self.end))
                node.distance = node_distance

        return paths

    def __lt__(self, p):
        return self.euristic_length < p.euristic_length

    def __gt__(self, p):
        return self.euristic_length > p.euristic_length

    def __eq__(self, p):
        return self.euristic_length == p.euristic_length

def reset_graph_distances(graph):
    for x in graph.keys():
        for y in graph[x].keys():
            if graph[x][y] is not None:
                graph[x][y].distance = float('inf')

def A_star(start, end, graph):
    reset_graph_distances(graph)
    paths = SortedList()
    start.distance = 0
    paths.add(Path([start], 0, end))
    best_solution = None

    while len(paths) > 0 and \
            (best_solution is None or best_solution > paths[0]):
        path = paths.pop(0)
        expanded_paths = path.expand(graph)
        for p in expanded_paths:
            if p.node_list[-1] == end and (best_solution is None or p < best_solution):
                best_solution = p
            elif p.node_list[-1] != end:
                paths.add(p)

    return best_solution
