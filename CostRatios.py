#!/usr/bin/env python

"""
Functions related to analysis of
Effects of Overcapacity on Storage Requirements, Timescles, and Costs

Costs analysis
Uses installation costs ONLY
"""


def costs_by_ratio(stor_caps_TWh, s_cap, w_cap,
                   pv_per_kw = 1000,
                   cost_ratio_wind_solar = np.geomspace(0.001, 1000, 1000)    
                    cost_ratio_storage_renew = np.geomspace(0.001, 1000, 1000)):
    """
    stor_caps_TWh - storage energy capacity
    s_cap - solar PV installed capacity MW
    w_cap - wind installed capacity MW
    these are all arrays with dimensions
    i for overcapacity and
    j for share_solar
    """
    solar_cost_per_mw = pv_per_kw * 1000

#save amount of overcapacity which minimizes costs
    least_cost_overcaps = np.zeros(shape = (len(cost_ratio_storage_renew), 
                                        len(cost_ratio_wind_solar)))
#save total system costs for each
    total_costs = np.zeros(shape = (len(cost_ratio_storage_renew), 
                                        len(cost_ratio_wind_solar)),
                           dtype = np.ndarray)
#save storage costs
    stor_costs = np.zeros(shape = (len(cost_ratio_storage_renew), 
                                        len(cost_ratio_wind_solar)),
                          dtype = np.ndarray)
#save generation costs
    gen_costs = np.zeros(shape = (len(cost_ratio_storage_renew), 
                                        len(cost_ratio_wind_solar)),
                         dtype = np.ndarray)

    for c in range(0, len(cost_ratio_storage_renew)):
    for k in range(0, len(cost_ratio_wind_solar)):
        s_costs_by_overcap = s_cap.transpose()[j] * solar_cost_per_mw
#         print(s_cost)

        wind_cost_per_mw = solar_cost_per_mw * cost_ratio_wind_solar[k]
        w_costs_by_overcap = w_cap.transpose()[j] * wind_cost_per_mw
#         print(wind_cost_per_mw)
        
#         cost_renew_per_mw = ((s_costs_by_overcap + w_costs_by_overcap) / (s_cap.transpose()[j] + w_cap.transpose()[j]))
        cost_renew_per_mw = solar_cost_per_mw
#         print(cost_renew_per_mw)
        
        storage_cost_per_mwh = cost_ratio_storage_renew[c] * cost_renew_per_mw
#         print(storage_cost_per_mwh)

        stor_costs_by_overcap = (stor_caps_TWh.transpose()[j] * tera_to_giga * giga_to_mega * storage_cost_per_mwh)

        stor_costs[c][k] = stor_costs_by_overcap
        gen_costs[c][k] = s_costs_by_overcap + w_costs_by_overcap
        
        
        total_costs_by_overcap= stor_costs_by_overcap + s_costs_by_overcap + w_costs_by_overcap
        total_costs[c][k] = total_costs_by_overcap
        
        o = int(min(np.argwhere(total_costs_by_overcap == min(total_costs_by_overcap))))
        least_cost_overcaps[c][k] = overcaps[o]
    return total_costs, least_cost_overcaps
