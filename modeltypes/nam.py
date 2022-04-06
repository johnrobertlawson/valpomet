"""Class for loading NAM data

TODO:
    * Get units rigorously dealt with
    * Select time and level more easily
    * astype(datetime.datetime64["ms"]).astype("O")
        * Can use dt.hour etc
        * Gets ns into datetimes; don't use ugly ways
"""

import itertools
import os
import pdb
import datetime
import wget
import glob

import numpy as np
import pandas as pd
import xarray as xr
import scipy
import cartopy.crs as ccrs

import valpomet.utils.utils as utils

class NAM:
    def __init__(self,fpath=None,print_inventory=False):
        self.fpath = fpath
        self.lazy_load = True
        self.xrobj, self.metadata = self.get_data_metadata()
        self.parsed_ds = self.xrobj.metpy.parse_cf()
        self.ds = self.parsed_ds.metpy.assign_latitude_longitude()

        #### KEY METADATA
        self.valid_times = self.xrobj.coords["time"].data
        self.init_time = self.xrobj.coords["reftime"].data
        # There is no time zero (analysis) 
        self.forecast_times = self.valid_times - self.init_time
        # datetime64[ns] format
        # In hours:
        self.forecast_hours = self.forecast_times / (3600*1e9)

        self.inventory = self.get_inventory()
        self.x, self.y = self.get_xy_coords()
        self.lats, self.lons = self.get_latlons()
        if print_inventory:
            self.print_inventory(write_to_file=True)

    def get_latlons(self):
        lats, lons = (self.ds.coords["latitude"].data, 
                        self.ds.coords["longitude"].data)
        return lats, lons
        
    def get_xy_coords(self):
        # (x = 614, y = 428
        return self.xrobj.coords["x"].data, self.xrobj.coords["y"].data
            
    def print_inventory(self,write_to_file=False):
        for x in self.inventory:
            print(x)
        if write_to_file:
            fpath = f"docs/NAM_inventory.txt"
            with open(fpath,"w") as f:
                for x in self.inventory:
                    f.write(f"{x}\n")
        return

    def get_inventory(self):
        prods = sorted(self.metadata["data_vars"].keys())
        return prods

    def parse_metadata(self):
        self.dims = self.metadata["dims"]
        return

    def get(self,vrbl,utc=None,lv=None,lats=None,lons=None,lv_str=None,
                return_z_coords=True,return_units=True,smooth=None,
                return_latlon=False):
        """

        lv_Str should be e.g.  height_above_ground1 - how to get coord?
        """
        if not all([utc,lv,lats,lons]):
            dataset = self.xrobj.data_vars.get(vrbl)
            # pdb.set_trace()
            units = dataset.units
            # lats = dataset.latitude
            # lons = dataset.longitude
            lats = self.lats
            lons = self.lons

            data = dataset.data
            # (1,1,361,720) shape for v-comp of wind trop vrbl
            
            # To find vertical coord system, find that name
            if lv_str is None:
                vertical_coord = []
                for coo in self.xrobj.get(vrbl).coords:
                    # pdb.set_trace()
                    if coo not in ("latitude","longitude","reftime","time",
                                        "time1","x","y",):
                        vertical_coord.append(coo)

                if len(vertical_coord) != 1:
                    print("Only one vertical level.")
                    z_coords = None
                else:
                    lv_str = vertical_coord[0]
                    z_coords = self.xrobj.get(vrbl).coords.get(lv_str).data
            
        if smooth is not None:
            data = self.smooth_data(data,smooth)
            

        rets = [data,]
        if return_units:
            rets.append(units)
        if return_latlon:
            rets.extend([lats,lons])
        if return_z_coords:
            rets.append(z_coords)
        
        return rets 

    @staticmethod
    def smooth_data(data,sigma,order=0):
        return scipy.ndimage.gaussian_filter(data,sigma=sigma,
                            # order=1,truncate=3)
                            )

    def get_data_metadata(self):
        data = xr.open_dataset(self.fpath)
        metadata = data.to_dict(data=False)
        # close netCDF file? Or should there be an "exit" class method?
        return data, metadata

    @staticmethod
    def create_nam_fname(latest=True):
        now = datetime.datetime.utcnow()
        if latest:
            if (now.hour >= 11) and (now.hour <=16):
                hour = 6
            elif (now.hour >= 17) and (now.hour <= 22):
                hour = 12
            elif (now.hour >= 23) or (now.hour <= 4):
                if now.hour <= 4:
                    now -= timedelta(days=1)
                else:
                    hour = 18
            else:
                hour = 0     

        date = datetime.datetime(now.year,now.month,now.day,hour)
        fname = f"{date:%Y%m%d}{hour:02d}_nam.nc"
        return fname

    @classmethod
    def create_nam_fpath(cls,root_dir,latest=True):
        # os.chdir('/data/ldmdata/model/nam')
        return os.path.join(root_dir,cls.create_nam_fname(latest=latest))

    @staticmethod
    def get_level_idx(z_coords,lv,raise_error=True):
        """Needs to work with units."""
        idx = z_coords.index(float(lv))
        return idx
