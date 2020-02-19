#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 08:25:47 2020

@author: ckhan
"""
import os
import os.path as opath
from functools import reduce
import json


exp_dpath = reduce(opath.join,
       [opath.expanduser("~"), 'Dropbox', '_researchData', 'BNC',
        'Experiments'])
ori_prob_dpath = opath.join(exp_dpath, 'problem')
df_prob_dpath = opath.join(exp_dpath, 'problem_df')
if not opath.exists(df_prob_dpath):
    os.mkdir(df_prob_dpath)

appr = 'BnC-hSE-hCA-hRS-hIP'
appr_dpath = reduce(opath.join, [exp_dpath, appr])

for fn in os.listdir(appr_dpath):
    if not fn.endswith('.txt'):
        continue
    sol_txt = opath.join(appr_dpath, fn)
    with open(sol_txt) as f:
        f.readline()
        _seq = f.readline().strip()
    #
    prefix = fn.split('_')[1][:-len('.txt')]
    prob_fn = 'prob_%s.json' % prefix
    prob_fpath = opath.join(ori_prob_dpath, prob_fn)
    #
    with open(prob_fpath) as json_file:
        prob = json.load(json_file)
    o, d = prob['o'], prob['d']    
    cov_P = [i for i in map(int, _seq.split('-')) if i in prob['P']]
    cov_D = [i for i in map(int, _seq.split('-')) if i in prob['D']]    
    cov_K = [k for k, hk in enumerate(prob['n_k']) if hk in cov_D]    
    new_o = 0
    mapper_ord_new = {o: new_o}
    mapper_new_ord = {new_o: o}
    new_P = []
    for old_i in cov_P:
        new_i = len(mapper_ord_new)
        mapper_ord_new[old_i] = new_i
        mapper_new_ord[new_i] = old_i
        new_P.append(new_i)
    new_D = []
    for old_i in cov_D:
        new_i = len(mapper_ord_new)
        mapper_ord_new[old_i] = new_i
        mapper_new_ord[new_i] = old_i
        new_D.append(new_i)
    new_d = len(mapper_ord_new)
    mapper_ord_new[d] = new_d
    mapper_new_ord[new_d] = d
    #
    new_PD = new_P + new_D
    new_S = [new_o, new_d]
    new_N = new_PD + new_S
    #
    depot = [0.5, 0.5]
    new_t_ij = [[0] * len(new_N) for _ in new_N]
    for new_i in new_N:
        if new_i == new_o or new_i == new_d:
            x0, y0 = depot
        else:
            x0, y0 = prob['XY'][mapper_new_ord[new_i]]
        for new_j in new_N:
            if new_j == new_o or new_j == new_d:
                x1, y1 = depot
            else:
                x1, y1 = prob['XY'][mapper_new_ord[new_j]]            
            new_t_ij[new_i][new_j] = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** (1 / 2)
    new_al_i, new_be_i = [0.0 for _ in new_N], [0.0 for _ in new_N]
    for new_i in [new_o, new_d]:
        new_al_i[new_i] = 0.0
        new_be_i[new_i] = prob['M']
    for new_i in new_PD:
        new_al_i[new_i] = prob['al_i'][mapper_new_ord[new_i]]
        new_be_i[new_i] = prob['be_i'][mapper_new_ord[new_i]]
    #
    new_K, new_h_k, new_n_k = [], [], []
    for new_k, old_k in enumerate(cov_K):
        new_K.append(new_k)        
        new_h_k.append(mapper_ord_new[prob['h_k'][old_k]])
        new_n_k.append(mapper_ord_new[prob['n_k'][old_k]])
    #
    prob['P'] = new_P
    prob['D'] = new_D
    prob['S'] = new_S
    prob['PD'] = new_PD
    prob['N'] = new_N
    prob['t_ij'] = new_t_ij
    prob['al_i'] = new_al_i
    prob['be_i'] = new_be_i        
    prob['K'] = new_K
    prob['h_k'] = new_h_k
    prob['n_k'] = new_n_k
    prob['o'], prob['d'] = new_o, new_d
    #
    ofpath = opath.join(df_prob_dpath, prob_fn)        
    with open(ofpath, 'w') as outfile:
        outfile.write(json.dumps(prob))