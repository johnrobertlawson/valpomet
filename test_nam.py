""" Testing loading and plotting of NAM data.
"""
import os
import pdb
import itertools

import numpy as np
import matplotlib as mpl
mpl.use("agg")

from valpomet.modeltypes.nam import NAM
from valpomet.modeltypes.ensemble import Ensemble
from valpomet.plotting.birdseye import BirdsEye
from valpomet.plotting.isentropic import plot_isentropic_birdseye

# GEFS.download_data()
data_root = '/data/ldmdata/model/nam'
fpath = NAM.create_nam_fpath(data_root)

if True:
    # 1 - BASIC
    do_test_1 = False
    # 2 - Pressure change
    do_test_2 = True
    # 3 - Comapring products' MSLP change
    # do_test_3 = True
    # 4 - 
    # do_test_4 = True
    # 5 - isentropes, birdseye
    do_test_5 = True
    # 6 - isentropes, cross-section
    do_test_6 = True


    nam = NAM(fpath)
    # TEST 1 - BASIC
    if do_test_1:
        vrbl = "Temperature_isobaric"
        # m_a = "Indiana"
        m_a = "CONUS"

        # Shape of data, lats, lons
        data,units,lats,lons,z_coords = nam.get(vrbl,return_latlon=True)
        # z_coords are from low to high
        # (29,29,428,614)
        FIG = BirdsEye(lats,lons,map_area="Indiana",do_faster_contourf=False)
        # Pick 10th level - not sure what that is
        FIG.contourf(data[3,10,:,:])
        FIG.contour(data[3,10,:,:])
        FIG.save("./test/nam_april2022_test1.png")
        pdb.set_trace()

    # TEST 2 - PRESSURE CHANGE 
    if do_test_2:
        fhrs = nam.forecast_hours.astype(int)
        all_arr = np.zeros([fhrs.size,428,614])

        # mslp_vrbl = 'Pressure_reduced_to_MSL_msl'

        # This is the better product:
        mslp_vrbl = 'MSLP_Eta_model_reduction_msl'
        # (29,428,614)

        # https://unidata.github.io/MetPy/latest/examples/calculations/Smoothing.html
        # smooth_n_point, two passes at 9 pixels is KG's method


        for n,fhr in enumerate(fhrs):
            data,units,lats,lons,z_coords = nam.get(mslp_vrbl,return_latlon=True,
                                        smooth=2,
                                        )
            data = data[n,:,:]/100
            all_arr[n,:,:] = data
            
        # 3-hourly
        data_diff = np.diff(all_arr,axis=0)

        # 12-hourly
        # dd_12h = np.diff(all_arr,axis=0,)

        # From b
        # (1,1,361,720)
        abs_levels = np.arange(940,1060,4)
        diff_levels = np.arange(-10,11,1)

        # m_a = "Indiana"
        m_a = "CONUS"

        FIG = BirdsEye(lats,lons,map_area=m_a,do_faster_contourf=False,
                            ocean_color="lightblue",figsize=(10,7),)
        # FIG.contourf(all_arr[4,:,:],levels=abs_levels)
        FIG.contour(all_arr[4,:,:],levels=abs_levels)
        FIG.save("./test/nam_april2022_test2c_sm.png")
        del FIG

        FIG = BirdsEye(lats,lons,map_area=m_a,do_faster_contourf=False,
                        do_US_counties=False)
        FIG.contourf(data_diff[5,:,:],levels=diff_levels,cmap=mpl.cm.bwr)
        FIG.contour(data_diff[5,:,:],levels=diff_levels)
        FIG.save("./test/nam_april2022_test2d_sm.png")
        pdb.set_trace()


    if do_test_5:
        pass
    # TEST 3 - ISENTROPIC BIRDSEYE



    if do_test_6:
        pass
    # TEST 4 - ISENTROPIC XSECTION

    pdb.set_trace()
