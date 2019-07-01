import numpy as np
from tester_MITDB import MITDB_test
from tester_GUDB import GUDB_test
from ecgdetectors import Detectors


# MIT-BIH database testing
mit_test = MITDB_test(r'C:\Users\Luis\Documents\MITDB')
mit_detectors = Detectors(360)

# test single detector
matched_filter_mit = mit_test.single_classifier_test(mit_detectors.matched_filter_detector, tolerance=0, print_results=True)
np.savetxt('matched_filter_mit.csv', matched_filter_mit, fmt='%i', delimiter=',')

# test all detectors on MITDB, will save results to csv, will take some time
mit_results = mit_test.classifer_test_all()

# McNemars stats test
Z_value_mit = mit_test.mcnemars_test(mit_detectors.swt_detector, mit_detectors.two_average_detector, print_results = True)


# GUDB database testing
gu_test = GUDB_test()
gu_detectors = Detectors(250)

swt_gudb = gu_test.single_classifier_test(gu_detectors.swt_detector, tolerance=0, config='chest_strap')

gu_results = gu_test.classifer_test_all(tolerance=0, config='chest_strap')

Z_value_gu = gu_test.mcnemars_test(gu_detectors.swt_detector, gu_detectors.two_average_detector, print_results = True)