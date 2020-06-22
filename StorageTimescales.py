#!/usr/bin/env python

"""
Functions related to analysis of
Effects of Overcapacity on Storage Requirements, Timescles, and Costs

Applies filters to storage profiles over different timescales

"""
import numpy
from scipy import signal

import StorageEnergyProfiles as st
import Filters as fi


path = '\Insert\Your\Path\'
file_demand = 'sample_demand_MW.csv'
file_wind ='sample_wind_capacityfactor.csv'
file_pv = 'sample_pv_capacityfactor.csv'

demand = np.genfromtxt(file_demand)
wind  = np.genfromtxt(file_wind)
solar = np.genfromtxt(file_pv)

######################### NET LOAD ############################
overcaps = [1.0, 1.01, 1.05, 1.1, 1.2, 1.5, 2.0]
share_solar = np.arange(0, 1.01, 0.25)

#store net load profiles (MW)
residuals = np.zeros(shape = (len(overcaps), len(share_solar)), dtype = list) 

#store installed capacities (MW)
s_cap = np.zeros(shape = (len(overcaps), len(share_solar))) 
w_cap = np.zeros(shape = (len(overcaps), len(share_solar))) 


for i in range(0, len(overcaps)) : 
    for j in range(0, len(share_solar)):
        r = st.residual(demand_data = demand,
                        wind_cf = wind,
                        solar_cf = solar, 
                        share_vre = 1,
                        share_solar_vre_mix = share_solar[j],
                        overcapacity_factor = overcaps[i])

        residuals[i][j] = r[0]
        s_cap = r[1]
        w_cap = r[2]

######################### OVERALL STORAGE ############################
#store profiles
storage_energy_profiles = np.zeros(shape = (len(overcaps), len(share_solar)), dtype = np.ndarray)

#store energy capacity
stor_caps_TWh = np.zeros(shape = (len(overcaps), len(share_solar)))

#store power capacity
power_caps_GW = np.zeros(shape = (len(overcaps), len(share_solar)))
power_caps_ch_GW = np.zeros(shape = (len(overcaps), len(share_solar)))

e_d = 1 #discharging efficiency
e_c = 1 #charging efficiency
for i in range(0, len(overcaps)) : 
    for j in range(0, len(share_solar)):
        r = residuals[i][j]
        stor = storage_energy_profile(r, time_resolution_min = 60,
                                      efficiency_discharge = e_d,
                                      efficiency_charge = e_c)[0].reshape(-1)
        r_new = -np.diff(stor)
        
        storage_energy_profiles[i][j] = stor
        stor_caps_TWh[i][j] = max(stor)/giga_to_mega/tera_to_giga
        power_caps_GW[i][j] = (max(r_new)/giga_to_mega)
        power_caps_ch_GW[i][j] = (min(r_new)/giga_to_mega)
         


######################### STORAGE TIMESCALES ############################
#create filters
fir_0to1d = fi.daily_filter()
fir_1to7d = fi.weekly_filter()
fir_7to365d = fi.annual_filter()
fir_365over = fi.longerm_filter()


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

#apply filter to every profile
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


