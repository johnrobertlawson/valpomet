"""For plotting lat-lon cross-sections (top-down maps)

TODO:
    * How to choose appropriate colormaps.
    * map_area from NAmerica (north america), CONUS, GreatLakes, Indiana.
"""

import os
import pdb

import numpy as np
import metpy
import matplotlib as mpl
mpl.use("agg")
import matplotlib.pyplot as plt
import cartopy
import cartopy.mpl.gridliner as cmg
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
import scipy
from metpy.plots import USCOUNTIES

import valpomet.utils.utils as utils
# import valpomet.plotting.colortables as colortables

class BirdsEye:
    def __init__(self,lats,lons,map_area="Indiana",do_maplines=True,
                        do_faster_contourf=True,alpha=0.65,
                        draw_res="50m",print_done=False,
                        # country_border_color="darkgray",
                        country_border_color="black",
                        coast_color="black",plot_coastline=True,
                        mask_out_land=False,mask_out_sea=False,
                        figsize=(9,7),dpi=300,do_US_counties=True,
                        ocean_color="black",
                        country_border_color="darkgray",
                        coast_color="black",plot_coastline=True,
                        mask_out_land=False,mask_out_sea=False,
                        figsize=(9,7),dpi=300,
                    ):


        ## Assign to attributes
        self.lats = lats
        self.lons = lons
        self.map_area = self.check_map_area(map_area)
        self.do_faster_contourf = do_faster_contourf
        self.alpha = alpha
        self.draw_res = draw_res
        self.print_done = print_done
        self.country_border_color = country_border_color
        self.coast_color = coast_color
        self.plot_coastline = plot_coastline
        self.mask_out_land = mask_out_land
        self.mask_out_sea = mask_out_sea 
        self.figsize = figsize
        self.dpi = dpi
        self.do_US_counties = do_US_counties
        self.ocean_color = ocean_color

        self.proj = self.get_proj()
        extents = self.get_extents()
        self.fig, self.ax = plt.subplots(1,subplot_kw=dict(
                                projection=self.proj),
                                figsize=self.figsize,
                                dpi=self.dpi,
                                )

        if do_maplines:
            self.do_map_stuff()

        if self.do_faster_contourf:
            self._x, self._y = np.meshgrid(self.lons,self.lats)

        if extents is not None:
            self.ax.set_extent([extents['lon_start'],extents['lon_end'],
                            extents['lat_start'],extents['lat_end']],
                            crs=ccrs.PlateCarree(),
                            )

        # Better way of changing plot font?
        # plt.rcParams["font.family"] = ["Ubuntu Thin",]
        plt.rcParams["font.family"] = "Ubuntu"
        # plt.rcParams['font.weight'] = "Thin"
        # plt.rcParams['font.style'] = "Thin"
        

    def get_proj(self):
        projs = {
                "NAmerica":ccrs.PlateCarree(),
                "CONUS":ccrs.PlateCarree(),
                "GreatLakes":ccrs.PlateCarree(),
                "Indiana":ccrs.PlateCarree(),
                }
        return projs[self.map_area]

    def get_extents(self,):
        MAP_EXTENTS = {
                    # "NAmerica":
                    "CONUS":
                        {'lat_start':23,'lat_end':57,'lon_start':-135,'lon_end':-55},
                    "Indiana":
                        {'lat_start':39,'lat_end':44,'lon_start':-90,'lon_end':-84},
                        # {'lat_start':20,'lat_end':60,'lon_start':-140,'lon_end':-50},
                    # "Global":
                        # {'lat_start':-90,'lat_end':90,'lon_start':-180,'lon_end':180},
                    }
        return MAP_EXTENTS[self.map_area]

    def set_ylocator(self,gl):
        """Only change lat (?) lines for some map_areas.
        """
        if self.map_area == "CONUS":
            lat_line_locs = range(20,61,10)
            gl.ylocator = mpl.ticker.FixedLocator(lat_line_locs)
        return gl

    @staticmethod
    def check_map_area(map_area):
        assert map_area in {"NAmerica","CONUS","GreatLakes","Indiana",
                            }
        return map_area

    def do_map_stuff(self,):
        """.
        """
        if self.plot_coastline:
            self.ax.coastlines(resolution=self.draw_res,
                    color=self.coast_color,linewidth=0.6,zorder=6)
        self.ax.add_feature(cartopy.feature.BORDERS,linestyle='-',alpha=1,
                    edgecolor=self.country_border_color,linewidth=0.4,
                    zorder=6)
        self.ax.add_feature(cartopy.feature.STATES,linestyle='-',alpha=1,
                    edgecolor=self.country_border_color,linewidth=0.4,
                    zorder=6)
        self.ax.add_feature(cartopy.feature.LAKES,linestyle='-',alpha=0.4,
                    # edgecolor=self.country_border_color,linewidth=0.4,
                    edgecolor="darkblue",linewidth=0.6,
                    facecolor=cartopy.feature.COLORS["water"],
                    zorder=1.5)
        if self.do_US_counties:
            self.ax.add_feature(USCOUNTIES.with_scale("5m"),
                        edgecolor=self.country_border_color,linewidth=0.4,
                        zorder=6)
        gl = self.ax.gridlines(draw_labels=True,linewidth=0.3,
        # gl = self.ax.gridlines(draw_labels=True,
                color='gray', alpha=0.5, linestyle='--',
                zorder=10)

        gl.top_labels = False
        gl.right_labels = False
        gl.xlines = True
        gl.ylines = True

        gl = self.set_ylocator(gl)
        gl.xformatter = cmg.LONGITUDE_FORMATTER
        gl.yformatter = cmg.LATITUDE_FORMATTER

        # land_zorder = 5 if self.mask_out_land else 1
        # Trying to fix missing green for land in NH
        land_zorder = 5 if self.mask_out_land else 1.5
        self.ax.add_feature(cfeature.NaturalEarthFeature('physical',
                    'land', self.draw_res,zorder=land_zorder,
                    edgecolor='face', facecolor='darkgreen',),
                    )
        sea_zorder = 5 if self.mask_out_sea else 1
        # sea_zorder = 5 if self.mask_out_sea else 1.5
        self.ax.add_feature(cfeature.NaturalEarthFeature('physical',
                    'ocean', self.draw_res,zorder=sea_zorder,
                    edgecolor='face', facecolor=self.ocean_color),
                    )
        return

    # @staticmethod
    # def get_cmap(vrbl,lv):
        # cmap,bounds,norm,extend = colortables.get_cmap(vrbl,lv)
        # return cmap,bounds,norm,extend
        # return

    # @staticmethod
    # def get_bounds(vrbl,lv):
        # return colortables.get_bounds(vrbl,lv)

    @staticmethod
    def smooth_data(data,sigma):
        assert isinstance(sigma,(float,int))
        return scipy.ndimage.gaussian_filter(data,sigma=sigma)

    # How does this work with metpy.units?
    # def get_cb_label(self,vrbl

    def contour(self,data,vrbl=None,smooth=None,zorder=5,levels=None,
                    colors='k',lw=0.33):

        if smooth is not None:
            data = self.smooth_data(data,smooth)
        
        kw = {"zorder":zorder,"levels":levels,"colors":colors,
                "linewidths":lw,}
        ct = self.ax.contour(self.lons,self.lats,data,
                    transform=ccrs.PlateCarree(),
                    **kw)
        plt.clabel(ct, fontsize=8, fmt='%1d',
                    use_clabeltext=True, colors=colors)
        return

    def contourf(self,data,vrbl=None,do_colorbar=True,smooth=None,
                    zorder=4,levels=None,cmap=None):

        if smooth is not None:
            data = self.smooth_data(data,smooth)

        cmap = mpl.cm.inferno_r if cmap is None else cmap
        # cmap, norm, bounds, extend = self.get_cmap(vrbl,lv)
        # kw = {"cmap":cmap,"norm":norm,"levels":bounds,"extend":extend,
                    # "zorder":zorder}
        kw = {"cmap":cmap,'zorder':zorder,'alpha':self.alpha,
                'levels':levels}

        if self.do_faster_contourf:
            # _lat, _lon, kw = self.get_these_latlons(kw)
            kw["fast_transform"] = True
            _lon = self._x
            _lat = self._y
            if self.map_area in ("NH","SH"):
                data, _lon = add_cyclic_point(data,coord=_lon)
            cf1 = self.ax.contourf(
                    _lon,_lat,data,transform=ccrs.PlateCarree(),
                    **kw)
        else:
            cf1 = self.ax.contourf(self.lons,self.lats,data,
                        transform=ccrs.PlateCarree(),
                        **kw)
        if do_colorbar:
            if False:
                cbar_ax = self.fig.add_axes([0.125, 0.05, 0.775, 0.03])
                mpl.colorbar.ColorbarBase(cbar_ax,cmap=cmap,
                                    # norm=norm,label=label,
                                    orientation='horizontal',extend='both',
                                    # ticks=ticks,
                                    )
                cbar_ax.tick_params(labelsize=8)
            if False:
                cbar_ax = self.fig.add_axes([0.125, 0.05, 0.775, 0.03])
                self.fig.colorbar(cf1,cax=cbar_ax,orientation="horizontal")
            if False:
                self.fig.colorbar(cf1,orientation="vertical")
            # more_down = True if (self.map_area in ("NH","SH")) else False
            # label_str = 0
            # ticks = self.get_ticks(vrbl,lv)
            # self.colorbar(cmap)
            # self.colorbar(cmap,norm,ticks,)
            # label=label_str,more_down=more_down)

            # Could get from evac Figure, or M-S MapFigure...
            pass
        return

    def barb(self,thinning=1):
        # self.ax
        return

    def save(self,fpath):
        self.fig.savefig(fpath,bbox_inches="tight")
        print("Saved to",fpath)
        plt.close(self.fig)
        return
