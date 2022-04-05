"""Testing GEFS loading and post-proc
"""

import os
import pdb
import itertools

import numpy as np

from valpomet.modeltypes.gefs import GEFS
from valpomet.modeltypes.ensemble import Ensemble
from valpomet.plotting.birdseye import BirdsEye
from valpomet.plotting.isentropic import plot_isentropic_birdseye

# GEFS.download_data()
data_root = '/storage/gefs_data'
members = ["c00"] + [f"p{n:02d}" for n in range(1,31)]
init_h = 12
fhr = 3
prods = {'pgrb2ap5','pgrb2bp5','pgrb2sp25'} 
vrbl = "Temperature_isobaric_ens"

FPATHS = {p:[] for p in prods}

for prod,member_name in itertools.product(prods,members):
    FPATHS[prod].append(os.path.join(data_root,GEFS.create_gefs_fname(
                            member_name,init_h,prod,fhr)))

if True:

    # 1 - BASIC
    do_test_1 = False
    # 2 - Pressure change
    do_test_2 = True
    # 3 - Comapring products' MSLP change
    do_test_3 = False
    # 4 - 
    do_test_4 = True
    # 5 - isentropes, birdseye
    do_test_5 = True
    # 6 - isentropes, cross-section
    do_test_6 = True

    #### FIRST TEST : GEFS class
    c00_s = GEFS(FPATHS["pgrb2sp25"][0])
    c00_a = GEFS(FPATHS["pgrb2ap5"][0])
    c00_b = GEFS(FPATHS["pgrb2bp5"][0])

    # This is (1,1,21,361,720) [?,?,level,lats(?),lons(?)]
    # lats.shape = (361,)
    # lons.shape = (720,)

    # TEST 1 - BASIC
    if do_test_1:
        vrbl = "Temperature_isobaric_ens"
        data,units,lats,lons,z_coords = c00_b.get(vrbl,return_latlon=True)
        FIG = BirdsEye(lats,lons,map_area="CONUS",do_faster_contourf=False)
        # Pick 10th level - not sure what that is
        FIG.contourf(data[0,0,10,:,:])
        FIG.contour(data[0,0,10,:,:])
        FIG.save("april2022_test1.png")
        pdb.set_trace()

    # TEST 2 - PRESSURE CHANGE 
    if do_test_2:
        # MSLP_change_FPATHS = []
        member_name = "c00"
        prod = "pgrb2bp5"
        vrbl = 'Pressure_msl_ens'
        fhrs = np.arange(0,121,3)
        all_arr = np.zeros([len(fhrs),361,720])
        for n,fhr in enumerate(fhrs):
            # MSLP_change_FPATHS.append(
            fpath = os.path.join(data_root,GEFS.create_gefs_fname(
                                member_name,init_h,prod,fhr)))
            gefs_loaded = GEFS(fpath)
            data,units,lats,lons,z_coords = gefs_loaded.get(vrbl,return_latlon=True)
            data = data/100

            all_arr[n,:,:] = data[0,0,:,:]
            
        # gefs_loads = GEFS(FPATHS])
        data_diff = np.diff(all_arr,axis=0)

        # From b
        # (1,1,361,720)
        levels = np.arange(880,1080,4)

        FIG = BirdsEye(lats,lons,map_area="CONUS",do_faster_contourf=False)
        # Pick 10th level - not sure what that is
        FIG.contourf(data[0,0,:,:],levels=levels)
        FIG.contour(data[0,0,:,:],levels=levels)
        FIG.save("april2022_test2.png")
        # pdb.set_trace()
        print(data.max(),data.min())

    if do_test_3:
        # From a
        # FIG = BirdsEye(lats,lons,map_area="CONUS",do_faster_contourf=False)

        vrbl = 'Pressure_reduced_to_MSL_msl_ens'
        data,units,lats,lons,z_coords = c00_a.get(vrbl,return_latlon=True)
        data = data/100
        print(data.max(),data.min())
        pdb.set_trace()

        # Not reduced to MSLP
        # vrbl = 'Pressure_surface_ens'
        # data,units,lats,lons,z_coords = c00_a.get(vrbl,return_latlon=True)
        # pdb.set_trace()

    if do_test_4:
        # From s
        # Pressure_reduced_to_MSL_msl_ens
        # Pressure_surface_ens
        vrbl = 'Pressure_reduced_to_MSL_msl_ens'
        data,units,lats,lons,z_coords = c00_s.get(vrbl,return_latlon=True)
        pdb.set_trace()

        vrbl = 'Pressure_surface_ens'
        data,units,lats,lons,z_coords = c00_s.get(vrbl,return_latlon=True)
        pdb.set_trace()



    if do_test_5:
        pass
    # TEST 3 - ISENTROPIC BIRDSEYE



    if do_test_6:
        pass
    # TEST 4 - ISENTROPIC XSECTION

    pdb.set_trace()



#####################
if False:
    # Create an ensemble - this will automatically number the members
    # Let's just pretend there isn't a control member - 31 then?
    gefs_ap5 = Ensemble(FPATHS["pgrb2bp5"])

    # now how to load all this! Ensemble.get etc
    temp_data,units,z_coords = gefs_ap5.get(vrbl)
    #self.lats, self.lons needed

#####################

# pdb.set_trace()
