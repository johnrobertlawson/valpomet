"""Basic class for plotting a latitude--longitude plot.

This is a little wrapper so we get the fonts, dpi etc we want
"""

import os
import datetime

import cartopy.crs as ccrs
import numpy as np
import matplotlib as M
M.use("agg")
import matplotlib.pyplot as plt
import metpy

import valpomet.utils.utils as utils

class BirdsEye:
    def __init__(self,*args,**kwargs):
        """Set up figure.

        Args:
            *args   : typical arguments that go to subplots
        """
        kwargs["dpi"] = 300
        self.fig, self.axes = plt.subplots(*args,**kwargs)