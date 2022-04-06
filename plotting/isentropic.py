"""
# Load mapfig class
# Load data from GEFS (control member?)

# Plot pressure on potential temperature surfaces, overlay spec. hum.
# Pressure, wind, mixing ratio (and RH?)
# 280 K to 310 K, every five, but 290-300 is every 2 K
# lat/lon with contours, barbs, contour-fill.

# Plot cross-sections? 
# Y-axis is pressure, x-axis is distance, contours are isentropes

# Get nicer font installed for maps

Using GEFS, we have in pgrb2b:
    * Montgomery_stream_function_isentrope_ens
    * Potential_vorticity_isentrope_ens
    * Temperature_isentrope_ens
    * u-component_of_wind_isentrope_ens
    * v-component_of_wind_isentrope_ens
    * Potential_temperature_sigma_ens
    * Cloud_mixing_ratio_isobaric_ens
    * Relative_humidity_hybrid_ens
    * Relative_humidity_isobaric_ens
    * Relative_humidity_sigma_ens

In pgrb2s:
    * Relative_humidity_height_above_ground_ens
    * Temperature_height_above_ground_ens
    * u-component_of_wind_height_above_ground_ens
    * v-component_of_wind_height_above_ground_ens

For plotting cross-sections,
    * Pressure_surface_ens (2s)
    * Geopotential_height_surface_ens (2b)
    * Temperature_surface_ens (2b)
    * 

Use MetPy.

https://www.meted.ucar.edu/labs/synoptic/isentropic_analysis/print.php

"""

import os
import pdb

import numpy as np
import metpy
from metpy.plots import add_timestamp

# from valpomet.plotting.xsection import XSection
from valpomet.plotting.birdseye import BirdsEye


def plot_isentropic_xsection(pot_temp,pressure_lvs,sfc_pressure,latA,
                lonA,latB,lonB,):
    # pot_temp should be 2-D, sfc_pressure is 1D
    # Is pressure_lvs 1-D or 2-D to match the data?
    return

def plot_isentropic_birdseye(pressure,wind,mixing_ratio,RH,label_K,
                        lats,lons):
    return
