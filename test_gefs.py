"""Testing GEFS loading and post-proc
"""

import os
import pdb
import itertools

from valpomet.modeltypes.gefs import GEFS
from valpomet.modeltypes.ensemble import Ensemble

# GEFS.download_data()
data_root = '/storage/gefs_data'
members = ["c00"] + [f"p{n:02d}" for n in range(1,31)]
init_h = 12
fhr = 3
prods = {'pgrb2ap5','pgrb2bp5','pgrb2sp25'} 

FPATHS = {p:[] for p in prods}

for prod,member_name in itertools.product(prods,members):
    FPATHS[prod].append(os.path.join(data_root,GEFS.create_gefs_fname(
                            member_name,init_h,prod,fhr)))

#### FIRST TEST : GEFS class
# c00_1 = GEFS(FPATHS["pgrb2sp25"][0])
# c00_2 = GEFS(FPATHS["pgrb2ap5"][0])
e00_3 = GEFS(FPATHS["pgrb2bp5"][0])

vrbl = "Temperature_isobaric_ens"
# This is (1,1,21,361,720) [?,?,level,lats(?),lons(?)]
# lats.shape = (361,)
# lons.shape = (720,)

# data,units,lats,lons,z_coords = gec00.get(vrbl)
# data = gec00.get(vrbl,return_coords=False,return_units=False)[0]

##################

#####################
# Create an ensemble - this will automatically number the members
# Let's just pretend there isn't a control member - 31 then?
gefs_ap5 = Ensemble(FPATHS["pgrb2bp5"])

# now how to load all this! Ensemble.get etc
temp_data,units,z_coords = gefs_ap5.get(vrbl)
#self.lats, self.lons needed
pdb.set_trace()
