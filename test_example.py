import numpy as np
from tester_MITDB import MITDB_test
from ecgdetectors import Detectors


fs = 360
detectors = Detectors(fs)

# MIT-BIH database testing
mit_test = MITDB_test(r'\MITDB_dir')

results = mit_test.classifier_test(detectors.matched_filter_detector, tolerance=0, print_results=True)
np.savetxt('MITDB_results.csv', results, fmt='%i', delimiter=',')

Z_value = mit_test.mcnemars_test(detectors.swt_detector, detectors.two_average_detector, print_results = True)

