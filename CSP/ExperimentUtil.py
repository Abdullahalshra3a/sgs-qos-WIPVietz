#- * - coding: utf - 8
# Created By: Frauke Oest

import pandas as pd
from Config import RESULT_PATH
from datetime import datetime
import openpyxl
import time


def dataframe_row_generator(experiment_nr, stat, res, time=None, sgss=[], solvers=[]):
    row = dict()
    row['experiment_time'] = time
    row['experiment_nr'] = experiment_nr
    for sgs in sgss:
        row[f'nr_sc_{sgs}'] = stat['number_of_so'][sgs]
        row[f'comp_time_{sgs}'] = stat['comp_time'][sgs]
    for solver in solvers:
        row[f'model_creation_{solver}'] = stat['comp_time'][f'model_creation_{solver}']
        row[f'minizinc_solving_{solver}'] = stat['comp_time'][f'minizinc_solving_{solver}']
    # row = {
    #     'experiment_time': time,
    #     'experiment_nr': experiment_nr,
    #     'nr_sc_SE': stat['number_of_so']['SE'],
    #     'nr_sc_CVC': stat['number_of_so']['CVC'],
    #     'nr_sc_VPP': stat['number_of_so']['VPP'],
    #     'nr_sc_AR': stat['number_of_so']['AR'],
    #     'nr_sc_LM': stat['number_of_so']['LM'],
    #     'comp_time_SE': stat['comp_time']['SE'],
    #     'comp_time_CVC': stat['comp_time']['CVC'],
    #     'comp_time_VPP': stat['comp_time']['VPP'],
    #     'comp_time_LM': stat['comp_time']['LM'],
    #     'comp_time_AR': stat['comp_time']['AR'],
    #     'model_creation': stat['comp_time']['model_creation'],
    #     'model_solving': stat['comp_time']['minizinc_single_solving'],
    #     'total_duration': stat['comp_time']['total_process'],
    # }
    if res:
        row['paths_SE'] = res['SE'].multipaths
        row['paths_CVC'] = res['CVC'].multipaths
        row['paths_VPP'] = res['VPP'].multipaths
        row['paths_LM'] = res['LM'].multipaths
        row['paths_AR'] = res['AR'].multipaths  # ,
    # 'latency_paths_SE': res['SE'].latency_sc,
    # 'latency_paths_CVC': res['CVC'].latency_sc,
    # 'latency_paths_VPP': res['VPP'].latency_sc,
    # 'latency_paths_LM': res['LM'].latency_sc,
    # 'latency_paths_AR': res['AR'].latency_sc
    else:
        if res:
            row['paths_SE'] = None
            row['paths_CVC'] = None
            row['paths_VPP'] = None
            row['paths_LM'] = None
            row['paths_AR'] = None
    return row

def write_experiments(experiments, sgss, solvers, file_name='result'):
    file_with_data = RESULT_PATH + file_name + '.xlsx'

    try:
        xls = pd.ExcelFile(file_with_data, engine='openpyxl')
        df = pd.read_excel(xls, 'Sheet1')
        print("file found")
        # with pd.ExcelWriter(RESULT_PATH + 'result.xlsx', mode='a', if_sheet_exists="replace") as writer:
        #     df.to_excel(writer, sheet_name='Sheet1')
    except FileNotFoundError:
        print("file not found")
        column_base = ['experiment_time', 'experiment_nr']
        column_sc_nr = [f'nr_sc_{sgs}' for sgs in sgss]
        column_sc_comptime = [f'comp_time_{sgs}' for sgs in sgss]
        column_model = [f'model_creation_{solver}' for solver in solvers]
        column_solving = [f'minizinc_solving_{solver}' for solver in solvers]
        column_sc_paths = [f'paths_{sgs}' for sgs in sgss]

        columns = column_base + column_sc_nr + column_sc_comptime + column_model + column_solving + column_sc_paths
        # df = pd.DataFrame(
        #     columns=['experiment_time', 'experiment_nr', 'nr_sc_SE', 'nr_sc_CVC', 'nr_sc_VPP', 'nr_sc_AR', 'nr_sc_LM',
        #              'comp_time_SE', 'comp_time_CVC', 'comp_time_VPP', 'comp_time_AR', 'comp_time_LM',
        #              'model_creation', 'model_solving', 'total_duration', 'paths_SE', 'paths_CVC', 'paths_VPP',
        #              'paths_LM', 'paths_AR'])
        df = pd.DataFrame(columns=columns)

    experiment_time = int(time.time())

    dt_object = datetime.fromtimestamp(int(experiment_time))

    for e in experiments:
        try:
            row = dataframe_row_generator(e, experiments[e]['stats'], experiments[e]['result'], dt_object, sgss, solvers)
            df = df.append(row, ignore_index=True)
        except KeyError:
            print(e)
   # normal_row = dataframe_row_generator(1, normal_stat, normal_res, dt_object)
    #df = df.append(normal_row, ignore_index=True)

    # no_bndwth_row = dataframe_row_generator(2, no_bndwth_stat, no_bndwth_res)
    # df = df.append(no_bndwth_row, ignore_index=True)
    #
    # red_row = dataframe_row_generator(3, red_stat, red_res)
    # df = df.append(red_row, ignore_index=True)
    #
    # no_lat_row = dataframe_row_generator(4, no_lat_stat, no_lat_res)
    # df = df.append(no_lat_row, ignore_index=True)

    # virt_row = dataframe_row_generator(5, virt_stat, virt_res)
    # df = df.append(virt_row, ignore_index=True)
    #
    # no_cpu_row = dataframe_row_generator(6, no_cpu_stat, no_cpu_res)
    # df = df.append(no_cpu_row, ignore_index=True)
    #
    # dist_row = dataframe_row_generator(7, dist_stat, dist_res)
    # df = df.append(dist_row, ignore_index=True)


    with pd.ExcelWriter(file_with_data) as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    # with pd.ExcelWriter(RESULT_PATH + 'result.xlsx', mode='a', if_sheet_exists="replace") as writer:
    #     df.to_excel(writer, sheet_name='Sheet1')

    # df.to_excel(RESULT_PATH + "result_"+str(experiment_time)+".xlsx", index=False)

    return df