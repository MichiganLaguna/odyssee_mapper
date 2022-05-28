""" Implementation of dijkstra algorithm in python"""
from collections import defaultdict

MAX_VALUE = 999


def build_graph(edges: list[list]) -> dict[str, dict[str, int]]:
    """Function to build a graph of adjency from a list of edges
    with the graph in this form : {'A':{'B', lenght},..."""
    graph = defaultdict(dict)

    # Loop to iterate over every edge of the graph
    for edge in edges:
        first_edge, second_edge, lenght = edge[0], edge[1], edge[2]

        # Creating the graph as adjacency list
        graph[first_edge][second_edge] = int(lenght)
    return graph


def init_(edges: list[list], starting_node: str) -> dict[str, int]:
    """Function to initialise a dictionary of distance
    between the starting node and every other node from the graph"""
    dist = {}
    for node in edges:
        dist[node[0]] = MAX_VALUE
        dist[node[1]] = MAX_VALUE
    dist[starting_node] = 0
    return dist


def find_min_(nodes: list[str], dist: dict[str, int]) -> str:
    """Function to find the nearest node from the starting node in a list of remaining nodes"""
    minimum = MAX_VALUE
    sommet = None
    for node in nodes:
        if dist[node] < minimum:
            minimum = dist[node]
            sommet = node
    return sommet


def maj_dist_(
    node_1: str,
    node_2: str,
    graph: list[str],
    dist: dict[str, int],
    precedent: dict[str, str],
) -> dict[str, str]:
    """Function wich update the distance of a node to the starting node
    and return a dictionary of nodes and their precedent node."""

    if dist[node_2] > dist[node_1] + graph[node_1][node_2]:
        dist[node_2] = dist[node_1] + graph[node_1][node_2]
        precedent[node_2] = node_1
    return precedent


def dijkstra(
    graph: dict[str, dict[str, int]], start: str, edges: list[list]
) -> list[dict[str, int], dict[str, str]]:
    """Function wich implement the algorithm of dijkstra"""
    precedent = {}
    nodes = list(graph.keys())
    dist = init_(edges, start)
    while nodes:
        node_1 = find_min_(nodes, dist)
        if node_1 is not None:
            nodes.remove(node_1)
            for node_2 in graph[node_1]:
                precedent = maj_dist_(node_1, node_2, graph, dist, precedent)
        else:
            break
    return [dist, precedent]


def find_shortest_path(start: str, end: str, precedent: list[str, str]) -> list[str]:
    """Function to find the shortest path between two points and return none if they are no path"""
    shortest_path = []
    head = end
    while head != start:
        shortest_path.append(head)
        try:
            head = precedent[head]
        except KeyError:
            return None
    shortest_path.append(start)
    return shortest_path
