import numpy as np
import pywt
import pathlib
import scipy.signal as signal
from biosppy import ecg


class Detectors:
    
    # specify the path to the data, the subject number and the experiment
    def __init__(self, sampling_frequency):

        self.fs = sampling_frequency


    def hamilton_detector(self, unfiltered_ecg):
        r_peaks = ecg.hamilton_segmenter(unfiltered_ecg, sampling_rate=self.fs)
        return r_peaks[0]

    
    def christov_detector(self, unfiltered_ecg):
        r_peaks = ecg.christov_segmenter(unfiltered_ecg, sampling_rate=self.fs)
        return r_peaks[0]

    
    def engzee_detector(self, unfiltered_ecg):
        r_peaks = ecg.engzee_segmenter(unfiltered_ecg, sampling_rate=self.fs)
        return r_peaks[0]

    
    def matched_filter_detector(self, unfiltered_ecg):

        current_dir = pathlib.Path(__file__).resolve()
        
        if self.fs == 250:
            template_dir = current_dir.parent/'templates'/'template_250hz.csv'
            template = np.loadtxt(template_dir)
        elif self.fs == 360:
            template_dir = current_dir.parent/'templates'/'template_360hz.csv'
            template = np.loadtxt(template_dir)
        else:
            print('\n!!No template for this frequency!!\n')

        f0 = 0.5/self.fs
        f1 = 45/self.fs

        b, a = signal.butter(2, [f0*2, f1*2], btype='bandpass')

        prefiltered_ecg = signal.lfilter(b, a, unfiltered_ecg)

        matched_coeffs = template[::-1]  #time reversing template

        detection = signal.lfilter(matched_coeffs, 1, prefiltered_ecg)  # matched filter FIR filtering
        squared = detection*detection  # squaring matched filter output
        #squared = normalise(squared)

        squared_peaks = panPeakDetect(squared, self.fs)
  
        r_peaks = searchBack(squared_peaks, unfiltered_ecg, len(template))

        return r_peaks

    
    def swt_detector(self, unfiltered_ecg):

        padding = -1
        swt_level = 3
        for i in range(1000):
            if (len(unfiltered_ecg)+i)%2**swt_level == 0:
                #print("Padded by %i\n" % i)
                padding = i
                break

        if padding > 0:
            unfiltered_ecg = np.pad(unfiltered_ecg, (0, padding), 'edge')
        elif padding == -1:
            print("Padding greater than 1000 required\n")    

        swt_ecg = pywt.swt(unfiltered_ecg, 'db3', level=swt_level)
        swt_ecg = np.array(swt_ecg)
        swt_ecg = swt_ecg[0, 1, :]

        squared = swt_ecg*swt_ecg
        #squared = normalise(squared)

        N = int(0.12*self.fs)
        mwa = MWA(squared, N)

        mwa_peaks = panPeakDetect(mwa, self.fs)

        r_peaks = searchBack(mwa_peaks, unfiltered_ecg, N)

        return r_peaks


    def pan_tompkins_detector(self, unfiltered_ecg):
        
        f1 = 5/self.fs
        f2 = 15/self.fs

        b, a = signal.butter(1, [f1*2, f2*2], btype='bandpass')

        filtered_ecg = signal.lfilter(b, a, unfiltered_ecg)        

        diff = np.diff(filtered_ecg) 

        squared = diff*diff

        #squared = normalise(squared)

        N = int(0.12*self.fs)
        mwa = MWA(squared, N)

        mwa_peaks = panPeakDetect(mwa, self.fs)

        r_peaks = searchBack(mwa_peaks, unfiltered_ecg, N)

        return r_peaks


    def two_average_detector(self, unfiltered_ecg):
        
        f1 = 8/self.fs
        f2 = 20/self.fs

        b, a = signal.butter(2, [f1*2, f2*2], btype='bandpass')

        filtered_ecg = signal.lfilter(b, a, unfiltered_ecg)

        window1 = int(0.12*self.fs)
        mwa_qrs = MWA(abs(filtered_ecg), window1)

        mwa_beat = MWA(abs(filtered_ecg), self.fs)

        blocks = np.zeros(len(unfiltered_ecg))
        for i in range(len(mwa_qrs)):
            if mwa_qrs[i] > mwa_beat[i]:
                blocks[i] = 1
            else:
                blocks[i] = 0

        block_sections = []
        pre_offset = int(15*self.fs/250)
        for i in range(1, len(blocks)):
            if blocks[i-1] == 0 and blocks[i] == 1:
                start_block = i-pre_offset
            elif blocks[i-1] == 1 and blocks[i] == 0:
                end_block = i-1
                if end_block-start_block<window1:
                    blocks[start_block:end_block+1] = 0
                else:
                    blocks[start_block:end_block+1] = 1
                    block_sections.append([start_block, end_block])

        r_peaks = []
        for i in range(len(block_sections)):
            start_block = block_sections[i][0]
            end_block = block_sections[i][1]
            ecg_section = unfiltered_ecg[start_block:end_block]
            r_peaks.append(np.argmax(ecg_section)+start_block)

        r_peaks = np.array(r_peaks)

        return(r_peaks)


def MWA(input_array, window_size):

    mwa = np.zeros(len(input_array))
    for i in range(len(input_array)):
        if i < window_size:
            section = abs(input_array[0:i])
        else:
            section = abs(input_array[i-window_size:i])
        
        if i!=0:
            mwa[i] = np.mean(section)
        else:
            mwa[i] = input_array[i]

    return mwa


def normalise(input_array):

    output_array = (input_array-np.min(input_array))/(np.max(input_array)-np.min(input_array))

    return output_array


def searchBack(detected_peaks, unfiltered_ecg, search_samples):

    r_peaks = []
    window = search_samples

    for i in detected_peaks:
        if i<window:
            section = unfiltered_ecg[:i]
            r_peaks.append(np.argmax(section))
        else:
            section = unfiltered_ecg[i-window:i]
            r_peaks.append(np.argmax(section)+i-window)

    return np.array(r_peaks)


def panPeakDetect(detection, fs):    

    peaks, _ = signal.find_peaks(detection, distance=(50*fs/360))

    min_distance = int((60.0/200.0)*fs)

    signal_peaks = []
    noise_peaks = []

    SPKI = 0.0
    NPKI = 0.0

    threshold_I1 = 0.0
    threshold_I2 = 0.0

    RR_missed = 0
    index = 0
    indexes = []

    missed_peaks = []
    for peak in peaks:

        if detection[peak] > threshold_I1:

            try:
                if peak-signal_peaks[-1]>min_distance:
                    signal_peaks.append(peak)
                    indexes.append(index)
                    SPKI = 0.125*detection[signal_peaks[-1]] + 0.875*SPKI
                    if RR_missed!=0:
                        if signal_peaks[-1]-signal_peaks[-2]>RR_missed:
                            missed_section_peaks = peaks[indexes[-2]+1:indexes[-1]]
                            missed_section_peaks2 = []
                            for missed_peak in missed_section_peaks:
                                if missed_peak-signal_peaks[-2]>min_distance and signal_peaks[-1]-missed_peak>min_distance and detection[missed_peak]>threshold_I2:
                                    missed_section_peaks2.append(missed_peak)

                            if len(missed_section_peaks2)>0:           
                                missed_peak = missed_section_peaks2[np.argmax(detection[missed_section_peaks2])]
                                missed_peaks.append(missed_peak)
                                signal_peaks.append(signal_peaks[-1])
                                signal_peaks[-2] = missed_peak
    

                elif detection[peak]>detection[signal_peaks[-1]]:
                    signal_peaks[-1] = peak
                    indexes[-1] = index
            except:
                signal_peaks.append(peak)
                indexes.append(index)
                SPKI = 0.125*detection[signal_peaks[-1]] + 0.875*SPKI
        
        else:
            noise_peaks.append(peak)
            NPKI = 0.125*detection[noise_peaks[-1]] + 0.875*NPKI
        
        threshold_I1 = NPKI + 0.25*(SPKI-NPKI)
        threshold_I2 = 0.5*threshold_I1

        if len(signal_peaks)>8:
            RR = np.diff(signal_peaks[-9:])
            RR_ave = int(np.mean(RR))
            RR_missed = int(1.66*RR_ave)

        index = index+1

    return signal_peaks