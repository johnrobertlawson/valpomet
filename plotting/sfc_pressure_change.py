""" 3-hour surface pressure change.
"""

import os
import pdb

import metpy

from valpomet.plotting.birdseye import Birdseye

def surface_pressure_change(model="GFS",init="now",fchr=12):
    f1 = BirdsEye(1,figsize=(10,8),dpi=300)
    if init == "now":
        init = datetime.datetime.utcnow()
    DATA = Data(vrbl="pressure",model="GFS",init=init,fchr=fchr)
    return

if __name__ == "__main__":
    DATA = surface_pressure_change()
    pass