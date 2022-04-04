"""For plotting lat-lon cross-sections (top-down maps)

TODO:
    * How to choose appropriate colormaps.
"""

import os
import pdb

import metpy
import matplotlib as mpl
mpl.use("agg")
import matplotlib.pyplot as plt

import valpomet.utils.utils as utils
from valpomet.plotting.colortables import ColorTables

class BirdsEye:
    def __init__(self,lats,lons):
        self.fig, self.ax = plt.subplots()
        self.lats = lats
        self.lons = lons

        # legend

    def contour(self,data,):
        # self.ax
        return

    def contourf(self,data,):
        # self.ax
        return

    def barb(self,thinning=1):
        # self.ax
        return

    def save(self,fpath):
        self.fig.savefig(fpath)
        plt.close(fig)
        return
