"""
NOTE: this file is only for respect the submission exam and includes the three files functions,test,utils
"""
# library used

import os
import math
import json
import networkx as nx
import random
import itertools
from tqdm import tqdm
import time
import matplotlib.pyplot as plt

# load the data for building the graph
with open('COVID-19/dati-json/dpc-covid19-ita-province.json') as f:
    data = json.load(f)

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


""" Graph of provinces P using NetworkX
Each node corresponds to a city and two cities a and b are connected by an edge if the following holds: 
if x,y is the position of a, then b is in position z,w with z in [x-d,x+d] and w in [y-d, y+d], with d=0.8. 
The graph is symmetric. Use the latitude and longitude information available in the files to get the position 
of the cities. This task can be done in several ways. Use the one you think is more efficient.
"""
# Construct provinces graph from a json using NetworkX
def construct_provinces_graph(provinces):
    graph = nx.Graph()
    # filter reference date because in the data the provinces are repeated
    reference_date = provinces[0]['data']
    # filter data using date and 'denominazione_provincia' and remove the data that have fields
    # 'In fase di definizione/aggiornamento'
    id = 0
    for province in (provinces for provinces in data if
                     provinces['denominazione_provincia'] != 'In fase di definizione/aggiornamento'):
        if province['data'] == reference_date:
            graph.add_node(id, city=province['denominazione_provincia'], long=province['long'],
                           lat=province['lat'])
            id += 1
        else:
            break
    return graph

"""# Random Graph 
Generate 2000 pairs of double (x,y) with x in [30,50) and y in [10,20). Repeat the algorithm at step 1, building a 
graph R using NetworkX where each pair is a node and two nodes are connected with the same rule reported above, 
still with d=0.08. If the algorithm at step 1 takes too long, repeat step 1. Note that here d=0.08 
(and not 0.8 as in the previous item), as in this way the resulting graph is sparser.
"""
def construct_random_graph(nodes_num, x_inf, x_sup, y_inf, y_sup):
    graph = nx.Graph()
    for node_id in range(nodes_num):
        graph.add_node(node_id, city=str(node_id), long=random.uniform(x_inf, x_sup), lat=random.uniform(y_inf, y_sup))
    return graph


'''# add edges in the simplest way O(n^2)'''
def set_edges(graph, threshold):
    for v in graph.nodes(data=True):
        for u in (n for n in graph.nodes(data=True) if (n != v)):
            if (v[1]['long'] - threshold < u[1]['long'] < v[1]['long'] + threshold) \
                    and (v[1]['lat'] - threshold < u[1]['lat'] < v[1]['lat'] + threshold):
                graph.add_edge(v[0], u[0], a=v[1]['city'], b=u[1]['city'],
                               weight=euclidean_distance(v[1]['long'], v[1]['lat'], u[1]['long'], u[1]['lat']))
    return graph


''' add edges for reduce complexity order for latitude or longitude 
    in this case i use python sort function on longitude 
    complexity of sort is O(n log(n)) and is the most expensive in this algoritm '''
def set_edges_fast(graph, threshold):
    nodes = list(graph.nodes(data=True))
    nodes.sort(key=lambda n: n[1]['long'])  # lambda function for in-line sorting see at human computer interaction
    n_nodes = len(nodes)

    for node in range(n_nodes):
        v_id, v_attr = nodes[node]
        # Check if there must be an edge between v and the following nodes in the list
        # variable flag is used for stop the loop
        flag = False
        j = node + 1
        while j < n_nodes and not flag:
            u_id, u_attr = nodes[j]
            if abs(v_attr["long"] - u_attr["long"]) <= threshold:
                if abs(v_attr["lat"] - u_attr["lat"]) <= threshold:
                    graph.add_edge(v_id, u_id,
                                   weight=euclidean_distance(v_attr['long'], v_attr['lat'], u_attr['long'],
                                                                   u_attr['lat']))
            else:
                flag = True
            j += 1
        # Check all the edge between v and the previous nodes in the list and if a node is much distant
        # than max_distance stop the loop because subsequent nodes cannot be connected to v
        # variable flag is used for stop the loop
        flag = False
        j = node - 1
        while j > 0 and not flag:
            u_id, u_attr = nodes[j]
            if abs(v_attr["long"] - u_attr["long"]) <= threshold:
                if abs(v_attr["lat"] - u_attr["lat"]) <= threshold:
                    graph.add_edge(v_id, u_id,
                                   weight=euclidean_distance(v_attr['long'], v_attr['lat'], u_attr['long'],
                                                                   u_attr['lat']))
            else:
                flag = True
            j -= 1
        return graph




''' Clustering coefficient calculation function '''
# O(V + E^2) the complexity is without intersection of list
# O(V + list intersection)
def clustering_coefficient(graph, intersection=False):
    clustering_coefficient_list = {}
    sum = 0
    for node in graph.nodes()(data=True):
        neighbours = [n for n in nx.neighbors(graph, node[0])]
        num_neighbours = len(neighbours)
        num_edge = 0
        if num_neighbours > 1:
            if intersection == False:
                for node1 in neighbours:
                    for node2 in neighbours:
                        if graph.has_edge(node1, node2):
                            num_edge += 1
                # the number of edge is /2 because we count the edge from node a to b and the same edge to note b to a
                # this is the number of triangles in explicit way
                coeff = (num_edge / 2) / ((num_neighbours * (num_neighbours - 1)) / 2)
                sum += coeff
                clustering_coefficient_list[node[1]['city']] = coeff
            # if i use list intersection i count the number of triangles in implicit way
            if intersection == True:
                num_triangles = 0
                for u in neighbours:
                    u_neighbors = list(graph.neighbors(u))
                    list_intersection = list_intersection(neighbours, u_neighbors)
                    num_triangles += len(list_intersection)
                coeff = num_triangles / (num_neighbours * (num_neighbours - 1))
                sum += coeff
                clustering_coefficient_list[node[1]['city']] = coeff
        else:
            clustering_coefficient_list[node[1]['city']] = 0
    return clustering_coefficient_list, sum / graph.number_of_nodes()  # return the list of coefficient and the average


'''
Choose any starting vertex v, and follow a trail of edges from that vertex until returning to v. It is not possible
 to get stuck at any vertex other than v, because the even degree of all vertices ensures that, when the trail enters 
 another vertex w there must be an unused edge leaving w. The tour formed in this way is a closed tour, but may not 
 cover all the vertices and edges of the initial graph.
As long as there exists a vertex u that belongs to the current tour but that has adjacent edges not part of the tour, 
start another trail from u, following unused edges until returning to u, and join the tour formed in this way to the
 previous tour.
Since we assume the original graph is connected, repeating the previous step will exhaust all edges of the graph.
'''
# O(E)
def hierholzer(graph):
    nodes = list(graph.nodes())
    # Check if the graph has an Euler circuit: All vertices have even degrees.
    for node in graph:
        neighbors = list(graph.neighbors(node))
        if len(neighbors) % 2 == 1:
            return "The graph is not eulerian"
    # save the neighbours maybe can save time?????
    # Create necessary data structures.
    # print(nodes[0])
    start = nodes[0]  # choose the start vertex to be the first vertex in the graph
    circuit = [start]  # can use a linked list for better performance here
    traversed = {}
    ptr = 0
    while len(traversed) // 2 < len(graph.edges()) and ptr < len(circuit):
        subpath = []  # vertices on subpath
        dfs(graph, circuit[ptr], circuit[ptr], subpath, traversed)
        if len(subpath) != 0:  # insert subpath vertices into circuit
            circuit = list(itertools.chain(circuit[:ptr + 1], subpath, circuit[ptr + 1:]))
        ptr += 1

    return circuit


""" Dfs on vertex u until get back to u. The argument vertices is a list and
    contains the vertices traversed. If all adjacent edges of starting vertex
    are already traversed, 'vertices' is empty after the call.
    """
def dfs(graph, u, root, subpath, traversed):
    for v in graph.neighbors(u):
        if (u, v) not in traversed or (v, u) not in traversed:
            traversed[(u, v)] = traversed[(v, u)] = True
            subpath.append(v)
            if v == root:
                return
            else:
                dfs(graph, v, root, subpath, traversed)


"""
An Eulerian trail, or Euler walk in an undirected graph is a walk that uses each edge exactly once.
If such a walk exists, the graph is called traversable or semi-eulerian.
An Eulerian cycle, Eulerian circuit or Euler tour in an undirected graph is a cycle that uses each edge exactly once. 
If such a cycle exists, the graph is called Eulerian or unicursal.The term "Eulerian graph" is also sometimes used 
in a weaker sense to denote a graph where every vertex has even degree. For finite connected graphs the two 
definitions are equivalent, while a possibly unconnected graph is Eulerian in the weaker sense if and only if each 
connected component has an Eulerian cycle.
"""



if __name__ == '__main__':
    plot_graph_P_R = False
    """# little test for data manipulation and see how the data are displayed"""
    provinces = []
    for i in range(len(data)):
        provinces.append([data[i].get("denominazione_provincia"), data[i].get("lat"), data[i].get("long")])
    #print(provinces)

    """ Performance test for generation of graph (average of num_test)"""
    num_test = 1
    time_p_slow = 0
    time_p_fast = 0
    time_r_slow = 0
    time_r_fast = 0
    for i in tqdm(range(num_test)):
        ''' fastest version for graph creation'''
        start = time.time()
        P = set_edges_fast(construct_provinces_graph(data), 0.8)
        end = time.time()
        time_p_fast += (end - start)
        start = time.time()
        R = set_edges_fast(construct_random_graph(2000, 30, 49, 10, 19), 0.08)
        end = time.time()
        time_r_fast += (end - start)
        ''' slowest version for graph creation'''
        start = time.time()
        P = set_edges(construct_provinces_graph(data), 0.8)
        end = time.time()
        time_p_slow += (end - start)
        start = time.time()
        R = set_edges(construct_random_graph(2000, 30, 49, 10, 19), 0.08)
        end = time.time()
        time_r_slow += (end - start)

    print("Time for graph generation")
    print("Slow generetion P: ", time_p_slow / num_test, " R: ", time_r_slow / num_test)
    print("Fast generetion P: ", time_p_fast / num_test, " R: ", time_r_fast / num_test)

    ''' Plot of two graph only with the last graph generated '''
    if plot_graph_P_R:
        plot_graph(P, name="graph_P", layout="spring", path="img/")
        plot_graph(R, name="graph_R", layout="random", path="img/")

    ''' TEST ON A SIMPLE TOY '''
    print("\nHierholzer eulerian path test on toy example")
    toy = nx.Graph()
    toy.add_nodes_from(['A', 'B', 'C', 'D', 'E'])  # graph with 2 triangles
    toy.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D'), ('C', 'E'), ('D', 'E')])
    print(nx.is_eulerian(toy), nx.has_eulerian_path(toy))
    print(hierholzer(toy))
    ''' Eulerian Path test i made the test on R and on a toy example because eulerian path on graph of provinces 
    dosen't exist because the graph of provinces in not strongly connected'''
    time_eulerian = []
    time_eulerian_nx = []
    num_node = [3, 9, 19, 29, 39, 49]
    for test in range(len(num_node)):
        toy = nx.complete_graph(num_node[test])
        toy = nx.eulerize(toy)
        # print(nx.is_eulerian(toy))
        # print(nx.has_eulerian_path(toy))
        # print(nx.has_eulerian_path(R))
        # print(nx.has_eulerian_path(P))
        '''EULERIAN PATH ON A TOY EXAMPLE USING NETWORKX'''
        start = time.time()
        path = nx.eulerian_path(toy)
        # print(list(path))
        end = time.time()
        time_eulerian_nx.append(end - start)
        '''EULERIAN PATH ON A TOY EXAMPLE USING IMPLEMENTED FUNCTIONS'''
        start = time.time()
        path = hierholzer(toy)
        # print(path)
        end = time.time()
        time_eulerian.append(end - start)

    print("\nTime for calculate eulerian path")
    print("Number of graph vertex", num_node)
    print("Using NetworkX Function on Toy example: ", time_eulerian_nx)
    print("Using simple implementation on Toy example: ", time_eulerian)
    plt.plot(num_node, time_eulerian, label='Implemented')
    plt.plot(num_node, time_eulerian_nx, ls='-.', label='NetworkX')
    plt.xlabel('Number of graph vertex')
    plt.ylabel('Time')
    plt.title('Eulerian path')
    plt.legend()
    plt.show()

    """ Clustering Coefficent test is mede on the last pair of P and R """
    start = time.time()
    print("\nCLUSTERING COEFFICIENT USING NX FUNCTION FOR P AND R")
    print("For each node in provinces graph: ", nx.clustering(P))
    print("Average: ", nx.average_clustering(P))
    end = time.time()
    time_cluster_networkx_P = (end - start)
    start = time.time()
    print("For each node in random graph: ", nx.clustering(R))
    print("Average: ", nx.average_clustering(R))
    end = time.time()
    time_cluster_networkx_R = (end - start)
    start = time.time()
    print("\nCLUSTERING COEFFICIENT USING SIMPLE IMPLEMENTED FUNCTION ")
    clustering_coefficient_P, avg_P = clustering_coefficient(P)
    print("For each node in provinces graph: ", clustering_coefficient_P)
    print("Average: ", avg_P)
    end = time.time()
    time_cluster_simple_P = (end - start)
    start = time.time()
    clustering_coefficient_R, avg_R = clustering_coefficient(R)
    print("For each node in random graph: ", clustering_coefficient_R)
    print("Average: ", avg_R)
    end = time.time()
    time_cluster_simple_R = (end - start)
    start = time.time()
    print("\nCLUSTERING COEFFICIENT USING IMPLEMENTED FUNCTION WITH LIST INTERSECTION")
    clustering_coefficient_intersection_P, avg_intersection_P = clustering_coefficient(P, intersection=True)
    print("For each node in provinces graph: ", clustering_coefficient_intersection_P)
    print("Average: ", avg_intersection_P)
    end = time.time()
    time_cluster_intersect_P = (end - start)
    start = time.time()
    clustering_coefficient_intersection_R, avg_intersection_R = clustering_coefficient(R, intersection=True)
    print("For each node in random graph: ", clustering_coefficient_intersection_R)
    print("Average: ", avg_intersection_R)
    end = time.time()
    time_cluster_intersectR = (end - start)

    print("\nTime for calculate clustering coefficient")
    print("The time is referred to the calculation of clusering coefficient on P and R")
    print("Using NetworkX Function on P: ", time_cluster_networkx_P , " on R: ",
          time_cluster_networkx_R)
    print("Using simple implementation on P: ", time_cluster_simple_P, " on R: ",
          time_cluster_simple_R)
    print("Using list intersect implementation on P: ", time_cluster_intersect_P, " on R: ",
          time_cluster_simple_R)


