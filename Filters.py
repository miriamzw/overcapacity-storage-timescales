#!/usr/bin/env python

"""
Functions related to analysis of
Effects of Overcapacity on Storage Requirements, Timescles, and Costs

Create FIR filters over different timescales

"""
import numpy
from scipy import signal

def daily_filter():
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

    return fir_0to1d

def weekly_filter():
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
    return fir_1to7d


def annual_filter():
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
    return fir_7to365d


def longterm_filter():
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
    return fir_365over

