import os.path as opath
import os
import json
from random import random, seed, choice, uniform
from itertools import chain
#
from __path_organizer import exp_dpath
#
DEFAULT_REWARD, DEFAULT_VOLUME, DEFAULT_WEIGHT = 1, 1, 1
EPSILON = 1e-6
TIME_HORIZON_RATIO = 1.5
MAX_NUM_WH = 10


def gen_instance(dpath,
                 nr=4, np=2, nd=10,
                 ca=0.5, dt=1.50,
                 tw=1, sn=0, isRandomRVW=False, isOnePTW=True):
    #
    num_rr_points = nr + 2
    o, d = 0, np + nd + 1
    #
    seed(sn)
    thUnit = 1.0 / (num_rr_points - 1)
    sX = [i * thUnit for i in range(num_rr_points)]
    sY = [0.0] + [0.75 if i % 2 == 0 else 0.25 for i in range(nr)] + [1.0]
    sXY = list(zip(sX, sY))
    #
    bu = 0.0
    for i in range(len(sXY) - 1):
        x0, y0 = sXY[i]
        x1, y1 = sXY[i + 1]
        bu += ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** (1 / 2)
    TH = bu * TIME_HORIZON_RATIO
    bu *= dt
    nX, nY = [random() for _ in range(nd)], [random() for _ in range(nd)]
    nXY = list(zip(nX, nY))
    assert np < MAX_NUM_WH
    hX, hY = [random() for _ in range(MAX_NUM_WH)], [random() for _ in range(MAX_NUM_WH)]
    hXY = list(zip(hX[:np], hY[:np]))
    _XY = {o: sXY[o]}
    S, P, D = [o], [], []
    for i in range(np):
        P.append(len(_XY))
        _XY[len(_XY)] = hXY[i]
    for i in range(nd):
        D.append(len(_XY))
        _XY[len(_XY)] = nXY[i]
    assert d == len(_XY)
    _XY[d] = sXY[-1]
    for i in range(nr):
        S.append(len(_XY))
        _XY[len(_XY)] = sXY[i + 1]
    S.append(d)
    assert num_rr_points == len(S)
    #
    PD = P[:] + D[:]
    N = PD[:] + S[:]
    N.sort()
    #
    h_k, n_k = [], []
    for i in range(len(D)):
        assert i == len(n_k)
        n0 = D[i]
        n_k.append(n0)
        x0, y0 = _XY[n0]
        closestPoint = None
        min_dist = 1e400
        for n1 in P:
            x1, y1 = _XY[n1]
            dist = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** (1 / 2)
            if dist < min_dist:
                closestPoint = n1
                min_dist = dist
        assert closestPoint is not None
        h_k.append(closestPoint)
    #
    t_ij = [[0.0] * len(N) for _ in N]
    for n0 in N:
        for n1 in N:
            x0, y0 = _XY[n0]
            x1, y1 = _XY[n1]
            t_ij[n0][n1] = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** (1 / 2)
    M = len(N) * len(N) * max(chain(*[t_ij[i] for i in N]))
    c_ij = [[0] * len(N) for _ in N]
    for i in range(len(S)):
        for j in range(len(S)):
            if j < i:
                continue
            c_ij[S[i]][S[j]] = 1
            c_ij[S[j]][S[i]] = 0
    #
    if tw == 0:
        aBigNum = TH * len(_XY)
        twUnitS = TH / (len(S) * 2)
        al_i, be_i = [0.0], [twUnitS]
        for _ in range(np):
            al_i.append(0)
            be_i.append(aBigNum)
        for k in range(nd):
            al_i.append(0)
            be_i.append(aBigNum)
        al_i.append(2 * (len(S) - 1) * twUnitS)
        be_i.append(bu)
        for i in range(1, len(S) - 1):
            al_i.append(2 * i * twUnitS)
            be_i.append((2 * i + 1) * twUnitS)
    else:
        if tw == 1:
            tw_numCompartment_pp, tw_numCompartment_dp = 2, 3
        elif tw == 2:
            tw_numCompartment_pp, tw_numCompartment_dp = 3, 4
        else:
            assert False
        twUnitS = TH / (len(S) * 2)
        twUnitP = TH / tw_numCompartment_pp
        twUnitD = TH / tw_numCompartment_dp
        _al_i, _be_i = {S[0]: 0.0}, {S[0]: twUnitS}
        _al_i[S[-1]] = 2 * (len(S) - 1) * twUnitS
        _be_i[S[-1]] = TH
        for i in range(1, len(S) - 1):
            _al_i[S[i]] = 2 * i * twUnitS
            _be_i[S[i]] = (2 * i + 1) * twUnitS
        for n0 in D:
            i = choice(range(tw_numCompartment_dp))
            al_d, be_d = i * twUnitD, (i + 1) * twUnitD
            _al_i[n0] = al_d
            _be_i[n0] = be_d
        for n0 in P:
            if not isOnePTW:
                i = choice(range(tw_numCompartment_pp))
                _al_i[n0] = i * twUnitP
                _be_i[n0] = (i + 1) * twUnitP
            else:
                _al_i[n0] = 0
                _be_i[n0] = TH
        al_i, be_i = [None for _ in _al_i], [None for _ in _be_i]
        for n0, v in _al_i.items():
            al_i[n0] = v
        for n0, v in _be_i.items():
            be_i[n0] = v
    #
    K = list(range(nd))
    if not isRandomRVW:
        v_k = [DEFAULT_VOLUME for _ in K]
        w_k = [DEFAULT_WEIGHT for _ in K]
        r_k = [DEFAULT_REWARD for _ in K]
    else:
        v_k, w_k, r_k = [], [], []
        for _ in K:
            v = uniform(EPSILON, DEFAULT_VOLUME)
            v_k.append(v)
            w = uniform(EPSILON, DEFAULT_WEIGHT)
            w_k.append(w)
            r = max(v, w)
            r_k.append(r)
    bv, bw = ca, ca
    #
    problemName = 'nr%03d-np%03d-nd%03d-ca%03d-dt%03d-tw%03d-sn%03d' % (nr, np, nd,
                                                                        ca, dt * 100,
                                                                        tw, sn)
    XY = [None for _ in range(len(_XY))]
    for i, xy in _XY.items():
        XY[i] = xy
    prob = {
            'problemName': problemName,
            'XY': XY, 'TH': TH,
            'S': S, 'P': P, 'D': D, 'PD': PD, 'N': N,
                'o': o, 'd': d,
                'h_k': h_k, 'n_k': n_k,
                't_ij': t_ij, 'c_ij': c_ij,
                'al_i': al_i, 'be_i': be_i,
                'M': M,
            'K': K,
                'r_k': r_k, 'v_k': v_k, 'w_k': w_k,
            'bv': bv, 'bw': bw, 'bu': bu}
    if not opath.exists(dpath):
        os.mkdir(dpath)
    ofpath = opath.join(dpath, 'prob_%s.json' % prob['problemName'])
    if not opath.exists(ofpath):
        with open(ofpath, 'w') as outfile:
            outfile.write(json.dumps(prob))


if __name__ == '__main__':
    dpath = opath.join(exp_dpath, 'problem_temp')
    nr, np, nd = 4, 4, 80
    ca, dt = 10, 1.25
    tw, sn = 1, 0

    # for nd in range(10, 110, 10):
        # for np in [2, 4]:
            # for np in range(2, 6):
            #     for ca in [0.5, 1.0]:
            # for dt in [1.25, 1.50, 2.00]:
            # for tw in [1, 2]:
    for sn in range(30, 35):
        gen_instance(dpath,
                     nr, np, nd,
                     ca, dt,
                     tw, sn, isRandomRVW=True, isOnePTW=True)
