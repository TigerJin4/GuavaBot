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
    all_students = client.k
    ## Initiate a dictionary that stores the total number of times that the students made mistake
    mistake = np.zeros(len(all_students))
    ## Keep track of the nodes that must have some bots on it

    must_have = {}
    for node in guavaGraph.nodes:
        must_have[node] = 0

    num_Nodes_examined = -1
    def phaseOne(num_iterations):
        ## Input: number of iterations for the exploration proccess
        ## Remote on each iteration; update information and knowledge about students
        for i in range(num_iterations):
            num_Nodes_examined += 1
            frumNode = topological_order[i]
            toNode = predecessor[frumNode]
            ##A list of boolean values: the students' prediction on whether the "frumNode" has bots
            scout_result = np.array(client.scout(frumNode, all_students))
            remote_result = client.remote(frumNode, toNode)
            if remote_result == 0:
                students_correctness = (scout_result == remote_result)
                mistake = mistake + (1 - students_correctness)
            else:
                students_correctness = (scout_result == 1)
                mistake = mistake + (1 - students_correctness)
                must_have[toNode] += remote_result

    def phaseTwo(cutoff):
        ## Input: cutoff point for the confidence that the target point has a bot
        for i in range(num_Nodes_examined, len(topological_order)):
            currentNode = topological_order[i]
            toNode = predecessor[currentNode]
            scout_result = np.array(client.scout(currentNode, all_students))
            max_num = max(mistake)
            if must_have[currentNode] > 0:
                remote_result = client.remote(currentNode, toNode)
                must_have[toNode] += remote_result
                mistake = mistake + (remote_result == False)
                continue
            else:
                weighted_authority = mistake / sum(mistake)
                 























    client.end()
