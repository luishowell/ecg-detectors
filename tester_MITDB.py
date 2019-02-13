import numpy as np
import wfdb
import tester_utils
import pathlib
import os


class MITDB_test:
 

    def __init__(self, mitdb_dir):

        self.mitdb_dir = pathlib.Path(mitdb_dir)

    
    def diagnostic_test(self, detector, tolerance=0, print_results = True):
        dat_files = []
        for file in os.listdir(self.mitdb_dir):
            if file.endswith(".dat"):
                dat_files.append(file)
        
        mit_records = [w.replace(".dat", "") for w in dat_files]
        
        results = np.zeros((len(mit_records), 5))

        i = 0
        for record in mit_records:
            progress = int(i/float(len(mit_records))*100)
            print("Progress: %i%%" % progress)

            sig, fields = wfdb.rdsamp(self.mitdb_dir/record)
            unfiltered_ecg = sig[:, 0]  

            ann = wfdb.rdann(str(self.mitdb_dir/record), 'atr')    
            anno = tester_utils.sort_MIT_annotations(ann)    

            r_peaks = detector(unfiltered_ecg)    

            TP, FP, FN = tester_utils.evaluate_detector(r_peaks, anno, tol=tolerance)
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
            print("F1 Score: %.2f%%" % f1)
        
        return results


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
        total_anno = 0
        i = 0
        for record in mit_records:
            progress = int(i/float(len(mit_records))*100)
            print("Progress: %i%%" % progress)
  
            sig, fields = wfdb.rdsamp(self.mitdb_dir/record)
            unfiltered_ecg = sig[:, 0]  

            ann = wfdb.rdann(str(self.mitdb_dir/record), 'atr')    
            anno = tester_utils.sort_MIT_annotations(ann)    

            r_peaks1 = detector1(unfiltered_ecg)    
            r_peaks2 = detector2(unfiltered_ecg)

            for sample in anno:
                result1 = np.any(np.in1d(sample, r_peaks1))
                result2 = np.any(np.in1d(sample, r_peaks2))
                
                total_anno +=1
                if result1 and result2:
                    d+=1
                elif result1 and not result2:
                    b+=1
                elif not result1 and result2:
                    c+=1
                elif not result1 and not result2:
                    a+=1
            
            i+=1
            
        print('\nNumber of beats: %i' % total_anno)
        print('a+b+c+d: %i\n' % (a+b+c+d))

        table = np.array([[a, b], [c, d]])

        if b==0 or c==0:
            Z = 0
        else:
            Z = (abs(b-c)-1)/np.sqrt(b+c)

        if print_results:
            print("\n2x2 Table")
            print(table)
            print("\nZ score: %.4f" % Z)
        
        return Z