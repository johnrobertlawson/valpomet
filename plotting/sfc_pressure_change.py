""" 3-hour surface pressure change.
"""

import os
import pdb
import datetime
import importlib

import metpy
valpomet = importlib.import_module("valpo-met")
from valpomet.plotting.birdseye import BirdsEye
from birdseye import BirdsEye
from valpomet.data.nwpdata import NWPData

def surface_pressure_change(model="GFS",init="now",fchr=12):
    f1 = BirdsEye(1,figsize=(10,8),dpi=300)
    if init == "now":
        init = datetime.datetime.utcnow()
    DATA = NWPData(vrbl="pressure",model="GFS",init=init,fchr=fchr)
    return DATA

if __name__ == "__main__":
    DATA = surface_pressure_change()
    pass