#!/usr/bin/env python

"""
Functions related to analysis of
Effects of Overcapacity on Storage Requirements, Timescles, and Costs

Creates net load profile
Creates storage energy profile based on a net load profile

"""
import numpy

def residual(demand_data, wind_cf = 0, solar_cf = 0, 
             share_vre = 1, share_solar_vre_mix = 0,
             overcapacity_factor = 1):
    """
    Calculates net load and required capacities for solar and wind
    based on time series data
    
    Returns r: residual net load time series (in MW if demand_data in MW)
            s: solar capacity installed (same units as demand_data)
            w: wind capacity installed (same units as demand_data)

    Inputs:
            demand_data: time series, usually MW
            wind_cf: time series capacity factor between 0 and 1
            solar_cf: time series capacity factor between 0 and 1
            share_vre: share of variable renewable energy (solar and wind) in
                        total energy mix
            share_solar_vre_mix: share of solar energy in variable renewables
                        if share_vre is 1, this is share solar energy total
                        if share_vre is 0.5, and share_solar_vre_mix= 0.5, then
                            total share_solar would be 0.25
                        1-share_solar_vre_mix = wind fraction of vre mix
            overcapacity_factor: amount of excess generation capacity
                    1, generate exactly as much energy as demand
                    1.1, capacity to generate 10% more energy than demanded
                    2, capacity to generate twice as much (100% extra)             
    """

    #data inputs
    demand_profile = np.array(demand_data)
    solar_profile = np.array(solar_cf)
    wind_profile = np.array(wind_cf)

    assert(len(demand_profile) == len(solar_profile))
    assert(len(demand_profile) == len(wind_profile))
    assert(max(wind_profile) <= 1.0)
    assert(min(wind_profile) >= 0)
    assert(max(solar_profile) <= 1.0)
    assert(min(solar_profile) >= 0)
    
    #solar capacity installed
    s = (share_vre * share_solar_vre_mix *
         np.sum(demand_profile) / np.sum(solar_profile) * overcapacity_factor) 

    #wind capacity installed
    w = (share_vre * (1-share_solar_vre_mix) *
         np.sum(demand_profile) / np.sum(wind_profile) * overcapacity_factor)

    #residual net load
    r = (demand_profile - (s * solar_profile + w * wind_profile)).reshape(-1)
    
    return r, s, w



def storage_energy_profile(r, time_resolution_min = 60.0,
                           efficiency_discharge = 1.0, efficiency_charge = 1.0):
    """
    Inputs:
        r: residual net load profile
        efficiency: efficiency of storage
                    if 1, this is how much energy needs to be shifted in time
        time_resolution_min = time resolution of net load in MINUTES

    Returns:  if r was in MW, end units are in MWh
        stored: storage energy profile time series
        spilled: time series of curtailed (not stored or demanded) electricity
        lost_to_ineff: time series of energy lost to inefficiency in the storage
    """
    
    #CHECK ENOUGH ENERGY IN SYSTEM
    #more supplied, even accounting for inefficiency, than demanded
    #use <1W because some zero floats over zero
    assert(sum(r*(r<0))*efficiency_discharge + sum(r*(r>0)) < 0.001)
    
    
    #find point of maximum cumulative excess demand -- start counting from there
    #this is when storage can start filling after discharging to meet
    #max cumulative demand, avoids need for multiple looping
    m = np.argwhere(np.cumsum(r) == np.max(np.cumsum(r))).reshape(-1)[0]
    r_shifted = np.concatenate((r[m:], r[:m]))
    
    #backwards residual demand
    #because integral progresses backwards through time
    rev = r_shifted[::-1]
    
    #places to save profiles of stored energy and spilled energy
    stored = np.zeros(shape = (len(rev), 1))
    spilled = np.zeros(shape = (len(rev), 1))
    lost_to_ineff = np.zeros(shape = (len(rev), 1))


    #initial time step
    i = 0
    #if net load is excess demand
    if rev[i] > 0:
        change = rev[i] * time_resolution_min/60.0 / efficiency_discharge

    #if excess supply
    else:
        change = 0
        
    stored[i] = change
    lost_to_ineff[i] = change*(1-efficiency_discharge)
    spilled[i] = rev[i] * time_resolution_min/60.0 - change + lost_to_ineff[i]
    
    #step through time, forward in rev (backward in r)
    for i in range(0, len(rev)):
        if rev[i] <0:
            efficiency = efficiency_charge
        else:
            efficiency = 1/efficiency_discharge
            #change in storage is 
        change = max(-stored[i-1],
                         rev[i] * time_resolution_min/60.0 / efficiency)
            
            #stored is previously stored + change
        stored[i] = stored[i-1] + change
            
            #amount lost to inefficiency,
        lost_to_ineff[i] = max(-change*(1-efficiency), 0)
            
            #spilled is excess supply not stored or lost to ineff
        spilled[i] = (rev[i] * time_resolution_min/60.0 - change
                          - lost_to_ineff[i])
            
    #return to original direction
    stored = stored[::-1] 
    spilled = spilled[::-1]
    lost_to_ineff = lost_to_ineff[::-1]
    
    #return to original times
    stored = np.concatenate((stored[len(r)-m:],
                             stored[:len(r)-m]))
    spilled = np.concatenate((spilled[len(r)-m:],
                              spilled[:len(r)-m]))
    lost_to_ineff = np.concatenate((lost_to_ineff[len(r)-m:],
                                    lost_to_ineff[:len(r)-m]))
    
    return stored, spilled, lost_to_ineff 
