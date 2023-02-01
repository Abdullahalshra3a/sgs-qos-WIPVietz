#- * - coding: utf - 8
# Created By: Frauke Oest

"""This helps in aggregating statistics based on the result excel sheet"""

import numpy as np
import pandas as pd
from Config import RESULT_PATH
from datetime import datetime
import openpyxl

file_with_data = RESULT_PATH + 'result.xlsx'
try:
    xls = pd.ExcelFile(file_with_data)
    df = pd.read_excel(xls, 'Sheet1')
    print("file found")
    res1 = df.copy()
    res1.drop(columns=['model_creation', 'total_duration','paths_SE', 'paths_CVC', 'paths_VPP', 'paths_LM', 'paths_AR'])

    columns = ['experiment_time', 'experiment_nr', 'nr_sc_SE', 'nr_sc_CVC', 'nr_sc_VPP', 'nr_sc_AR', 'nr_sc_LM',
               'comp_time_SE', 'comp_time_CVC', 'comp_time_VPP', 'comp_time_AR', 'comp_time_LM',
               'model_creation', 'model_solving', 'total_duration', 'paths_SE', 'paths_CVC', 'paths_VPP', 'paths_LM',
               'paths_AR']


    res = res1.reindex(
        columns=['experiment_time', 'experiment_nr', 'nr_sc_AR', 'nr_sc_CVC', 'nr_sc_LM', 'nr_sc_SE', 'nr_sc_VPP',
                 'comp_time_AR', 'comp_time_CVC', 'comp_time_LM', 'comp_time_SE', 'comp_time_VPP', 'model_solving'])
   # print(res)
    mean_exp = res.groupby('experiment_nr').mean()
   # print(mean_exp)
    latex_mean = mean_exp.to_latex(float_format="%.4f")  # float_format="%.4f"

    # print("Latex format mean:")
    # print(latex_mean)
    # #
    std_exp = res.groupby('experiment_nr').std()
    latex_std = std_exp.to_latex(float_format="%.4f")  # float_format="%.4f"

    print("Latex format std")
    print(latex_std)


except FileNotFoundError:
    print("file not found")
