from tqdm import tqdm
import time
from functions import *
import matplotlib.pyplot as plt


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
        utils.plot_graph(P, name="graph_P", layout="spring", path="img/")
        utils.plot_graph(R, name="graph_R", layout="random", path="img/")

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
    # plt.plot(num_node, time_eulerian_nx, ls='-.', label='NetworkX')
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