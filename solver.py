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
    mst = nx.minimum_spanning_tree(guavaGraph)
    predecessor = nx.dfs_predecessors(mst, guavaHome)
    topological_order = list(nx.dfs_postorder_nodes(mst, guavaHome))
    all_students = list(np.arange(client.k)+1)
    ## Initiate a dictionary that stores the total number of times that the students made mistake
    mistake = np.zeros(client.k)
    ## Keep track of the nodes that must have some bots on it

    must_have = {}
    for node in guavaGraph.nodes:
        must_have[node] = 0

    cannotscout = {}
    for node in guavaGraph.nodes:
        cannotscout[node] = False


    def phaseOne(num_iterations):
        ## Input: number of iterations for the exploration proccess
        ## Remote on each iteration; update information and knowledge about students
        nonlocal mistake, cannotscout
        for i in range(num_iterations):
            frumNode = topological_order[i]
            toNode = predecessor[frumNode]
            if cannotscout[frumNode]:
                pass
            scout_result = np.array(list(client.scout(frumNode, all_students).values()))
            remote_result = client.remote(frumNode, toNode)
            cannotscout[frumNode] = True
            cannotscout[toNode] = True
            print('scout result is', scout_result)
            if remote_result == 0:
                students_correctness = (scout_result == remote_result)
                mistake = mistake + (1 - students_correctness)
            else:
                students_correctness = (scout_result == 1)
                mistake = mistake + (1 - students_correctness)
                must_have[toNode] += remote_result

    def phaseTwo(cutoff):
        ## Input: integer cutoff point for the confidence that the target point has a bot
        nonlocal numIterations, mistake, cannotscout
        for i in range(numIterations, len(topological_order)):
            currentNode = topological_order[i]
            toNode = predecessor[currentNode]
            if cannotscout[currentNode]:
                pass
            scout_result = np.array(list(client.scout(currentNode, all_students).values()))
            ## max_num = max(mistake)
            if must_have[currentNode] > 0:
                remote_result = client.remote(currentNode, toNode)
                cannotscout[currentNode] = True
                cannotscout[toNode] = True
                must_have[toNode] += remote_result
                mistake = mistake + (scout_result == False)
                pass
            else:
                weighted_authority = mistake / sum(mistake)
                if sum(scout_result * weighted_authority) >= cutoff:
                    remote_result = client.remote(currentNode, toNode)
                    if remote_result == 0:
                        students_correctness = (scout_result == remote_result)
                        mistake = mistake + (1 - students_correctness)
                    else:
                        students_correctness = (scout_result == 1)
                        mistake = mistake + (1 - students_correctness)
                        must_have[toNode] += remote_result

    numIterations = len(topological_order) // 2
    cutpoint = 0.5
    phaseOne(numIterations)
    phaseTwo(cutpoint)
    client.end()
