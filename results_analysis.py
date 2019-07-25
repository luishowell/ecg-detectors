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


def get_result(results_df, calc_function, det_names, experiments=None):
    
    result = []
    for det in det_names:
        result.append(calc_function(results_df, det, experiments))

    return np.array(result)


def single_plot(data, y_label, title = None):
    fig, ax = plt.subplots()
    plot_names = ['Elgendi et al', 'Matched Filter', 'Kalidas and Tamil', 'Engzee Mod', 'Christov', 'Hamilton', 'Pan and Tompkins']
    x_pos = np.arange(len(plot_names))

    fig.set_size_inches(10, 7)
    rects1 = ax.bar(x_pos, data, width = 0.65, align='center')
    ax.set_ylabel(y_label)
    ax.set_xlabel('Detector')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(plot_names)
    autolabel(ax, rects1)

    if title!=None:
        ax.set_title(title)

    plt.tight_layout()

    return rects1


def double_plot(data1, data2, y_label, legend1, legend2, title=None):
    fig, ax = plt.subplots()
    plot_names = ['Elgendi et al', 'Matched Filter', 'Kalidas and Tamil', 'Engzee Mod', 'Christov', 'Hamilton', 'Pan and Tompkins']
    x_pos = np.arange(len(plot_names))

    fig.set_size_inches(10, 7)
    width = 0.4
    rects1 = ax.bar(x_pos, data1, width)
    rects2 = ax.bar(x_pos+width, data2, width)
    ax.set_ylim(70)
    ax.set_ylabel(y_label)
    ax.set_xlabel('Detector')
    ax.set_xticks(x_pos + width / 2)
    ax.set_xticklabels(plot_names)
    ax.legend((rects1[0], rects2[0]), (legend1, legend2))
    autolabel(ax, rects1)
    autolabel(ax, rects2)

    if title!=None:
        ax.set_title(title)

    plt.tight_layout()

    return rects1, rects2


def autolabel(ax, rects):
    """
    Attach a text label above each bar displaying its height
    """

    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2.0, 1.005*height,'%.2f' % height,ha='center', va='bottom')


# GUDB
gudb_cs_results = pd.read_csv('results_GUDB_chest_strap.csv', dtype=int, index_col=0)
gudb_cable_results = pd.read_csv('results_GUDB_loose_cables.csv', dtype=int, index_col=0)

# MITDB
mitdb_results = pd.read_csv('results_MITDB.csv', dtype=int, index_col=0)

det_names = ['two_average', 'matched_filter', 'swt', 'engzee', 'christov', 'hamilton', 'pan_tompkins']
plot_names = ['Elgendi et al', 'Matched Filter', 'Kalidas and Tamil', 'Engzee Mod', 'Christov', 'Hamilton', 'Pan and Tompkins']
experiment_names = ['sitting','maths','walking','hand_bike','jogging']
output_names = ['TP', 'FP', 'FN', 'TN']


# calculating results
mitdb_se = get_result(mitdb_results, sensitivity, det_names)
mitdb_ppv = get_result(mitdb_results, ppv, det_names)
mitdb_f1 = get_result(mitdb_results, f1, det_names)

gudb_cs_se = get_result(gudb_cs_results, sensitivity, det_names, experiment_names)
gudb_cs_ppv = get_result(gudb_cs_results, ppv, det_names, experiment_names)
gudb_cs_f1 = get_result(gudb_cs_results, f1, det_names, experiment_names)

gudb_cable_se = get_result(gudb_cable_results, sensitivity, det_names, experiment_names)
gudb_cable_ppv = get_result(gudb_cable_results, ppv, det_names, experiment_names)
gudb_cable_f1 = get_result(gudb_cable_results, f1, det_names, experiment_names)

cs_sitting_f1 = get_result(gudb_cs_results, f1, det_names, ['sitting'])
cs_jogging_f1 = get_result(gudb_cs_results, f1, det_names, ['jogging'])

cable_sitting_f1 = get_result(gudb_cable_results, f1, det_names, ['sitting'])
cable_jogging_f1 = get_result(gudb_cable_results, f1, det_names, ['jogging'])

# plotting
single_plot(mitdb_se, 'Sensitivity (%)', 'MITDB')
single_plot(mitdb_ppv, 'PPV (%)', 'MITDB')

double_plot(gudb_cs_se, gudb_cable_se, 'Sensitivity (%)', 'Chest Strap', 'Loose Cables', 'GUDB')
double_plot(gudb_cs_ppv, gudb_cable_ppv, 'PPV (%)', 'Chest Strap', 'Loose Cables', 'GUDB')
double_plot(gudb_cs_f1, gudb_cable_f1, 'F1 Score (%)', 'Chest Strap', 'Loose Cables', 'GUDB')

double_plot(cs_sitting_f1, cs_jogging_f1, 'F1 Score (%)', 'Chest Strap Sitting', 'Chest Strap Jogging', 'GUDB')
double_plot(cable_sitting_f1, cable_jogging_f1, 'F1 Score (%)', 'Loose Cables Sitting', 'Loose Cables Jogging', 'GUDB')
double_plot(cs_sitting_f1, cable_sitting_f1, 'F1 Score (%)', 'Chest Strap Sitting', 'Loose Cables Sitting', 'GUDB')

plt.show()
