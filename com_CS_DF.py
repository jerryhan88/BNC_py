#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 12:45:38 2020

@author: ckhan
"""

import os
import os.path as opath
from functools import reduce
import json
import csv


exp_dpath = reduce(opath.join,
       [opath.expanduser("~"), 'Dropbox', '_researchData', 'BNC',
        'Experiments'])
ori_prob_dpath = opath.join(exp_dpath, 'problem')
df_prob_dpath = opath.join(exp_dpath, 'problem_df')
PARAMETERS = ['nt', 'rp', 'pa', 'ca', 'st', 'tw']

fn = 'summary_CS_DF.csv'
sum_fpath = opath.join(exp_dpath, fn)
with open(sum_fpath, 'w') as w_csvfile:
    writer = csv.writer(w_csvfile, lineterminator='\n')
    header = ['pf']
    header += PARAMETERS
    header += ['sn']
    header += ['CS_ori', 'CS_dist', 'CS_diff', 'DF_dist', 'saving']
    writer.writerow(header)




CS_appr, DF_appr = 'BnC-hSE-hCA-hRS-hIP', 'DF'
CS_appr_dpath = reduce(opath.join, [exp_dpath, CS_appr])
DF_appr_dpath = reduce(opath.join, [exp_dpath, DF_appr])

for fn in os.listdir(CS_appr_dpath):
    if not fn.endswith('.txt'):
        continue
    pf = fn.split('_')[1][:-len('.txt')]
    #
    CS_sol_txt = opath.join(CS_appr_dpath, fn)
    with open(CS_sol_txt) as f:
        f.readline()
        _seq = f.readline().strip()
    CS_prob_fn = 'prob_%s.json' % pf
    CS_prob_fpath = opath.join(ori_prob_dpath, CS_prob_fn)    
    with open(CS_prob_fpath) as json_file:
        CS_prob = json.load(json_file)
    #
    CS_seq = list(map(int, _seq.split('-')))
    CS_dist_seq = 0.0
    for i in range(len(CS_seq) - 1):
        n0, n1 = CS_seq[i], CS_seq[i + 1]
        CS_dist_seq += CS_prob['t_ij'][n0][n1]
    #
    CS_dist_ori = 0.0
    for i in range(len(CS_prob['S']) - 1):
        n0, n1 = CS_prob['S'][i], CS_prob['S'][i + 1]
        CS_dist_ori += CS_prob['t_ij'][n0][n1]
    CS_diff = CS_dist_seq - CS_dist_ori
    #
    DF_fn = fn.replace(CS_appr, DF_appr)
    DF_sol_txt = opath.join(DF_appr_dpath, DF_fn)
    with open(DF_sol_txt) as f:
        f.readline()
        _seq = f.readline().strip()
    DF_prob_fn = 'prob_%s.json' % pf
    DF_prob_fpath = opath.join(df_prob_dpath, DF_prob_fn)    
    with open(DF_prob_fpath) as json_file:
        DF_prob = json.load(json_file)
    DF_seq = list(map(int, _seq.split('-')))
    DF_dist_seq = 0.0
    for i in range(len(DF_seq) - 1):
        n0, n1 = DF_seq[i], DF_seq[i + 1]
        DF_dist_seq += DF_prob['t_ij'][n0][n1]
    #
    with open(sum_fpath, 'a') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        row = [pf]
        row += [int(s[len('xx'):]) for s in pf.split('-')]
        row += [CS_dist_ori, CS_dist_seq, CS_diff, DF_dist_seq]
        row += [(DF_dist_seq - CS_diff) / DF_dist_seq]
        writer.writerow(row)
     