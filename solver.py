# Put your solution here.
import networkx as nx
import numpy as np
import random



def solve(client):
    client.end()
    client.start()
    ##Getting the networkx graph instance for the city
    guavaGraph = client.G
    ##Getting the homenode for the city
    guavaHome = client.h
    ##Getting the nodes list of the city
    guavaNodes = client.n
    mst = nx.minimum_spanning_tree(guavaGraph)
    predecessor = nx.dfs_predecessors(mst, guavaHome)
    topological_order = list(nx.dfs_postorder_nodes(mst, guavaHome))
    ## Initiate a dictionary that stores the total number of times that the students made mistake
    all_students = client.k

    mistake = np.zeros(len(all_students))


    def phaseOne(num_iterations):
        for i in range(num_iterations):
            frumNode = topological_order[i]
            toNode = predecessor[frumNode]
            ##A list of boolean values: the students' prediction on whether the "frumNode" has bots
            scout_result = np.array(client.scout(frumNode, all_students))
            remote_result = client.remote(frumNode, toNode)
            students_correctness = ((scout_result - remote_result) == 0)
            mistake = mistake + (1 - students_correctness)
            














    client.end()
