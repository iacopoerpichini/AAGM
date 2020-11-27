# library used
import json
import networkx as nx
import random
import utils
import itertools

# load the data for building the graph
with open('COVID-19/dati-json/dpc-covid19-ita-province.json') as f:
    data = json.load(f)

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
                               weight=utils.euclidean_distance(v[1]['long'], v[1]['lat'], u[1]['long'], u[1]['lat']))
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
                                   weight=utils.euclidean_distance(v_attr['long'], v_attr['lat'], u_attr['long'],
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
                                   weight=utils.euclidean_distance(v_attr['long'], v_attr['lat'], u_attr['long'],
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
                    list_intersection = utils.list_intersection(neighbours, u_neighbors)
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
# Eulerian Path here i see the networkx implementation for understanding how is made
# def has_eulerian_path(G):
#     """Return True iff `G` has an Eulerian path.
#
#     An Eulerian path is a path in a graph which uses each edge of a graph
#     exactly once.
#
#     A directed graph has an Eulerian path iff:
#         - at most one vertex has out_degree - in_degree = 1,
#         - at most one vertex has in_degree - out_degree = 1,
#         - every other vertex has equal in_degree and out_degree,
#         - and all of its vertices with nonzero degree belong to a
#         - single connected component of the underlying undirected graph.
#
#     An undirected graph has an Eulerian path iff:
#         - exactly zero or two vertices have odd degree,
#         - and all of its vertices with nonzero degree belong to a
#         - single connected component.
#
#     Parameters
#     ----------
#     G : NetworkX Graph
#         The graph to find an euler path in.
#
#     Returns
#     -------
#     Bool : True if G has an eulerian path.
#
#     See Also
#     --------
#     is_eulerian
#     eulerian_path
#     """
#     if G.is_directed():
#         ins = G.in_degree
#         outs = G.out_degree
#         semibalanced_ins = sum(ins(v) - outs(v) == 1 for v in G)
#         semibalanced_outs = sum(outs(v) - ins(v) == 1 for v in G)
#         return (semibalanced_ins <= 1 and
#                 semibalanced_outs <= 1 and
#                 sum(G.in_degree(v) != G.out_degree(v) for v in G) <= 2 and
#                 nx.is_weakly_connected(G))
#     else:
#         return (sum(d % 2 == 1 for v, d in G.degree()) in (0, 2)
#                 and nx.is_connected(G))
#
#
# def is_eulerian(G):
#     """Returns True if and only if `G` is Eulerian.
#
#     A graph is *Eulerian* if it has an Eulerian circuit. An *Eulerian
#     circuit* is a closed walk that includes each edge of a graph exactly
#     once.
#
#     Parameters
#     ----------
#     G : NetworkX graph
#        A graph, either directed or undirected.
#
#     Examples
#     --------
#     >>> nx.is_eulerian(nx.DiGraph({0: [3], 1: [2], 2: [3], 3: [0, 1]}))
#     True
#     >>> nx.is_eulerian(nx.complete_graph(5))
#     True
#     >>> nx.is_eulerian(nx.petersen_graph())
#     False
#
#     Notes
#     -----
#     If the graph is not connected (or not strongly connected, for
#     directed graphs), this function returns False.
#
#     """
#     if G.is_directed():
#         # Every node must have equal in degree and out degree and the
#         # graph must be strongly connected
#         return (all(G.in_degree(n) == G.out_degree(n) for n in G) and
#                 nx.is_strongly_connected(G))
#     # An undirected Eulerian graph has no vertices of odd degree and
#     # must be connected.
#     return all(d % 2 == 0 for v, d in G.degree()) and nx.is_connected(G)
#
#
# def is_semieulerian(G):
#     """Return True iff `G` is semi-Eulerian.
#
#     G is semi-Eulerian if it has an Eulerian path but no Eulerian circuit.
#     """
#     return has_eulerian_path(G) and not is_eulerian(G)
#
#
# def eulerize(G):
#     """Transforms a graph into an Eulerian graph
#
#     Parameters
#     ----------
#     G : NetworkX graph
#        An undirected graph
#
#     Returns
#     -------
#     G : NetworkX multigraph
#
#     Raises
#     ------
#     NetworkXError
#        If the graph is not connected.
#
#     See Also
#     --------
#     is_eulerian
#     eulerian_circuit
#
#     References
#     ----------
#     .. [1] J. Edmonds, E. L. Johnson.
#        Matching, Euler tours and the Chinese postman.
#        Mathematical programming, Volume 5, Issue 1 (1973), 111-114.
#        [2] https://en.wikipedia.org/wiki/Eulerian_path
#     .. [3] http://web.math.princeton.edu/math_alive/5/Notes1.pdf
#
#     Examples
#     --------
#         >>> G = nx.complete_graph(10)
#         >>> H = nx.eulerize(G)
#         >>> nx.is_eulerian(H)
#         True
#
#     """
#     if G.order() == 0:
#         raise nx.NetworkXPointlessConcept("Cannot Eulerize null graph")
#     if not nx.is_connected(G):
#         raise nx.NetworkXError("G is not connected")
#     odd_degree_nodes = [n for n, d in G.degree() if d % 2 == 1]
#     G = nx.MultiGraph(G)
#     if len(odd_degree_nodes) == 0:
#         return G
#
#     # get all shortest paths between vertices of odd degree
#     odd_deg_pairs_paths = [(m,
#                             {n: nx.shortest_path(G, source=m, target=n)}
#                             )
#                            for m, n in combinations(odd_degree_nodes, 2)]
#
#     # use inverse path lengths as edge-weights in a new graph
#     # store the paths in the graph for easy indexing later
#     Gp = nx.Graph()
#     for n, Ps in odd_deg_pairs_paths:
#         for m, P in Ps.items():
#             if n != m:
#                 Gp.add_edge(m, n, weight=1 / len(P), path=P)
#
#     # find the minimum weight matching of edges in the weighted graph
#     best_matching = nx.Graph(list(nx.max_weight_matching(Gp)))
#
#     # duplicate each edge along each path in the set of paths in Gp
#     for m, n in best_matching.edges():
#         path = Gp[m][n]["path"]
#         G.add_edges_from(nx.utils.pairwise(path))
#     return G
#
# # ok i have used the libraries
# P_euler = eulerize(P_edge)
# print(has_eulerian_path(P_euler))
# print(is_eulerian(P_euler))
# print(is_semieulerian(P_euler))
