""" Testing loading and plotting of NAM data.
"""
import os
import pdb
import itertools
import datetime

import numpy as np
import metpy
from metpy.units import units as mpunits
# from metpy.calc import 
import matplotlib as mpl
mpl.use("agg")

from valpomet.modeltypes.nam import NAM
from valpomet.modeltypes.ensemble import Ensemble
from valpomet.plotting.birdseye import BirdsEye
from valpomet.plotting.isentropic import plot_isentropic_birdseye
import valpomet.utils.utils as utils

# GEFS.download_data()
data_root = '/data/ldmdata/model/nam'
fpath = NAM.create_nam_fpath(data_root)

if True:
    # 1 - BASIC
    do_test_1 = False
    # 2 - Pressure change
    do_test_2 = False
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
        isen_lvs = [280,285,290,293,296,300,305,310] * mpunits.kelvin
        # nam_data = nam.ds.set_coords(["longitude","latitude"])
        # nam_data = nam.ds.set_coords(["longitude","latitude","isobaric","isobaric2"])
        nam_data = nam.ds.set_coords(["longitude","latitude","isobaric2"])
        # P_lvs = nam_data["isobaric2"]
        P_lvs = nam_data["Relative_humidity_isobaric"
                    ].metpy.vertical.values*mpunits.Pa
        # nam_data = nam.xrobj.squeeze().set_coords(["longitude","latitude"])
        _temp = "Temperature_isobaric"
        _u = "u-component_of_wind_isobaric"
        _v = "v-component_of_wind_isobaric"
        # .METPY.sel(vertical=[50000,"Pa"]
        # .sel() can do timestamps in the pandas format or datetime object ("O")
        _z = "Geopotential_height_isobaric"
        _RH = "Relative_humidity_isobaric"
        timesel = nam.get_datetime_from_idx(1)
        P_array = np.zeros([len(P_lvs),428,614])
        for x,y in itertools.product(np.arange(428),np.arange(614)):
        # for x,y in itertools.product([np.arange(428),np.arange(614)]):
            P_array[:,int(x),int(y)] = P_lvs
        
        # pdb.set_trace()
        gkg = mpunits.gram / mpunits.kilogram
        spechum = metpy.calc.specific_humidity_from_mixing_ratio(
                    metpy.calc.mixing_ratio_from_relative_humidity(
                    # nam_data["isobaric2"],#.isel(time=0),
                    # nam_data["Temperature_isobaric"].metpy.vertical,
                    # nam_data["Relative_humidity_isobaric"].metpy.vertical,
                    # P_lvs*mpunits.Pa,
                    P_array*mpunits.Pa,
                    nam_data["Temperature_isobaric"].metpy.sel(
                        vertical=P_lvs,time=timesel).values*mpunits.K,
                    nam_data["Relative_humidity_isobaric"].metpy.sel(
                        # vertical=P_lvs,time=timesel).values*mpunits.percent,
                        vertical=P_lvs,time=timesel).values*mpunits.percent,
                        )
                    )*gkg

        temp = nam_data[_temp].metpy.sel(vertical=P_lvs,time=timesel)
        # temp = nam_data[_temp].isel(time=0).metpy.sel(vertical=P_lvs)
        uu = nam_data[_u].metpy.sel(vertical=P_lvs,time=timesel)
        vv = nam_data[_v].metpy.sel(vertical=P_lvs,time=timesel)
        Z = nam_data[_z].metpy.sel(vertical=P_lvs,time=timesel)
        RH = nam_data[_RH].metpy.sel(vertical=P_lvs,time=timesel)
        # pdb.set_trace()
        print("Interpolating to (K): ",isen_lvs)
        # pdb.set_trace()
        # isen_data = metpy.calc.isentropic_interpolation_as_dataset(
        isen_data = metpy.calc.isentropic_interpolation(
                        # isen_lvs,temp,uu,vv,spechum,Z)
                        isen_lvs,P_lvs,temp,uu,vv,spechum,Z,RH,
                        bottom_up_search=False)
        # pdb.set_trace()
        P_isen, u_isen, v_isen, sphum_isen, Z_isen, RH_isen = isen_data

        kw = dict()
        kw["map_area"] = "US"
        kw["do_US_counties"] = False
        # kw["map_area"] = "Indiana"
        # kw["do_US_counties"] = True1
        kw["land_color"] = "white"

        # Smoothing needed?
        for n,islv in enumerate(isen_lvs):
            FIG = BirdsEye(nam.lats,nam.lons,do_faster_contourf=False,
                                ocean_color="lightblue",figsize=(10,7),alpha=0.5,
                                # do_colorbar=True,
                                **kw)
            FIG.contour(P_isen[n,:,:],levels=np.arange(100,1101,25))
            # FIG.contour(sphum_isen[n,:,:],colors="darkgreen",lw=0.25)
            # FIG.contourf(sphum_isen[n,:,:],cmap=mpl.cm.Greens)
            FIG.contour(RH_isen[n,:,:],colors="darkgreen",lw=0.25,
                            levels=np.arange(60,101,10))
            FIG.contourf(RH_isen[n,:,:],cmap=mpl.cm.Greens,
                            levels=np.arange(60,101,10))
            FIG.barbs(u_isen[n,:,:],v_isen[n,:,:],thinning=10,color="black",
                                        lw=1,)
            FIG.save(f"./test/nam_april2022_test3_{islv.magnitude:03d}K.png")
        pdb.set_trace()



    # TEST 3 - ISENTROPIC BIRDSEYE



    if do_test_6:
        pass
    # TEST 4 - ISENTROPIC XSECTION

    pdb.set_trace()
