"""Wrapper to download data using THREDDS, Herbie
"""

import os
import datetime

import metpy
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
from metpy.units import units
import netCDF4
import numpy as np

import valpomet.utils.utils as utils

class NWPData:
    def __init__(self,vrbl,model,init,fchr,):
        """Download data using standardised variable names.
        """
        self.vrbl = vrbl
        self.model = model
        self.init = init
        self.fchr = fchr
        self.fcdt = self.init + datetime.timedelta(hours=self.fchr)

        self.data, self.lats, self.lons = self.download_data()

    def download_data(self):
        """Determine which scripts etc will be used"""
        if self.model == "GFS":
            data, lats, lons = self.download_gfs()
        return data, lats, lons

    @staticmethod
    def region_latlons(region):
        regions = dict()
        regions["NW IN"] = dict(north=50,south=25,east=-90,west=-110)
        return regions[region]

    def variable_lookups(self,):
        vrbl_names = dict()
        vrbl_names["GFS"] = dict(
            P="Pressure_surface",
            )
        return vrbl_names[self.model][self.vrbl]

    def download_gfs(self):
        gfs = TDSCatalog('http://thredds.ucar.edu/thredds/catalog/grib/'
                         'NCEP/GFS/Global_0p25deg/catalog.xml')
        dataset = list(gfs.datasets.values())[1]
        print(dataset.access_urls)
        ncss = NCSS(dataset.access_urls['NetcdfSubset'])
        query = ncss.query()
        query.time_range(self.init,self.fcdt)
        query.lonlat_box(**self.region_latlons())
        query.accept('netcdf4')
        vrbl_name = self.variable_lookups()
        query.variables(vrbl_name)
        data = ncss.get_data(query)
        lat = data.variables['lat'][:]
        lon = data.variables['lon'][:]
        time_var = data.variables[utils.find_time_var(data.variables[vrbl_name])]
        time_var = netCDF4.num2date(time_var[:], time_var.units).tolist()
        time_strings = [t.strftime('%m/%d %H:%M') for t in time_var]
        lon_2d, lat_2d = np.meshgrid(lon, lat)
        return data, lon_2d, lat_2d
