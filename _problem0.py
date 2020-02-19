import os.path as opath
import os
import json
from random import random, seed, sample, choice, randint
from itertools import chain
#
from __path_organizer import exp_dpath
from Krushal_minSpanningTree import get_minSpanningTree, get_minSpanningTree_givenBone

FLOAT_PRECISION = 1e2
DEFAULT_REWARD, DEFAULT_VOLUME, DEFAULT_WEIGHT = 1, 1, 1
DEFAULT_TW_BEGIN, DEFAULT_TW_END = 0, FLOAT_PRECISION * 1e6


class Problem(object):
    def __init__(self,
                 problemName,
                 reward, volume, weight,
                 numWH, whAllocation,
                 distance, timeWindow,
                 caVol, caWei, detourLimit):
        self.problemName = problemName
        self.K = list(range(len(reward)))
        self.P, self.D, self.PD = set(), set(), set()
        self.r_k, self.v_k, self.w_k = [None for _ in self.K], [None for _ in self.K], [None for _ in self.K]
        self.h_k, self.n_k = [None for _ in self.K], [None for _ in self.K]
        for k in self.K:
            self.r_k[k] = reward[k]
            self.v_k[k] = volume[k]
            self.w_k[k] = weight[k]
            self.h_k[k] = whAllocation[k]
            self.n_k[k] = 1 + numWH + k
            self.P.add(self.h_k[k])
            self.D.add(self.n_k[k])
        self.PD = self.P.union(self.D)
        self.o, self.d = 0, numWH + len(self.D) + 1
        self.S = [self.o]
        for i in range(self.d + 1, len(distance)):
            self.S.append(i)
        self.S.append(self.d)
        self.N = []
        for i in self.PD:
            self.N.append(i)
        for i in self.S:
            self.N.append(i)
        self.N.sort()
        self.t_ij = [[0.0] * len(distance) for _ in distance]
        self.al_i, self.be_i = [-1 for _ in distance], [-1 for _ in distance]
        for i in self.N:
            for j in self.N:
                self.t_ij[i][j] = distance[i][j]
            self.al_i[i], self.be_i[i] = timeWindow[i]
        self.c_ij = [[0] * len(distance) for _ in distance]
        for i in range(len(self.S)):
            for j in range(len(self.S)):            
                if j < i:
                    continue
                self.c_ij[self.S[i]][self.S[j]] = 1
                self.c_ij[self.S[j]][self.S[i]] = 0
        self.M = max(1.0,
                 len(self.N) * len(self.N) * max(chain(*[self.t_ij[i] for i in self.N])))
        self.bv, self.bw, self.bu = caVol, caWei, detourLimit

    def write_json(self, dpath):
        prob = {'problemName': self.problemName,
                'K': self.K,  'P': list(self.P),  'D': list(self.D),  'PD': list(self.PD),
                'r_k': self.r_k, 'v_k': self.v_k, 'w_k': self.w_k,
                'h_k': self.h_k, 'n_k': self.n_k,
                'o': self.o, 'd': self.d,
                'S': self.S, 'N': self.N,
                't_ij': self.t_ij,
                'al_i': self.al_i, 'be_i': self.be_i,
                'c_ij': self.c_ij,
                'M': self.M,
                'bv': self.bv, 'bw': self.bw, 'bu': self.bu
                }
        ofpath = opath.join(dpath, 'prob_%s.json' % prob['problemName'])
        if not opath.exists(ofpath):
            with open(ofpath, 'w') as outfile:
                outfile.write(json.dumps(prob))


def gen_graph(numNodes, seedNum):
    cur_seedNum = seedNum
    while True:
        seed(cur_seedNum)
        X, Y = [], []
        for i in range(numNodes):
            X.append(random())
            Y.append(random())
        graph = [[0.0] * numNodes for _ in range(numNodes)]
        for i in range(numNodes):
            for j in range(numNodes):
                if i == j:
                    continue
                dx = X[i] - X[j]
                dy = Y[i] - Y[j]
                graph[i][j] = round(((dx ** 2 + dy ** 2) ** (1 / 2)) * FLOAT_PRECISION)
                if graph[i][j] == 0:
                    graph[i][j] = 1
        #
        triangle_inequality_preserved = True
        all_pairs = [(i, j) for j in range(numNodes) for i in range(numNodes) if i != j]
        while all_pairs:
            i, j = all_pairs.pop()
            for k in range(numNodes):
                if k == i or k == j:
                    continue
                if graph[i][k] + graph[k][j] < graph[i][j]:
                    triangle_inequality_preserved = False
                    break
            if not triangle_inequality_preserved:
                break
        if triangle_inequality_preserved:
            break
        else:
            cur_seedNum += 1000
    return graph


def gen_graph_Manhattan(numNodes, seedNum):
    seed(seedNum)
    points = [(i, j) for j in range(numNodes) for i in range(numNodes)]
    sampled_points = sample(points, numNodes)
    #
    graph = [[0.0] * numNodes for _ in range(numNodes)]
    for i, (x0, y0) in enumerate(sampled_points):
        for j, (x1, y1) in enumerate(sampled_points):
            if i == j:
                continue
            graph[i][j] = float(abs(x0 - x1) + abs(y0 - y1))
    return graph


def gen_pi(numTasks, num_rrPoints,
           paR, caR, stR,
           seedNum=0, pi_dpath=exp_dpath):
    # paR
    #   pickup point aggregation ratio; 1.0 -> one warehouse;
    # caR
    #   capacity ratio; 1.0 -> the number of tasks
    # stR
    #   spanning tree ratio, which decides the detour limit based on the sum of weight of MST
    if not opath.exists(pi_dpath):
        os.mkdir(pi_dpath)
    for r in [paR, caR]:
        assert 0.0 <= r <= 1.0
    #

    problemName = 'nt%03d-rp%03d-pa%03d-ca%03d-st%03d-tw%03d-sn%03d' % (numTasks, num_rrPoints,
                                                                 paR * 100, caR * 100, stR * 100,
                                                                 0,
                                                                 seedNum)
    caVol, caWei = int(numTasks * caR), int(numTasks * caR)
    #
    numWH = numTasks if paR == 0.0 else min(numTasks, int(1 / paR))
    whAllocation = []
    for i in range(numTasks):
        whAllocation.append(1 + (i % numWH))
    numNodes = 2 + num_rrPoints + numWH + numTasks
    # graph = gen_graph(numNodes, seedNum)
    graph = gen_graph_Manhattan(numNodes, seedNum)

    o, d = 0, numWH + numTasks + 1
    routineSeq = [o]
    for i in range(num_rrPoints):
        routineSeq.append(d + i + 1)
    routineSeq.append(d)
    min_dist = 0.0
    for i in range(len(routineSeq) - 1):
        min_dist += graph[routineSeq[i]][routineSeq[i + 1]]

    # numMaxPickupTasks = min(caVol, caWei)
    # wIndices = list(range(1, 1 + numWH))
    # dIndices = list(range(1 + numWH, numWH + numTasks + 1))
    # targetNodes = routineSeq + wIndices + sample(dIndices, numMaxPickupTasks)
    # newGraph4MST = [[0 for _ in targetNodes] for _ in targetNodes]
    # for i, u in enumerate(targetNodes):
    #     for j, v in enumerate(targetNodes):
    #         newGraph4MST[i][j] = graph[u][v]
    # backBone = [(i, i + 1) for i in range(len(routineSeq) - 1)]
    #
    # minSpanningTree = get_minSpanningTree_givenBone(newGraph4MST, backBone)
    # mst_dist = sum(newGraph4MST[i][j] for i, j in minSpanningTree)
    # detourLimit = int(mst_dist * stR)

    detourLimit = int(min_dist * stR)

    # minSpanningTree = get_minSpanningTree(graph)
    # mst_dist = sum(graph[i][j] for i, j in minSpanningTree)
    #
    timeWindow = [[DEFAULT_TW_BEGIN, DEFAULT_TW_END] for _ in range(numNodes)]
    reward, volume, weight = [], [], []
    for k in range(numTasks):
        reward.append(DEFAULT_REWARD)
        volume.append(DEFAULT_VOLUME)
        weight.append(DEFAULT_WEIGHT)
    #
    p = Problem(problemName,
                reward, volume, weight,
                numWH, whAllocation,
                graph, timeWindow,
                caVol, caWei, detourLimit)
    p.write_json(pi_dpath)

def temp():
    nr, np, nd = 4, 2, 10
    caR, dtR = 0.5, 1.50
    tw = 1
    #
    num_rr_points = nr + 2
    o, d = 0, np + nd + 1
    #
    thUnit = 1.0 / (num_rr_points - 1)
    sX = [i * thUnit for i in range(num_rr_points)]
    sY = [0.0] + [0.75 if i % 2 == 0 else 0.25 for i in range(nr)] + [1.0]
    sXY = list(zip(sX, sY))
    hX, hY = [random() for _ in range(np)], [random() for _ in range(np)]
    hXY = list(zip(hX, hY))
    nX, nY = [random() for _ in range(nd)], [random() for _ in range(nd)]
    nXY = list(zip(nX, nY))

    XY = {o: sXY[o]}
    S, P, D = [o], [], []
    for i in range(np):
        P.append(len(XY))
        XY[len(XY)] = hXY[i]
    for i in range(nd):
        D.append(len(XY))
        XY[len(XY)] = nXY[i]
    assert d == len(XY)
    XY[d] = sXY[-1]
    for i in range(nr):
        S.append(len(XY))
        XY[len(XY)] = sXY[i + 1]
    S.append(d)
    assert num_rr_points == len(S)
    #
    h_k = []
    for i in range(len(D)):
        n0 = D[i]
        x0, y0 = XY[n0]
        closestPoint = None
        min_dist = 1e400
        for n1 in P:
            x1, y1 = XY[n1]
            dist = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** (1 / 2)
            if dist < min_dist:
                closestPoint = n1
                min_dist = dist
        assert closestPoint is not None
        h_k.append(closestPoint)
        #
    bu = 0.0
    for i in range(len(sXY) - 1):
        x0, y0 = sXY[i]
        x1, y1 = sXY[i + 1]
        bu += ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** (1 / 2)
    bu *= dtR
    #
    if tw == 0:
        al_i, be_i = [0.0 for _ in range(len(XY))], [bu * len(XY) for _ in range(len(XY))]
    else:
        if tw == 1:
            tw_numCompartment_pp, tw_numCompartment_dp = 2, 3
        elif tw == 2:
            tw_numCompartment_pp, tw_numCompartment_dp = 3, 4
        else:
            assert False
        twUnitS = bu / (len(S) * 2)
        twUnitP = bu / tw_numCompartment_pp
        twUnitD = bu / tw_numCompartment_dp
        al_i, be_i = [0.0], [twUnitS]
        for _ in range(np):
            i = choice(range(tw_numCompartment_pp))
            al_i.append(i * twUnitP)
            be_i.append((i + 1) * twUnitP)
        for _ in range(nd):
            i = choice(range(tw_numCompartment_dp))
            al_i.append(i * twUnitD)
            be_i.append((i + 1) * twUnitD)
        al_i.append(2 * (len(S) - 1) * twUnitS)
        be_i.append(bu)
        for i in range(1, len(S) - 1):
            al_i.append(2 * i * twUnitS)
            be_i.append((2 * i + 1) * twUnitS)






if __name__ == '__main__':
    temp()

    assert False


    numTasks, num_rrPoints = 10, 4
    paR, caR, stR = 0.5, 0.5, 1.10

    pi_dpath = opath.join(exp_dpath, 'problem110')

    # for paR in [0.0, 0.5, 1.0]:
    #     for caR in [0.5, 0.75, 1.0]:
    # for num_rrPoints in [2, 4, 8]:

    # for numTasks, stR in [(20, 0.8),
    #                       # (50, 0.20),
    #                       ]:
    for numTasks in [10, 20, 30, 40, 50]:
        for seedNum in range(20):
            gen_pi(numTasks, num_rrPoints,
                   paR, caR, stR,
                   seedNum, pi_dpath)
