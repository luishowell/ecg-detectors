import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# det_names = ['two_average', 'matched_filter', 'swt', 'engzee', 'christov', 'hamilton', 'pan_tompkins']
# experiment_names = ['sitting','maths','walking','hand_bike','jogging']
# output_names = ['TP', 'FP', 'FN', 'TN']


def str_join(a, b, c=None):

    a = np.array(a)
    b = np.array(b)

    if c==None:
        str_array = np.core.defchararray.add(a, b)
    
    else:
        c = np.array(c)
        str_array = np.core.defchararray.add(np.core.defchararray.add(a, b), c)

    return str_array


def summed_results(results_df, detector_name, experiments=None):

    if experiments!=None:
        tp_col_names = str_join(detector_name+' ', experiments, ' TP')
        fp_col_names = str_join(detector_name+' ', experiments, ' FP')
        fn_col_names = str_join(detector_name+' ', experiments, ' FN')
        tn_col_names = str_join(detector_name+' ', experiments, ' TN')
    else:
        tp_col_names = str_join(detector_name+' ', 'TP')
        fp_col_names = str_join(detector_name+' ', 'FP')
        fn_col_names = str_join(detector_name+' ', 'FN')
        tn_col_names = str_join(detector_name+' ', 'TN')      

    total_tp = np.sum(results_df.loc[:, tp_col_names].values)
    total_fp = np.sum(results_df.loc[:, fp_col_names].values)
    total_fn = np.sum(results_df.loc[:, fn_col_names].values)
    total_tn = np.sum(results_df.loc[:, tn_col_names].values)

    return total_tp, total_fp, total_fn, total_tn


def sensitivity(results_df, detector_name, experiments=None):

    total_tp, total_fp, total_fn, total_tn = summed_results(results_df, detector_name, experiments)

    se = total_tp/(total_tp+total_fn)*100.0

    return se


def ppv(results_df, detector_name, experiments=None):

    total_tp, total_fp, total_fn, total_tn = summed_results(results_df, detector_name, experiments)

    ppv_val = total_tp/(total_tp+total_fp)*100.0

    return ppv_val


def f1(results_df, detector_name, experiments=None):

    total_tp, total_fp, total_fn, total_tn = summed_results(results_df, detector_name, experiments)

    f1_val = (2*total_tp)/((2*total_tp)+total_fp+total_fn)*100.0

    return f1_val


gudb_cs_results = pd.read_csv('results_GUDB_chest_strap_11.21.csv', dtype=int, index_col=0)

experiment_names = ['sitting','maths','walking','hand_bike','jogging']


print(sensitivity(gudb_cs_results, 'two_average', experiment_names))

print(ppv(gudb_cs_results, 'two_average', experiment_names))

print(f1(gudb_cs_results, 'two_average', experiment_names))