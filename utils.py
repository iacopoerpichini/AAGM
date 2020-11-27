import matplotlib.pyplot as plt
import os
import math
import networkx as nx

# Euclidean distance used for calculate the distance with longitude and latitude
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

# Used for plot with networkx
def plot_graph(graph, name, layout, path):
    pos = nx.layout.spring_layout(graph)
    if layout == "spring":
        pos = nx.layout.spring_layout(graph)
    elif layout == "random":
        pos = nx.layout.random_layout(graph)
    plt.subplots(1, 1, figsize=(10, 10))
    nx.draw_networkx_nodes(graph, pos, node_size=20, node_color="#ff0000", alpha=0.8)
    nx.draw_networkx_edges(graph, pos, edge_color="#0000ff", width=2)
    plt.axis('off')
    plt.savefig(os.path.join(path, name + ".png"))

# intersect of two list see at lection
def list_intersection(list_1, list_2):
    intersection = []
    list_1, list_2 = sorted(list_1), sorted(list_2)
    i, j = 0, 0
    while i < len(list_1) and j < len(list_2):
        if list_1[i] < list_2[j]:
            i += 1
        elif list_1[i] > list_2[j]:
            j += 1
        else:
            intersection.append(list_1[i])
            i += 1
            j += 1
    return intersection
