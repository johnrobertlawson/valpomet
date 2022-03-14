from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from metpy.units import units
from netCDF4 import num2date
import numpy as np
from siphon.ncss import NCSS
import metpy.calc as mpcalc
from scipy.ndimage import gaussian_filter
from matplotlib import rcParams, colors
import xarray as xr

_LUTSIZE = rcParams['image.lut']
_s3pcpn_l_data =  {'blue': [(0.0, 1.0, 1.0), (0.050000000000000003, 0.81568628549575806, 0.81568628549575806), (0.10000000000000001, 1.0, 1.0), (0.14999999999999999, 0.50196081399917603, 0.50196081399917603), (0.20000000000000001, 0.0, 0.0), (0.25, 0.0, 0.0), (0.29999999999999999, 0.0, 0.0), (0.34999999999999998, 0.0, 0.0), (0.40000000000000002, 0.0, 0.0), (0.45000000000000001, 0.50196081399917603, 0.50196081399917603), (0.5, 1.0, 1.0), (0.55000000000000004, 1.0, 1.0), (0.59999999999999998, 1.0, 1.0), (0.65000000000000002, 0.50196081399917603, 0.50196081399917603), (0.69999999999999996, 0.12549020349979401, 0.12549020349979401), (0.75, 0.50196081399917603, 0.50196081399917603), (0.80000000000000004, 0.87843137979507446, 0.87843137979507446), (0.84999999999999998, 0.73725491762161255, 0.73725491762161255), (0.90000000000000002, 0.47058823704719543, 0.47058823704719543), (0.94999999999999996, 0.23529411852359772, 0.23529411852359772), (1.0, 0.0, 0.0)], 'green': [(0.0, 1.0, 1.0), (0.050000000000000003, 0.81568628549575806, 0.81568628549575806), (0.10000000000000001, 1.0, 1.0), (0.14999999999999999, 0.87843137979507446, 0.87843137979507446), (0.20000000000000001, 0.75294119119644165, 0.75294119119644165), (0.25, 0.87843137979507446, 0.87843137979507446), (0.29999999999999999, 1.0, 1.0), (0.34999999999999998, 0.62745100259780884, 0.62745100259780884), (0.40000000000000002, 0.0, 0.0), (0.45000000000000001, 0.12549020349979401, 0.12549020349979401), (0.5, 0.25098040699958801, 0.25098040699958801), (0.55000000000000004, 0.12549020349979401, 0.12549020349979401), (0.59999999999999998, 0.25098040699958801, 0.25098040699958801), (0.65000000000000002, 0.12549020349979401, 0.12549020349979401), (0.69999999999999996, 0.12549020349979401, 0.12549020349979401), (0.75, 0.50196081399917603, 0.50196081399917603), (0.80000000000000004, 0.87843137979507446, 0.87843137979507446), (0.84999999999999998, 0.83137255907058716, 0.83137255907058716), (0.90000000000000002, 0.65098041296005249, 0.65098041296005249), (0.94999999999999996, 0.42352941632270813, 0.42352941632270813), (1.0, 0.20000000298023224, 0.20000000298023224)], 'red': [(0.0, 1.0, 1.0), (0.050000000000000003, 0.31372550129890442, 0.31372550129890442), (0.10000000000000001, 0.0, 0.0), (0.14999999999999999, 0.0, 0.0), (0.20000000000000001, 0.0, 0.0), (0.25, 0.50196081399917603, 0.50196081399917603), (0.29999999999999999, 1.0, 1.0), (0.34999999999999998, 1.0, 1.0), (0.40000000000000002, 1.0, 1.0), (0.45000000000000001, 1.0, 1.0), (0.5, 0.94117647409439087, 0.94117647409439087), (0.55000000000000004, 0.50196081399917603, 0.50196081399917603), (0.59999999999999998, 0.25098040699958801, 0.25098040699958801), (0.65000000000000002, 0.12549020349979401, 0.12549020349979401), (0.69999999999999996, 0.12549020349979401, 0.12549020349979401), (0.75, 0.50196081399917603, 0.50196081399917603), (0.80000000000000004, 0.87843137979507446, 0.87843137979507446), (0.84999999999999998, 0.93333333730697632, 0.93333333730697632), (0.90000000000000002, 0.85490196943283081, 0.85490196943283081), (0.94999999999999996, 0.62745100259780884, 0.62745100259780884), (1.0, 0.40000000596046448, 0.40000000596046448)]}
s3pcpn_l = colors.LinearSegmentedColormap('s3pcpn_l', _s3pcpn_l_data, _LUTSIZE)

# Uncomment the gfs model of your choice below!
#model = 'gfs_2p50'
#model = 'gfs_1p00'
model = 'gfs_0p50'
#model = 'gfs_0p25'
#print(model[0:3])

# Get the current hour from the computer and choose the proper model
# initialization time.
# These times are set based on when they appear on the nomads server.
currdate = datetime.utcnow()
currhr = int(datetime.utcnow().strftime('%H'))
if currhr >= 4 and currhr < 11:
    run = '00'
    date = datetime.strftime(currdate, "%Y%m%d"+run)
elif currhr >= 11 and currhr < 17:
    run = '06'
    date = datetime.strftime(currdate, "%Y%m%d"+run)
elif currhr >= 17 and currhr < 23:
    run = '12'
    date = datetime.strftime(currdate, "%Y%m%d"+run)
else:
    run = '18'
    date = datetime.strftime(currdate - timedelta(hours=24), "%Y%m%d"+run)

print(date)

# Here we are using the NETCDF-4 OPENDAP feature to get the data from a URL.
# You need an internet connection to be able to use this feature.
data = xr.open_dataset('http://nomads.ncep.noaa.gov:80/dods/{}/{}{}/{}_{}z'.format(model,
                                                                                   model[0:3],
                                                                                   date[:-2],
                                                                                   model,
                                                                                   run))

# Pulling in only the data we need.
lats  = data.lat
lons  = data.lon
levs  = list(data.lev.values)  # 26 levels, 850 = [5], 500 = [12], 300 = [16]
#print levs[0],levs[5],levs[16]
times  = data.time
ntimes = len(times)

print("The time resolution is "+str(times.resolution)+" days")
time_step = 24*times.resolution
print("The time step between forecast hours is "+str(time_step)+" hours")


# Set US Bounds for GFS 1 deg data, these are the reference index values
iLLlat = np.where(np.array(lats)==10)[0][0]
iLLlon = np.where(np.array(lons)==210)[0][0]


iURlat = np.where(np.array(lats)==70)[0][0]
iURlon = np.where(np.array(lons)==320)[0][0]

lons = lons[iLLlon:iURlon]
lats = lats[iLLlat:iURlat]

wind_lon = lons[::5]
wind_lat = lats[::5]

lev1000 = levs.index(1000)
lev850 = levs.index(850)
lev700 = levs.index(700)
lev500 = levs.index(500)
lev300 = levs.index(300)


#hghts = data.variables['hgtprs'][0:24,0:20,iLLlat:iURlat,iLLlon:iURlon]
hght850 = data.hgtprs[:,lev850,iLLlat:iURlat,iLLlon:iURlon]
tmpk850 = data.tmpprs[:,lev850,iLLlat:iURlat,iLLlon:iURlon]
# uwnd850  = data.variables['ugrdprs'][:,lev850,iLLlat:iURlat:5,iLLlon:iURlon:5]
# vwnd850  = data.variables['vgrdprs'][:,lev850,iLLlat:iURlat:5,iLLlon:iURlon:5]
print("Got the 850-hPa Heights and TMPK")

hght500 = data.hgtprs[:,lev500,iLLlat:iURlat,iLLlon:iURlon]
avor500 = data.absvprs[:,lev500,iLLlat:iURlat,iLLlon:iURlon]
# uwnd500  = data.variables['ugrdprs'][:,12,iLLlat:iURlat:5,iLLlon:iURlon:5]
# vwnd500  = data.variables['vgrdprs'][:,12,iLLlat:iURlat:5,iLLlon:iURlon:5]
print("Got the 500-hPa Heights and AVOR")

hght300 = data.hgtprs[:,lev300,iLLlat:iURlat,iLLlon:iURlon]
uwnd300  = data.ugrdprs[:,lev300,iLLlat:iURlat,iLLlon:iURlon]
vwnd300  = data.vgrdprs[:,lev300,iLLlat:iURlat,iLLlon:iURlon]
print("Got the 300-hPa Heights, UWND, and VWND")

mslp  = data.prmslmsl[:,iLLlat:iURlat,iLLlon:iURlon]
#temp2m = data.variables['tmpsfc'][:,iLLlat:iURlat,iLLlon:iURlon]
hght1000 = data.hgtprs[:,lev1000,iLLlat:iURlat,iLLlon:iURlon]
precip   = data.apcpsfc[:,iLLlat:iURlat,iLLlon:iURlon]
# uwnd10 = data.ugrd10m[:,iLLlat:iURlat:5,iLLlon:iURlon:5]
# vwnd10 = data.vgrd10m[:,iLLlat:iURlat:5,iLLlon:iURlon:5]
print("Got the MSLPs, 1000-hPa Heights, and SFC Precip")

plotcrs = ccrs.LambertConformal(central_latitude=45., central_longitude=-100.,
                                    standard_parallels=[30, 60])
    
datacrs = ccrs.PlateCarree()

clon, clat = np.meshgrid(lons, lats)

tlatslons = plotcrs.transform_points(datacrs,clon,clat)
tlon = tlatslons[:,:,0]
tlat = tlatslons[:,:,1]

# To set the map area, need to convert to proper coords.
LL = plotcrs.transform_point(-125.,22.,ccrs.PlateCarree())
UR = plotcrs.transform_point(-55.,52.,ccrs.PlateCarree())

 # Add state boundaries to plot
states_provinces = cfeature.NaturalEarthFeature(category='cultural',
                                                name='admin_1_states_provinces_lakes',
                                                scale='50m', facecolor='none')
# Add country borders to plot
country_borders = cfeature.NaturalEarthFeature(category='cultural',
                                               name='admin_0_countries',
                                               scale='50m', facecolor='none')

def plot_background(num,crs1):
    ax = plt.subplot(num,projection=crs1)
    #   ax.set_extent([west long, east long, south lat, north lat])
    ax.set_extent([LL[0],UR[0],LL[1],UR[1]],crs1)
    ax.coastlines('50m',edgecolor='black',linewidth=0.5)
    ax.add_feature(states_provinces,edgecolor='black',linewidth=0.5)
    ax.add_feature(country_borders, edgecolor='black', linewidth=0.75)
    return ax

clevpmsl = np.arange(800,1100,4)
clev850 = np.arange(0,5000,30)
clevrh700 = [50,70,80,90,100]
clevtmpc850 = np.arange(-50,40,2)
clev500 = np.arange(0,10000,60)
clevavor500 = [-4,-3,-2,-1,0,7,10,13,16,19,22,25,28,31,34,37,40,43,46]
clev300 = np.arange(0,15000,120)
clevsped300 = np.arange(50,230,20)
clevprecip = [0,0.01,0.03,0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50,
              0.60,0.70,0.80,0.90,1.00,1.25,1.50,1.75,2.00,2.50]
colorsavor500 = ('#660066','#660099','#6600CC','#6600FF','w','#ffE800','#ffD800','#ffC800',
                 '#ffB800','#ffA800','#ff9800','#ff8800','#ff7800','#ff6800','#ff5800',
                 '#ff5000','#ff4000','#ff3000')

for fh in range(ntimes):
    # Create a clean datetime object for plotting based on time of Geopotential heights
    vtime = datetime.strptime(str(times.values[fh].astype('datetime64[ms]')),
                          '%Y-%m-%dT%H:%M:%S.%f')
    print(vtime)

    # For a few vairables we want to smooth the data to remove non-synoptic scale wiggles.
    hght_1000 = gaussian_filter(hght1000[fh], sigma=1.5, order=0)
    hght_850 = gaussian_filter(hght850[fh], sigma=1.5, order=0)
    hght_500 = gaussian_filter(hght500[fh], sigma=1.5, order=0)
    hght_300 = gaussian_filter(hght300[fh], sigma=1.5, order=0)
    pmsl = gaussian_filter(mslp[fh]/100., sigma=1.5, order=0)
    
    uwnd_300 = uwnd300[fh] * units('m/s')
    vwnd_300 = uwnd300[fh] * units('m/s')

    # Convert data to common formats
    tmpc_850 = tmpk850[fh] - 273.15
    #tmpf2m = (9./5.)*(temp2m - 273.15) + 32.0
    absvort_500 = avor500[fh] *1e5
    wspd_300 = mpcalc.wind_speed(uwnd_300, vwnd_300)
    pcpin   = precip[fh] * .0393700787

    fig=plt.figure(1,figsize=(17.,13.))
    fig.subplots_adjust(bottom=0, left=.01, right=.99, top=.99, hspace=.03, wspace = 0.02)
        
    # Following line is to get wind barbs properly on the correct projection
    # udat, vdat, xv, yv = m.transform_vector(uwnd_500[0,:,:],vwnd_500[0,:,:],tlon1,tlat1,15,21,returnxy=True)
    # Upper-left panel MSLP, 1000-500 hPa Thickness, Precip (in)
    ax1 = plot_background(221,plotcrs)
    ax1.set_extent([230., 290., 20., 55.], ccrs.PlateCarree())
    plt.title('MSLP (hPa), 2m TMPF, and Precip',loc='left')
    plt.title('VALID: {}'.format(vtime),loc='right')
    cmap = s3pcpn_l
    if fh == 0:
        cf = ax1.contourf(tlon,tlat,np.zeros(pcpin.shape),clevprecip,cmap=cmap)
        prev_precip = np.zeros(pcpin.shape)
    else:
        cf = ax1.contourf(tlon,tlat,pcpin-prev_precip,clevprecip,cmap=cmap)
        prev_precip = pcpin
#     ax1.barbs(wind_lon,wind_lat,(uwnd_10.to('kts')).m,(vwnd_10.to('kts')).m,length=6,
#               transform=datacrs)
    cbar = plt.colorbar(cf,orientation='horizontal',extend='both',aspect=65,pad=0,extendrect='True')
    cs2 = ax1.contour(tlon,tlat,hght_500-hght_1000,clev500,colors='r',linewidths=1.5,linestyles='dashed')
    cs  = ax1.contour(tlon,tlat,pmsl,clevpmsl,colors='k',linewidths=1.5)
    plt.clabel(cs,fontsize=10,inline=True,fmt='%d',rightside_up=True)
    plt.clabel(cs2,fontsize=9,inline=True,fmt='%d',rightside_up=True)
        
    # Upper-right panel 850-hPa Heights and Temp (C)
    ax2 = plot_background(222,plotcrs)
    ax2.set_extent([230., 290., 20., 55.], ccrs.PlateCarree())
    cmap = plt.cm.jet
    cf = ax2.contourf(tlon,tlat,tmpc_850,clevtmpc850,cmap=cmap,extend='both')
    cbar = plt.colorbar(cf,orientation='horizontal',extend='both',aspect=65,pad=0,extendrect='True')
    cs1 = ax2.contour(tlon,tlat,tmpc_850,clevtmpc850,colors='k',linewidths=1.5, linestyles=':',alpha=0.5)
    cs = ax2.contour(tlon,tlat,hght_850,clev850,colors='k',linewidths=1.5)
#     ax2.barbs(wind_lon,wind_lat,(uwnd_850.to('kts')).m,(vwnd_850.to('kts')).m,length=6,
#               transform=datacrs)
    plt.clabel(cs,fontsize=10,inline=True,fmt='%d',rightside_up=True)
    plt.clabel(cs1,fontsize=10,inline=True,fmt='%d')
    plt.title('850-hPa HGHTs (m) and TMPC',loc='left')
    plt.title('VALID: {}'.format(vtime),loc='right')
        
    # Lower-left panel 500-hPa Heights and AVOR
    ax3 = plot_background(223,plotcrs)
    ax3.set_extent([230., 290., 20., 55.], ccrs.PlateCarree())
    cf = ax3.contourf(tlon,tlat,absvort_500,clevavor500,colors=colorsavor500,extend='both')
    cs1 = ax3.contour(tlon,tlat,absvort_500,clevavor500,colors='k',linewidths=1.5,linestyles=':',alpha=0.5)
    cbar = plt.colorbar(cf,orientation='horizontal',extend='both',aspect=65,pad=0,extendrect='True')
    cs = ax3.contour(tlon,tlat,hght_500[:,:],clev500,colors='k',linewidths=1.5)
#     ax3.barbs(wind_lon,wind_lat,(uwnd_500.to('kts')).m,(vwnd_500.to('kts')).m,length=6,
#               transform=datacrs)
    plt.clabel(cs,fontsize=10,inline=True,fmt='%d',rightside_up=True)
    plt.title('500-hPa HGHTs (m) and AVOR ($*10^5$ $s^{-1}$)',loc='left')
    plt.title('VALID: {}'.format(vtime),loc='right')
        
    # Lower-right panel 300-hPa Heights and Wind Speed (kts)
    ax4 = plot_background(224,plotcrs)
    ax4.set_extent([230., 290., 20., 55.], ccrs.PlateCarree())
    cmap = plt.cm.get_cmap("BuPu")
    cf = ax4.contourf(tlon,tlat,wspd_300,clevsped300,cmap=cmap,extend='max')
    cbar = plt.colorbar(cf,orientation='horizontal',extend='max',aspect=65,pad=0,extendrect='True')
    cs = ax4.contour(tlon,tlat,hght_300,clev300,colors='k',linewidths=1.5)
#     ax4.barbs(wind_lon,wind_lat,(uwnd_300.to('kts')).m,(vwnd_300.to('kts')).m,length=6,
#               transform=datacrs)
    plt.clabel(cs,fontsize=10,inline=True,fmt='%d',rightside_up=True)
    plt.title('300-hPa HGHTs (m) and SPED (kts)',loc='left')
    plt.title('VALID: {}'.format(vtime),loc='right')
        
    # To make a nicer layout use plt.tight_layout()

    plt.savefig('/home/kgoebber/http/ncep_models/gfs/gfs_four_panel_f%02d.png' % (fh*time_step),dpi=150, bbox_inches='tight')
    plt.close()
    #plt.show()

