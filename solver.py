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
    all_students = list(np.arange(client.k) + 1)
    ## Initiate a dictionary that stores the total number of times that the students made mistake
    mistake = np.zeros(client.k)
    ## Keep track of the nodes that must have some bots on it

    must_have = {}
    for node in guavaGraph.nodes:
        must_have[node] = 0

    cannotscout = {}
    for node in guavaGraph.nodes:
        cannotscout[node] = False


    def phaseOneO(num_iterations):
        ## Input: number of iterations for the exploration proccess
        ## Remote on each iteration; update information and knowledge about students
        nonlocal mistake, cannotscout
        for i in range(num_iterations):
            frumNode = topological_order[i]
            toNode = predecessor[frumNode]
            can_update_mistake = False
            if not cannotscout[frumNode]:
                can_update_mistake = True
                scout_result = np.array(list(client.scout(frumNode, all_students).values()))
            else:
                scout_result = np.zeros(client.k)
            if sum(scout_result)/len(scout_result) >= 0:
                remote_result = client.remote(frumNode, toNode)
                cannotscout[frumNode] = True
                if remote_result > 0:
                    cannotscout[toNode] = True
                if remote_result == 0:
                    if can_update_mistake:
                        students_correctness = (scout_result == remote_result)
                        mistake = mistake + (1 - students_correctness)
                else:
                    if can_update_mistake:
                        students_correctness = (scout_result == 1)
                        mistake = mistake + (1 - students_correctness)
                    must_have[toNode] += remote_result

    def phaseOne(num_iterations):
         ## Input: number of iterations for the exploration proccess
         ## Remote on each iteration; update information and knowledge about students
         nonlocal mistake, cannotscout
         for i in range(num_iterations):
             frumNode = topological_order[i]
             if frumNode != guavaHome:
                 toNode = predecessor[frumNode]
                 if not cannotscout[frumNode]:
                     scout_result = np.array(list(client.scout(frumNode, all_students).values()))
                 else:
                     scout_result = np.zeros(client.k)
                 if sum(scout_result)/len(scout_result) >= 0.2:
                     remote_result = client.remote(frumNode, toNode)
                     cannotscout[frumNode] = True
                     if remote_result > 0:
                         cannotscout[toNode] = True




    def phaseTwo(cutoff):
        ## Input: integer cutoff point for the confidence that the target point has a bot
        nonlocal numIterations, mistake, cannotscout
        for i in range(numIterations, len(topological_order)-1):
            currentNode = topological_order[i]
            toNode = predecessor[currentNode]
            can_update_mistake = False
            if not cannotscout[currentNode]:
                can_update_mistake = True
                scout_result = np.array(list(client.scout(currentNode, all_students).values()))
            else:
                scout_result = 0
            ## max_num = max(mistake)
            if must_have[currentNode] > 0:
                remote_result = client.remote(currentNode, toNode)
                cannotscout[currentNode] = True
                if remote_result > 0:
                    cannotscout[toNode] = True
                must_have[toNode] += remote_result
                mistake = mistake + (scout_result == False)
                pass
            else:
                weighted_authority = mistake / sum(mistake)
                if sum(scout_result * weighted_authority) >= cutoff:
                    remote_result = client.remote(currentNode, toNode)
                    if remote_result == 0:
                        if can_update_mistake:
                            students_correctness = (scout_result == remote_result)
                            mistake = mistake + (1 - students_correctness)
                    else:
                        if can_update_mistake:
                            students_correctness = (scout_result == 1)
                            mistake = mistake + (1 - students_correctness)
                        must_have[toNode] += remote_result
                        cannotscout[toNode] = True
    def phaseOne(num_iterations):
         ## Input: number of iterations for the exploration proccess
         ## Remote on each iteration; update information and knowledge about students
         nonlocal mistake, cannotscout
         for i in range(num_iterations):
             frumNode = topological_order[i]
             if frumNode != guavaHome:
                 toNode = predecessor[frumNode]
                 if not cannotscout[frumNode]:
                     scout_result = np.array(list(client.scout(frumNode, all_students).values()))
                 else:
                     scout_result = np.zeros(client.k)
                 if sum(scout_result)/len(scout_result) >= 0.2:
                     remote_result = client.remote(frumNode, toNode)
                     cannotscout[frumNode] = True
                     if remote_result > 0:
                         cannotscout[toNode] = True

    numIterations = len(topological_order)
    cutpoint = 0.4
    phaseOne(numIterations)
    client.end()
