import os.path as opath
import os
import csv
import pandas as pd
from functools import reduce


# exp_dpath = reduce(opath.join,
#        [opath.expanduser("~"), 'Dropbox', '_researchData', 'BNC',
#         'Experiments', '_LP_results'])

exp_dpath = reduce(opath.join,
       [opath.expanduser("~"), 'Dropbox', '_researchData', 'BNC',
        'Experiments'])

PARAMETERS = ['nt', 'rp', 'pa', 'ca', 'st', 'tw']


def get_appNames():
    appNames = []
    for dn in os.listdir(exp_dpath):
        p = opath.join(exp_dpath, dn)
        if not opath.isdir(p):
            continue
        if not (dn.startswith('BnC') or dn.startswith('ILP') or
                dn.startswith('RC') or dn.startswith('LP')):
            continue
        appNames.append(dn)
    return appNames
    

def summary():
    fn = 'summary_raw.csv'
    raw_fpath = opath.join(exp_dpath, fn)
    appNames = get_appNames()
    with open(raw_fpath, 'w') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        header = ['pf']
        header += PARAMETERS
        header += ['sn']
        header += ['%s_objV' % appName for appName in appNames]
        header += ['%s_cpuT' % appName for appName in appNames]
        writer.writerow(header)

    prob_dpath = opath.join(exp_dpath, 'problem')
    prefixs = []
    for fn in os.listdir(prob_dpath):
        if not fn.endswith('.json'):
            continue
        _, prefix = fn[:-len('.json')].split('_')
        prefixs.append(prefix)
    prefixs.sort()
    #
    for pf in prefixs:
        nt, rp, pa, ca, st, tw, sn = [int(s[len('xx'):]) for s in pf.split('-')]
        new_row = [pf, nt, rp, pa, ca, st, tw, sn]
        objVs, cpuTs = [], []
        for appName in appNames:
            sol_fpath = reduce(opath.join, [exp_dpath, appName, '%s_%s.csv' % (appName, pf)])
            if opath.exists(sol_fpath):
                with open(sol_fpath) as r_csvfile:
                    reader = csv.DictReader(r_csvfile)
                    for row in reader:
                        _objV, _eliCpuTime = [row[cn] for cn in ['objV', 'eliCpuTime']]
                    objVs.append(_objV)
                    cpuTs.append(_eliCpuTime)
            else:
                objVs.append('-')
                cpuTs.append('-')
        new_row += objVs
        new_row += cpuTs
        with open(raw_fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow(new_row)
    df = pd.read_csv(raw_fpath)
    df = df.sort_values(by=['nt', 'rp', 'pa', 'ca', 'st', 'tw', 'sn'])
    df.to_csv(raw_fpath, index=False)
    #
    fn = 'summary_num.csv'
    sumNum_fpath = opath.join(exp_dpath, fn)
    for appName in appNames:
        col1, col2 = '%s_objV' % appName, '%s_cpuT' % appName
        df = df[df[col1] != "-"]
        df[col1] = df[col1].apply(pd.to_numeric)
        df[col2] = df[col2].apply(pd.to_numeric)
        df = df[df[col1] > 0.0]

    gdf = df.groupby(PARAMETERS).mean().reset_index()
    gdf = gdf.drop(['sn'], axis=1)
    gdf.to_csv(sumNum_fpath, index=False)

    fn = 'summary_per.csv'
    sumPer_fpath = opath.join(exp_dpath, fn)
    baseName = 'LP-N'
    bCol1, bCol2 = '%s_objV' % baseName, '%s_cpuT' % baseName
    for appName in appNames:
        if appName == baseName:
            continue
        col1 = '%s_objV' % appName
        gdf = gdf[gdf[col1] <= gdf[bCol1]]
    for appName in appNames:
        if appName == baseName:
            continue
        col1, col2 = '%s_objV' % appName, '%s_cpuT' % appName
        gdf[col1] = gdf.apply(lambda row: (row[bCol1] - row[col1]) / row[bCol1], axis=1)
        gdf[col2] = gdf.apply(lambda row: (row[col2] - row[bCol2]) / row[bCol2], axis=1)
    gdf = gdf.drop([bCol1, bCol2], axis=1)
    gdf.to_csv(sumPer_fpath, index=False)


def temp():
    appNames = get_appNames()
    bCol = 'LP-N_objV'
    raw_fpath = opath.join(exp_dpath, 'summary_raw.csv')
    prmt_sns = {}
    with open(raw_fpath) as r_csvfile:
        reader = csv.DictReader(r_csvfile)
        for row in reader:
            nt, rp, pa, ca, st, tw = [eval(row[cn]) for cn in PARAMETERS]
            sn = int(row['sn'])
            isValidInstance = True
            for appName in appNames:
                col = '%s_objV' % appName
                if row[col] == '-' or eval(row[col]) < 0.0:
                    isValidInstance = False
                    break
                if col != bCol and eval(row[bCol]) >= 0.0 and eval(row[col]) > eval(row[bCol]):
                    isValidInstance = False
                    break                    
            if not isValidInstance:
                continue
            k = (nt, rp, pa, ca, st, tw)
            if k not in prmt_sns:
                prmt_sns[k] = []
            prmt_sns[k].append(sn)

    sumCnt_fpath = opath.join(exp_dpath, 'summary_cnt.csv')
    with open(sumCnt_fpath, 'w') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        header = PARAMETERS[:]
        header += ['numIns', 'seedNums']
        writer.writerow(header)
        for k, seedNums in prmt_sns.items():
            new_row = list(k)
            new_row += [len(seedNums), ';'.join(['%d' % sn for sn in seedNums])]
            writer.writerow(new_row)            
    df = pd.read_csv(sumCnt_fpath)
    df = df.sort_values(by=['nt', 'rp', 'pa', 'ca', 'st', 'tw'])
    df.to_csv(sumCnt_fpath, index=False)
        
    
def gen_vizImgs():
    import sys
    import json
    from PyQt5.QtWidgets import QApplication
    #
    from vizPos import Viz as posViz
    from vizTW import Viz as twViz
    #
    prob_dpath = reduce(opath.join, [exp_dpath, 'problem'])
    img_dpath = reduce(opath.join, [exp_dpath, '_img'])
    if not opath.exists(img_dpath):
        os.mkdir(img_dpath)
    for fn in sorted(os.listdir(prob_dpath)):
        if not fn.endswith('.json'):
            continue
        #
        prefix = fn[len('prob_'):-len('.json')]
        prob_fpath = reduce(opath.join, [exp_dpath, 'problem', fn])
        prob = None
        with open(prob_fpath) as json_file:
            prob = json.load(json_file)
        assert prob is not None
        #
        pos_fpath = opath.join(img_dpath, '%s_pos.pdf' % prefix)
        if not opath.exists(pos_fpath):
            app = QApplication(sys.argv)
            viz = posViz(prob)
            viz.save_img(pos_fpath)
            app.quit()
            del app
        #
        tw_fpath = opath.join(img_dpath, '%s_tw.pdf' % prefix)
        if not opath.exists(tw_fpath):
            app = QApplication(sys.argv)
            viz = twViz(prob)
            viz.save_img(tw_fpath)
            app.quit()
            del app


if __name__ == '__main__':
    # summary()
    # temp()
    gen_vizImgs()

