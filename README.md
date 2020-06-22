# overcapacity-storage-timescales
This repository contains code related to the paper "Effects of Overcapacity on Storage Requirements, Timescales, and Costs". 

StorageEnergyProfiles.py
Includes functions for calculating net load profile and overall storage energy profile

Filters.py
Includes funcitons for making FIR filters for daily, weekly, annual, and longer timescales
These can be applied to the overall storage energy profile to analyze cycling frequency and estimate storage over different timescales

StorageTimescales.py
Applies functions from StorageEnergyProfiles.py and Filters.py using demand data (MW) and solar and wind capacity factor profiles
