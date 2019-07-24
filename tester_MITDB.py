import numpy as np
import pandas as pd
import wfdb
import _tester_utils
import pathlib
import os
from ecgdetectors import Detectors


class MITDB_test:
 

    def __init__(self, mitdb_dir):

        self.mitdb_dir = pathlib.Path(mitdb_dir)
    
    def single_classifier_test(self, detector, tolerance=0, print_results = True):
        max_delay_in_samples = 350 / 5
        dat_files = []
        for file in os.listdir(self.mitdb_dir):
            if file.endswith(".dat"):
                dat_files.append(file)
        
        mit_records = [w.replace(".dat", "") for w in dat_files]
        
        results = np.zeros((len(mit_records), 5), dtype=int)

        i = 0
        for record in mit_records:
            progress = int(i/float(len(mit_records))*100.0)
            print("Progress: %i%%" % progress)

            sig, fields = wfdb.rdsamp(self.mitdb_dir/record)
            unfiltered_ecg = sig[:, 0]  

            ann = wfdb.rdann(str(self.mitdb_dir/record), 'atr')    
            anno = _tester_utils.sort_MIT_annotations(ann)    

            r_peaks = detector(unfiltered_ecg)

            delay = _tester_utils.calcMedianDelay(r_peaks, unfiltered_ecg, max_delay_in_samples)

            TP, FP, FN = _tester_utils.evaluate_detector(r_peaks, anno, delay, tol=tolerance)
            TN = len(unfiltered_ecg)-(TP+FP+FN)

            results[i, 0] = int(record)    
            results[i, 1] = TP
            results[i, 2] = FP
            results[i, 3] = FN
            results[i, 4] = TN

            i = i+1

        if print_results:
            total_tp = np.sum(results[:, 1])
            total_fp = np.sum(results[:, 2])
            total_fn = np.sum(results[:, 3])            
            
            se = total_tp/(total_tp+total_fn)*100.0
            ppv = total_tp/(total_tp+total_fp)*100.0
            f1 = (2*total_tp)/((2*total_tp)+total_fp+total_fn)*100.0
            
            print("\nSensitivity: %.2f%%" % se)
            print("PPV: %.2f%%" % ppv)
            print("F1 Score: %.2f%%\n" % f1)
        
        return results


    def classifer_test_all(self, tolerance=0):

        det_names = ['two_average', 'matched_filter', 'swt', 'engzee', 'christov', 'hamilton', 'pan_tompkins']
        output_names = ['TP', 'FP', 'FN', 'TN']

        total_records = 0
        for file in os.listdir(self.mitdb_dir):
            if file.endswith(".dat"):
                total_records = total_records + 1

        total_results = np.zeros((total_records, 4*len(det_names)), dtype=int)

        counter = 0
        for det_name in det_names:

            print('\n'+det_name)

            result = self.single_classifier_test(_tester_utils.det_from_name(det_name, 360), tolerance=tolerance, print_results=False)
            index_labels = result[:, 0]
            result = result[:, 1:]

            total_results[:, counter:counter+4] = result

            counter = counter+4  

        col_labels = []

        for det_name in det_names:
                for output_name in output_names:
                    label = det_name+" "+output_name
                    col_labels.append(label)

        total_results_pd = pd.DataFrame(total_results, index_labels, col_labels, dtype=int)            
        total_results_pd.to_csv('results_MITDB'+'_'+_tester_utils.get_time()+'.csv', sep=',')

        return total_results_pd


    def mcnemars_test(self, detector1, detector2, tolerance=0, print_results = True):
        dat_files = []
        for file in os.listdir(self.mitdb_dir):
            if file.endswith(".dat"):
                dat_files.append(file)
        
        mit_records = [w.replace(".dat", "") for w in dat_files]

        a = 0 #neg/neg
        b = 0 #pos/neg
        c = 0 #neg/pos
        d = 0 #pos/pos
        i = 0
        for record in mit_records:
            progress = int(i/float(len(mit_records))*100)
            print("Progress: %i%%" % progress)
  
            sig, fields = wfdb.rdsamp(self.mitdb_dir/record)
            unfiltered_ecg = sig[:, 0]  

            ann = wfdb.rdann(str(self.mitdb_dir/record), 'atr')    
            anno = _tester_utils.sort_MIT_annotations(ann)    

            r_peaks1 = detector1(unfiltered_ecg)    
            r_peaks2 = detector2(unfiltered_ecg)

            for sample in anno:
                result1 = np.any(np.in1d(sample, r_peaks1))
                result2 = np.any(np.in1d(sample, r_peaks2))              

                if result1 and result2:
                    d+=1
                elif result1 and not result2:
                    b+=1
                elif not result1 and result2:
                    c+=1
                elif not result1 and not result2:
                    a+=1
            
            i+=1

        table = np.array([[a, b], [c, d]])

        if b==0 or c==0:
            Z = 0
        else:
            Z = (abs(b-c)-1)/np.sqrt(b+c)

        if print_results:
            print("\n2x2 Table")
            print(table)
            print("\nZ score: %.4f\n" % Z)
        
        return Z
