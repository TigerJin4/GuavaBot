# Put your solution here.
import networkx as nx
import numpy as np
import random
from sortedcontainers import SortedDict
import math
def solve(client):
    client.end()
    client.start()
    ##Getting the networkx graph instance for the city
    guavaGraph = client.G
    ##Getting the homenode for the city
    guavaHome = client.home
    ##Getting the nodes list of the city
    mst = nx.minimum_spanning_tree(guavaGraph)
    mst_leaves = []
    for node in mst.nodes():
        if len(list(mst.neighbors(node))) == 1:
            mst_leaves += [node]

    predecessor = nx.dfs_predecessors(mst, guavaHome)
    topological_order = list(nx.dfs_postorder_nodes(mst, guavaHome))
    all_students = list(np.arange(client.k)+1)
    ## Initiate a dictionary that stores the total number of times that the students made mistake
    mistake = {}
    for student in all_students:
        mistake[student] = 1

    ## Keep track of the nodes that must have some bots on it
    must_have = {}
    for node in guavaGraph.nodes:
        must_have[node] = 0

    ## Number of bots:
    num_bots = client.l


    ##Overall scout results:
    overall_results = {}

    cannotscout = {}
    for node in guavaGraph.nodes:
        cannotscout[node] = False

    explored = {}
    for node in guavaGraph.nodes():
        explored[node] = False


    stop_scouting = False

    total_vert = len(guavaGraph.nodes())


    def scout_nodes(nodes, students):
        '''
        :param nodes: A list of nodes that the students scout on
        :param students: A list of students to perform the scout task
        :return: None
        '''
        nonlocal overall_results, stop_scouting
        if not client.k == sum(client.bot_count):
            for node in nodes:
                overall_results[node]= client.scout(node, students)
    confid = []
    def calculate_confidence(theNode):
        '''
        :param scoutResults: A dictionary of scouting results; key: student; value:result
        :param mistakeDict: An array of students' mistake count; indexed by student - 1
        :return: a float in [0,1] that indicates the weighted confidence in that the current node has bot
        '''
        nonlocal overall_results, mistake, confid
        weighted_confidence = 0
        current_node_result = overall_results[theNode]
        total_weights = sum(np.array([mistake[s] for s in list(current_node_result.keys())]))
        for s in list(current_node_result.keys()):
            weighted_confidence += current_node_result[s] * mistake[s] / total_weights
        confid += [weighted_confidence]
        return weighted_confidence

    def remote_and_update(fromNode, toNode, epsilon):
        '''
        :param fromNode: node to perform remote from
        :param toNode: node to perform remote to
        :return:
        '''
        nonlocal mistake, cannotscout, overall_results, stop_scouting, must_have, num_bots, explored
        remote_result = client.remote(fromNode, toNode)
        explored[fromNode] = True
        cannotscout[fromNode] = True
        if remote_result > 0:
            cannotscout[toNode] = True
            must_have[toNode] += remote_result
            must_have[fromNode] = 0


        if fromNode in list(overall_results.keys()):
            expectedAnswer = (remote_result > 0)
            updateResults = overall_results[fromNode]
            for student in list(updateResults.keys()):
                if updateResults[student] == expectedAnswer:
                    mistake[student] *= (1 - epsilon)

    def exploration(degree, eps):
        '''
        :param degree: the degree of exploration process (percentage)
        :return: None
        '''
        nonlocal mst_leaves, all_students, predecessor, guavaGraph, all_students, guavaHome, explored
        leaves_weights = {}
        for i in range(len(mst_leaves)):
            leaf = mst_leaves[i]
            if leaf in list(predecessor.keys()):
                pred = predecessor[leaf]
                current_weight = guavaGraph[leaf][pred]['weight']
                if current_weight in list(leaves_weights.keys()):
                    leaves_weights[current_weight] += [leaf]
                else:
                    leaves_weights[current_weight] = [leaf]

        sorted_leaves_weights = SortedDict(leaves_weights)
        nodes_oredered = []
        for key in sorted_leaves_weights.keys():
            nodes_oredered += sorted_leaves_weights[key]
        print(nodes_oredered)
        for i in range(degree):
            currentNode = nodes_oredered[i]
            if currentNode in list(predecessor.keys()):
                toNode = predecessor[currentNode]
                if not cannotscout[currentNode]:
                    scout_nodes([currentNode], all_students)
                remote_and_update(currentNode, toNode, eps)

    confid_2 = {}
    def exploitation(prop_cutoff, confidence_cutoff,epsil):
        print('into exploitation')
        decision_maker = []
        nonlocal overall_results, topological_order, explored, guavaHome
        nonlocal guavaGraph, predecessor, mistake, total_vert, explored
        nonlocal all_students, confid_2
        pass_count = 0
        for i in range(len(topological_order) - 1):
            # Pass if explored already
            currentNode = topological_order[i]
            if explored[currentNode]:
                continue

            toNode = predecessor[currentNode]

            # Remote for sure if there are known bots on the current node
            if client.bot_count[currentNode]:
                remote_and_update(currentNode, toNode, epsil)
                continue
            if client.bot_count[currentNode] == 0:
                if client.l == sum(np.array(client.bot_count)):
                    continue


            discovered_prop = sum(np.array(client.bot_count)) / client.l
            max_weight = max(np.array(list(mistake.values())))
            min_weight = min(np.array(list(mistake.values())))

            # Trust the result of students whose mistake result range is in
            # [max - (1 - discovered_prop)*total_total_vertices, max]
            #if discovered_prop <= prop_cutoff:
            #    students_to_scout = all_students
            #else:
            #mistake_lower_bound = max_weight - 0.1 * (1 + discovered_prop ** 5)
            #mistake_lower_bound = 0
            #students_to_scout = [s for s in all_students if mistake[s] >= mistake_lower_bound or mistake[s] - min_weight <  0.8 * (1 + discovered_prop ** 5)]
            percent75 = np.percentile(np.array(list(mistake.values())), 50)
            students_to_scout = []
            for stu in all_students:
                if mistake[stu] >= percent75:
                    students_to_scout += [stu]
            scout_nodes([currentNode], students_to_scout)
            decision_maker += [len(students_to_scout)]

            my_confidence = calculate_confidence(currentNode)
            #if discovered_prop <= prop_cutoff:
            #    if my_confidence >= confidence_cutoff:
            #        remote_and_update(currentNode, toNode, epsil)
            #    else:
            #        pass_count += 1
            #        confid_2 += my_confidence
            #else:
            if my_confidence >= confidence_cutoff:
                remote_and_update(currentNode, toNode, epsil)
            #   confid_2[currentNode] = [my_confidence, client.bot_count[toNode]]

            elif discovered_prop < 0.8 and my_confidence >= confidence_cutoff * 0.9:
                remote_and_update(currentNode, toNode, epsil)
            #    confid_2[currentNode] = [my_confidence, client.bot_count[toNode]]
            else:
                pass_count += 1


        print(pass_count)
        print(decision_maker)












    #numIterations = len(topological_order) // 10
    #cutpoint = 0.4
    #phaseOne(numIterations)
    #phaseTwo(cutpoint)
    epsilo = 0.01
    deg = math.floor(len(mst_leaves) * 0.1)
    exploration(deg, epsilo)
    cut_o = 0.40

    exploitation(0.4, cut_o, epsilo)
    print(confid)
    client.end()
