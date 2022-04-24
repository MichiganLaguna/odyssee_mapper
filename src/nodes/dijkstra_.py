# %%
from collections import defaultdict

# MAX_VALUE is the maximum distance between the start and the end of two nodes
MAX_VALUE = 999 

# %%
#Function to build a graph of adjency from a list of edges with the graph in this form : {'A':{'B', lenght},...
def build_graph(edges):
    graph = defaultdict(dict)

    #Loop to iterate over every edge of the graph
    for edge in edges:
        a, b, lenght = edge[0], edge[1], edge[2]

        #Creating the graph as adjacency list
        graph[a][b] = int(lenght)
        graph[b][a] = int(lenght)
    return graph

# %%
#Function to initialise a dictionary of distance between the starting node and every other node from the graph
def init_(graph, start):
    dist = dict()
    for s in graph:
        dist[s] = MAX_VALUE
    dist[start] = 0
    return dist

# %%
#Function to find the nearest node from the starting node in a list of remaining nodes
def find_min_(nodes, dist):
    min = MAX_VALUE
    sommet = None
    for s in nodes:
        if dist[s] < min:
            min = dist[s]
            sommet = s
    return sommet

# %%
#Function wich update the distance of a node to the starting node and return a dictionary of nodes and their precedent node.
def maj_dist_(s1, s2, graph, dist, precedent):
    if dist[s2] > dist[s1] + graph[s1][s2] :
        dist[s2] = dist[s1] + graph[s1][s2]
        precedent[s2] = s1
    return precedent

# %%
#Function wich implement the algorithm of dijkstra
def dijkstra(graph, start):
    precedent = dict()
    nodes = list(graph.keys())
    dist = init_(nodes, start)
    while nodes:
        s1 = find_min_(nodes, dist)
        if s1 is not None:
            nodes.remove(s1)
            for s2 in graph[s1]:
                precedent = maj_dist_(s1,s2, graph, dist, precedent)
        else:
            break
    return [dist, precedent]
# %%
#Function to find the shortest path between two points and return none if they are no path
def find_shortest_path(start, end, precedent):
    shortest_path = []
    s = end
    while s != start:
        shortest_path.append(s)
        try:
            s = precedent[s]
        except KeyError:
            return None
    shortest_path.append(start)
    return shortest_path