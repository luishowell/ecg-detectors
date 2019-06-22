import numpy as np
import matplotlib.pyplot as plt
import pathlib
from hrv import HRV
from ecgdetectors import Detectors
import scipy.stats as stats

path_gu_ecg_database = '../dataset_716'
data_path = path_gu_ecg_database + r'/experiment_data'

import sys
sys.path.insert(0, path_gu_ecg_database + r'/example_code')
from ecg_gla_database import Ecg

# for plotting max hflf ratio
hflfmax = 10

# example subject for the spectra
subj = 1

sitting_class = Ecg(data_path, subj, 'maths')
sitting_class.filter_data()
detectors = Detectors(sitting_class.fs)
r_peaks = detectors.swt_detector(sitting_class.einthoven_II)

hrv_class = HRV(sitting_class.fs)
lfhf = hrv_class.fAnalysis(r_peaks)
print("Wavelet detector: lf/hf=",lfhf)

# in time
plt.title("Example for sitting (no error)")
plt.subplot(211)
plt.plot(hrv_class.t_hr_linear,hrv_class.hr_linear)
plt.plot(hrv_class.t_hr_discrete,hrv_class.hr_discrete,"x")

# now the Fourier spectrum
plt.subplot(212)
plt.plot(hrv_class.f_hr_axis,hrv_class.f_hr)
plt.ylim([0,0.3])

r_peaks = detectors.two_average_detector(sitting_class.einthoven_II)

hrv_class = HRV(sitting_class.fs)
lfhf = hrv_class.fAnalysis(r_peaks)
print("Two average detector: lf/hf=",lfhf)

plt.figure()
# in time
plt.title("Example for sitting (with error)")
plt.subplot(211)
plt.plot(hrv_class.t_hr_linear,hrv_class.hr_linear)
plt.plot(hrv_class.t_hr_discrete,hrv_class.hr_discrete,"x")

# now the Fourier spectrum
plt.subplot(212)
plt.plot(hrv_class.f_hr_axis,hrv_class.f_hr)
plt.ylim([0,0.3])





maths_hf = []
maths_error_hf = []
maths_true_hf = []

sitting_hf = []
sitting_error_hf = []
sitting_true_hf = []

total_subjects = 25
subject = []

for i in range(total_subjects):
#for i in range(2):
    print(i)
    sitting_class = Ecg(data_path, i, 'sitting')
    sitting_class.filter_data()
    maths_class = Ecg(data_path, i, 'maths')
    maths_class.filter_data()

    if sitting_class.anno_cs_exists and maths_class.anno_cs_exists:
        subject.append(i)
        
        hrv_class = HRV(sitting_class.fs)

        r_peaks = detectors.swt_detector(sitting_class.einthoven_II)
        sitting_hf.append(hrv_class.fAnalysis(r_peaks))
        
        r_peaks = detectors.swt_detector(maths_class.einthoven_II)
        maths_hf.append(hrv_class.fAnalysis(r_peaks))

        sitting_error_rr = detectors.two_average_detector(sitting_class.einthoven_II)
        sitting_error_hf.append(hrv_class.fAnalysis(sitting_error_rr))

        maths_error_rr = detectors.two_average_detector(maths_class.einthoven_II)
        maths_error_hf.append(hrv_class.fAnalysis(maths_error_rr))

        maths_true_rr = maths_class.anno_cs
        maths_true_hf.append(hrv_class.fAnalysis(maths_true_rr))

        sitting_true_rr = sitting_class.anno_cs
        sitting_true_hf.append(hrv_class.fAnalysis(sitting_true_rr))

subject = np.array(subject)
width = 0.1

fig, ax = plt.subplots()
rects1 = ax.bar(subject, sitting_hf, width)
rects2 = ax.bar(subject + width, maths_hf, width)
rects3 = ax.bar(subject+(2*width), sitting_error_hf, width)
rects4 = ax.bar(subject+(3*width), maths_error_hf, width)
rects5 = ax.bar(subject+(4*width), sitting_true_hf, width)
rects6 = ax.bar(subject+(5*width), maths_true_hf, width)

ax.set_ylabel('fAnalysis (s)')
ax.set_xlabel('Subject')
ax.set_title('LF/HF ratio for sitting and maths test')
ax.set_xticks(subject + width)
ax.set_xticklabels(subject)
ax.legend((rects1[0], rects2[0], rects3[0], rects4[0], rects5[0], rects6[0]), ('sitting (WT)', 'maths (WT)', 'sitting (AVG)', 'math (AVG)', 'sitting (TRUE)', 'math(TRUE)' ))

plt.figure()

# now let's do stats with no error

avg_sitting_hf = np.average(sitting_hf)
sd_sitting_hf = np.std(sitting_hf)

avg_maths_hf = np.average(maths_hf)
sd_maths_hf = np.std(maths_hf)

plt.bar([0,1],[avg_sitting_hf,avg_maths_hf],yerr=[sd_sitting_hf,sd_maths_hf],align='center', alpha=0.5, ecolor='black', capsize=10)
plt.ylim([0,hflfmax])
plt.title("Wavelet transform: sitting vs math")

plt.figure()

# and stats with error

avg_sitting_error_hf = np.average(sitting_error_hf)
sd_sitting_error_hf = np.std(sitting_error_hf)

avg_maths_error_hf = np.average(maths_error_hf)
sd_maths_error_hf = np.std(maths_error_hf)

plt.bar([0,1],[avg_sitting_error_hf,avg_maths_error_hf],yerr=[sd_sitting_error_hf,sd_maths_error_hf],align='center', alpha=0.5, ecolor='black', capsize=10)
plt.ylim([0,hflfmax])
plt.title("Two average detectors: sitting vs maths")

plt.figure()

# ground truth

avg_sitting_true_hf = np.average(sitting_true_hf)
sd_sitting_true_hf = np.std(sitting_true_hf)

avg_maths_true_hf = np.average(maths_true_hf)
sd_maths_true_hf = np.std(maths_true_hf)

plt.bar([0,1],[avg_sitting_true_hf,avg_maths_true_hf],yerr=[sd_sitting_true_hf,sd_maths_true_hf],align='center', alpha=0.5, ecolor='black', capsize=10)
plt.ylim([0,hflfmax])
plt.title("Ground truth: sitting vs math")

plt.figure()

plt.bar([0,1,2],[avg_maths_true_hf,avg_maths_error_hf,avg_maths_hf],yerr=[sd_maths_true_hf,sd_maths_error_hf,sd_maths_hf],align='center', alpha=0.5, ecolor='black', capsize=10)
plt.ylim([0,hflfmax])
plt.title("(Math task) Ground truth vs avg det vs wavelet det")

t,p = stats.ttest_rel(maths_true_hf,maths_error_hf)
print("(Math task) Ground truth vs 2 avgerage det: p=",p)

t,p = stats.ttest_rel(maths_true_hf,maths_hf)
print("(Math task) Ground truth vs wavelet det: p=",p)






plt.show()
