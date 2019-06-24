import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def str_join(a, b, c):

    a = np.array(a)
    b = np.array(b)
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
        tp_col_names = detector_name+' '+'TP'
        fp_col_names = detector_name+' '+'FP'
        fn_col_names = detector_name+' '+'FN'
        tn_col_names = detector_name+' '+'TN'      

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


def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2.0, 1.01*height,'%.2f' % height,ha='center', va='bottom')


gudb_cs_results = pd.read_csv('results_GUDB_chest_strap_11.21.csv', dtype=int, index_col=0)
gudb_cable_results = pd.read_csv('results_GUDB_loose_cables_15.35.csv', dtype=int, index_col=0)
mitdb_results = pd.read_csv('results_MITDB_13.49.csv', dtype=int, index_col=0)

det_names = ['two_average', 'matched_filter', 'swt', 'engzee', 'christov', 'hamilton', 'pan_tompkins']
experiment_names = ['sitting','maths','walking','hand_bike','jogging']
output_names = ['TP', 'FP', 'FN', 'TN']


mitdb_se = []
for det in det_names:
    mitdb_se.append(sensitivity(mitdb_results, det))
mitdb_ppv = []
for det in det_names:
    mitdb_ppv.append(ppv(mitdb_results, det))
mitdb_f1 = []
for det in det_names:
    mitdb_f1.append(f1(mitdb_results, det))

gudb_cs_se = []
for det in det_names:
    gudb_cs_se.append(sensitivity(gudb_cs_results, det, experiment_names))
gudb_cs_ppv = []
for det in det_names:
    gudb_cs_ppv.append(ppv(gudb_cs_results, det, experiment_names))
gudb_cs_f1 = []
for det in det_names:
    gudb_cs_f1.append(f1(gudb_cs_results, det, experiment_names))

gudb_cable_se = []
for det in det_names:
    gudb_cable_se.append(sensitivity(gudb_cable_results, det, experiment_names))
gudb_cable_ppv = []
for det in det_names:
    gudb_cable_ppv.append(ppv(gudb_cable_results, det, experiment_names))
gudb_cable_f1 = []
for det in det_names:
    gudb_cable_f1.append(f1(gudb_cable_results, det, experiment_names))


x_pos = np.arange(len(det_names))
width = 0.4

fig, ax = plt.subplots()
rects1 = ax.bar(x_pos, mitdb_se, align='center')
ax.set_ylabel('Sensitivity (%)')
ax.set_title('Detector Sensitivity on MITDB')
ax.set_xticks(x_pos)
ax.set_xticklabels(det_names)
autolabel(rects1)

fig, ax = plt.subplots()
rects1 = ax.bar(x_pos, mitdb_ppv, align='center')
ax.set_ylabel('PPV (%)')
ax.set_title('Detector PPV on MITDB')
ax.set_xticks(x_pos)
ax.set_xticklabels(det_names)
autolabel(rects1)

fig, ax = plt.subplots()
rects1 = ax.bar(x_pos, gudb_cs_se, width)
rects2 = ax.bar(x_pos+width, gudb_cable_se, width)
ax.set_ylabel('PPV (%)')
ax.set_title('Detector PPV on GUDB')
ax.set_xticks(x_pos + width / 2)
ax.set_xticklabels(det_names)
ax.legend((rects1[0], rects2[0]), ('Chest Strap', 'Loose Cables'))
autolabel(rects1)
autolabel(rects2)

plt.show()