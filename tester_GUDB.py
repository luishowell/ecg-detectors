import numpy as np
import pandas as pd
import _tester_utils
import pathlib
from ecgdetectors import Detectors

current_dir = pathlib.Path(__file__).resolve()
data_dir = str(pathlib.Path(current_dir).parents[1]/'dataset_716'/'experiment_data')
code_dir = str(pathlib.Path(current_dir).parents[1]/'dataset_716'/'example_code')

import sys
sys.path.insert(0, code_dir)
from ecg_gla_database import Ecg


class GUDB_test:
 
    
    def single_classifier_test(self, detector, tolerance=0, config="chest_strap", print_results = True):

        max_delay_in_samples = 250 / 5

        total_subjects = Ecg.total_subjects

        results = np.zeros((total_subjects, (4*len(Ecg.experiments))+1), dtype=int)

        for subject_number in range(0, total_subjects):
            progress = int(subject_number/float(total_subjects)*100.0)
            print("Progress: %i%%" % progress)

            results[subject_number, 0] = subject_number
            exp_counter = 1
            for experiment in Ecg.experiments:
                
                ecg_class = Ecg(data_dir, subject_number, experiment)

                anno_exists = False
                if config=="chest_strap" and ecg_class.anno_cs_exists:
                    unfiltered_ecg = ecg_class.cs_V2_V1                   
                    anno = ecg_class.anno_cs
                    anno_exists = True
                elif config=="loose_cables" and ecg_class.anno_cables_exists:
                    unfiltered_ecg = ecg_class.einthoven_II 
                    anno = ecg_class.anno_cables
                    anno_exists = True
                elif config!="chest_strap" and config!="loose_cables":
                    raise RuntimeError("Config argument must be chest_strap or loose_cables!")
                    return results

                if anno_exists:                  

                    r_peaks = detector(unfiltered_ecg)

                    delay = _tester_utils.calcMedianDelay(r_peaks, unfiltered_ecg, max_delay_in_samples)

                    TP, FP, FN = _tester_utils.evaluate_detector(r_peaks, anno, delay, tol=tolerance)
                    TN = len(unfiltered_ecg)-(TP+FP+FN)

                    results[subject_number, exp_counter] = TP
                    results[subject_number, exp_counter+1] = FP
                    results[subject_number, exp_counter+2] = FN
                    results[subject_number, exp_counter+3] = TN

                exp_counter = exp_counter+4

        if print_results:
            total_tp = np.sum(np.vstack((results[:, 1],results[:, 5],results[:, 9],results[:, 13],results[:, 17])))
            total_fp = np.sum(np.vstack((results[:, 2],results[:, 6],results[:, 10],results[:, 14],results[:, 18])))
            total_fn = np.sum(np.vstack((results[:, 3],results[:, 7],results[:, 11],results[:, 15],results[:, 19])))  
            
            se = total_tp/(total_tp+total_fn)*100.0
            ppv = total_tp/(total_tp+total_fp)*100.0
            f1 = (2*total_tp)/((2*total_tp)+total_fp+total_fn)*100.0
            
            print("\nSensitivity: %.2f%%" % se)
            print("PPV: %.2f%%" % ppv)
            print("F1 Score: %.2f%%\n" % f1)

        return results


    def classifer_test_all(self, tolerance=0, config="chest_strap"):

        det_names = ['two_average', 'matched_filter', 'swt', 'engzee', 'christov', 'hamilton', 'pan_tompkins']
        output_names = ['TP', 'FP', 'FN', 'TN']

        total_results = np.zeros((Ecg.total_subjects, 4*len(Ecg.experiments)*len(det_names)), dtype=int)

        counter = 0
        for det_name in det_names:

            print('\n'+det_name)

            result = self.single_classifier_test(_tester_utils.det_from_name(det_name, 250), tolerance=tolerance, config=config, print_results=False)
            result = result[:, 1:]

            total_results[:, counter:counter+(4*len(Ecg.experiments))] = result

            counter = counter+(4*len(Ecg.experiments))        

        index_labels = np.arange(Ecg.total_subjects)
        col_labels = []

        for det_name in det_names:
            for experiment_name in Ecg.experiments:
                for output_name in output_names:
                    label = det_name+" "+experiment_name+" "+output_name
                    col_labels.append(label)

        total_results_pd = pd.DataFrame(total_results, index_labels, col_labels, dtype=int)            
        total_results_pd.to_csv('results_GUDB_'+config+'_'+_tester_utils.get_time()+'.csv', sep=',')

        return total_results_pd

    
    def mcnemars_test(self, detector1, detector2, config="chest_strap", tolerance=0, print_results = True):

        total_subjects = Ecg.total_subjects

        a = 0 #neg/neg
        b = 0 #pos/neg
        c = 0 #neg/pos
        d = 0 #pos/pos

        for subject_number in range(0, total_subjects):
            progress = int(subject_number/float(total_subjects)*100.0)
            print("Progress: %i%%" % progress)

            for experiment in Ecg.experiments:
                
                ecg_class = Ecg(data_dir, subject_number, experiment)

                anno_exists = False
                if config=="chest_strap" and ecg_class.anno_cs_exists:
                    unfiltered_ecg = ecg_class.cs_V2_V1                   
                    anno = ecg_class.anno_cs
                    anno_exists = True
                elif config=="loose_cables" and ecg_class.anno_cables_exists:
                    unfiltered_ecg = ecg_class.einthoven_II 
                    anno = ecg_class.anno_cables
                    anno_exists = True
                elif config!="chest_strap" and config!="loose_cables":
                    print("Config argument must be chest_strap or loose_cables!")
                    return -1

                if anno_exists:                  

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
