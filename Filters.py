#!/usr/bin/env python

"""
Functions related to analysis of
Effects of Overcapacity on Storage Requirements, Timescles, and Costs

Create FIR filters over different timescales

"""
import numpy
from scipy import signal

######################### CREATE FIR FILTERS #########################
#<1 DAY FILTER
d = 1

downsample_rate_0to1d = 1 
sample_rate_0to1d = 24*365 /downsample_rate_0to1d 
num_samples_0to1d = 24*365*37

nyq_rate_0to1d = sample_rate_0to1d / 2.0
width_0to1d = 5/ nyq_rate_0to1d
ripple_db = 60
N_ord_0to1d, beta_0to1d = signal.kaiserord(ripple_db, width_0to1d)

fc_0to1d = sample_rate_0to1d / (24*d/downsample_rate_0to1d)

fir_0to1d = signal.firwin(N_ord_0to1d, fc_0to1d/nyq_rate_0to1d,
                          pass_zero = False)




#1-7 DAY FILTER
d1 = 1
d7 = 7

downsample_rate_1to7d = 10 
sample_rate_1to7d = 24*365 /downsample_rate_1to7d
num_samples_1to7d = 24*365*37 

nyq_rate_1to7d = sample_rate_1to7d / 2.0
width_1to7d = 2/ nyq_rate_1to7d
ripple_db = 60
N_ord_1to7d, beta_1to7d = signal.kaiserord(ripple_db, width_1to7d)

fc1_1to7d = sample_rate_1to7d / (24*d1/downsample_rate_1to7d)
fc2_1to7d = sample_rate_1to7d / (24*d7/downsample_rate_1to7d)

low_pass1 = signal.firwin(N_ord_1to7d, fc1_1to7d/nyq_rate_1to7d,
                          pass_zero = True)
high_pass7 = signal.firwin(N_ord_1to7d, fc2_1to7d/nyq_rate_1to7d,
                           pass_zero = False)

fir_1to7d = np.convolve(low_pass1, high_pass7)




#7-365 DAY FILTER
d7 = 7
d365 = 365

downsample_rate_7to365d =  50
sample_rate_7to365d = 24*365 /downsample_rate_7to365d 
num_samples_7to365d = 24*365*37

nyq_rate_7to365d = sample_rate_7to365d / 2.0
width_7to365d = 1/ nyq_rate_7to365d
ripple_db = 60
N_ord_7to365d, beta_7to365d = signal.kaiserord(ripple_db, width_7to365d)

fc1_7to365d = sample_rate_7to365d / (24*d7/downsample_rate_7to365d)
fc2_7to365d = sample_rate_7to365d / (24*d365/downsample_rate_7to365d)

low_pass7 = signal.firwin(N_ord_7to365d, fc1_7to365d/nyq_rate_7to365d,
                          pass_zero = True, 
                         window = ('kaiser', beta_7to365d))
high_pass365 = signal.firwin(N_ord_7to365d, fc2_7to365d/nyq_rate_7to365d,
                             pass_zero = False,
                            window = ('kaiser', beta_7to365d))

fir_7to365d = np.convolve(low_pass7, high_pass365)




#>365 DAY FILTER
d365 = 365

downsample_rate_365over = 50 #downsampling rate
sample_rate_365over = 24*365 /downsample_rate_365over #1 #2
num_samples_365over = 24*365*37 #/downsample_rate

nyq_rate_365over = sample_rate_365over / 2.0
width_365over = 1/ nyq_rate_365over
ripple_db = 60
N_ord_365over, beta_365over = signal.kaiserord(ripple_db, width_365over)

fc_365over = sample_rate_365over / (24*d365/downsample_rate_365over)

fir_365over = signal.firwin(N_ord_365over, fc_365over/nyq_rate_365over, pass_zero = True)



######################### APPLY FILTERS TO OVERALL STORAGE ##############
overcaps = [1.0, 1.01, 1.05, 1.1, 1.2, 1.5, 2.0]
share_solar = np.arange(0, 1.01, 0.25)

#store energy profile components
filts_0to1 = np.zeros(shape = (len(overcaps), len(share_solar)),
                      dtype = np.ndarray)
filts_1to7 = np.zeros(shape = (len(overcaps), len(share_solar)),
                      dtype = np.ndarray)
filts_7to365 = np.zeros(shape = (len(overcaps), len(share_solar)),
                        dtype = np.ndarray)
filts_365over = np.zeros(shape = (len(overcaps), len(share_solar)),
                         dtype = np.ndarray)

#store energy capacity
sizes_twh_0to1 = np.zeros(shape = (len(overcaps), len(share_solar)))
sizes_twh_1to7 = np.zeros(shape = (len(overcaps), len(share_solar)))
sizes_twh_7to365 = np.zeros(shape = (len(overcaps), len(share_solar)))
sizes_twh_365over = np.zeros(shape = (len(overcaps), len(share_solar)))

#store power profiles
power_0to1 = np.zeros(shape = (len(overcaps), len(share_solar)),
                      dtype = np.ndarray)
power_1to7 = np.zeros(shape = (len(overcaps), len(share_solar)),
                      dtype = np.ndarray)
power_7to365 = np.zeros(shape = (len(overcaps), len(share_solar)),
                        dtype = np.ndarray)
power_365over = np.zeros(shape = (len(overcaps), len(share_solar)),
                         dtype = np.ndarray)


#store power capacity
disch_0to1 = np.zeros(shape = (len(overcaps), len(share_solar)))
disch_1to7 = np.zeros(shape = (len(overcaps), len(share_solar)))
disch_7to365 = np.zeros(shape = (len(overcaps), len(share_solar)))
disch_365over = np.zeros(shape = (len(overcaps), len(share_solar)))

ch_0to1 = np.zeros(shape = (len(overcaps), len(share_solar)))
ch_1to7 = np.zeros(shape = (len(overcaps), len(share_solar)))
ch_7to365 = np.zeros(shape = (len(overcaps), len(share_solar)))
ch_365over = np.zeros(shape = (len(overcaps), len(share_solar)))

for i in range(0, len(overcaps)) : 
    for j in range(0, len(share_solar)): 
        sig = storage_energy_profiles[i][j] /giga_to_mega/tera_to_giga
        
        x_0to1 = sig[::downsample_rate_0to1d]
        filt_stor_prof_0to1 = signal.filtfilt(fir_0to1d, 1.0, x_0to1)
        filts_0to1[i][j] = filt_stor_prof_0to1
        sizes_twh_0to1[i][j] = max(filt_stor_prof_0to1) - min(filt_stor_prof_0to1)
        power_0to1[i][j] = np.diff(filts_0to1[i][j]) / downsample_rate_0to1d * tera_to_giga
        disch_0to1[i][j] = max(np.diff(filts_0to1[i][j]) / downsample_rate_0to1d * tera_to_giga)
        ch_0to1[i][j] = min(np.diff(filts_0to1[i][j]) / downsample_rate_0to1d * tera_to_giga)

        x_1to7 = sig[::downsample_rate_1to7d]
        filt_stor_prof_1to7 = signal.filtfilt(fir_1to7d, 1.0, x_1to7)
        filts_1to7[i][j] = filt_stor_prof_1to7
        sizes_twh_1to7[i][j] = max(filt_stor_prof_1to7) - min(filt_stor_prof_1to7)
        power_1to7[i][j] = np.diff(filts_1to7[i][j]) / downsample_rate_1to7d * tera_to_giga
        disch_1to7[i][j] = max(np.diff(filts_1to7[i][j]) / downsample_rate_1to7d * tera_to_giga)       
        ch_1to7[i][j] = min(np.diff(filts_1to7[i][j]) / downsample_rate_1to7d * tera_to_giga)

        x_7to365 = sig[::downsample_rate_7to365d]
        filt_stor_prof_7to365 = signal.filtfilt(fir_7to365d, 1.0, x_7to365)
        filts_7to365[i][j] = filt_stor_prof_7to365
        sizes_twh_7to365[i][j] = max(filt_stor_prof_7to365) - min(filt_stor_prof_7to365)
        power_7to365[i][j] = np.diff(filts_7to365[i][j]) / downsample_rate_7to365d * tera_to_giga
        disch_7to365[i][j] = max(np.diff(filts_7to365[i][j]) / downsample_rate_7to365d * tera_to_giga)
        ch_7to365[i][j] = min(np.diff(filts_7to365[i][j]) / downsample_rate_7to365d * tera_to_giga)

        x_365over = sig[::downsample_rate_365over]
        filt_stor_prof_365over = signal.filtfilt(fir_365over, 1.0, x_365over)
        filts_365over[i][j] = filt_stor_prof_365over
        sizes_twh_365over[i][j] = max(filt_stor_prof_365over) - min(filt_stor_prof_365over)
        power_365over[i][j] = np.diff(filts_365over[i][j]) / downsample_rate_365over * tera_to_giga
        disch_365over[i][j] = max(np.diff(filts_365over[i][j]) / downsample_rate_365over * tera_to_giga)
        ch_365over[i][j] = min(np.diff(filts_365over[i][j]) / downsample_rate_365over * tera_to_giga)

