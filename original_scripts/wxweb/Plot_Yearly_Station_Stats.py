import urllib
import os
import plotly
import plotly.graph_objs as go
#plotly.offline.init_notebook_mode()
#plotly.tools.set_credentials_file(username='gobie28', api_key='OkhuWXxBR4WbgCykUaTO')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


def cyclic_rolling_mean(dat,window):
    '''This function will compute a rolling mean for a 
       given window length and return a numpy array of
       the same length as the original array.
       
       This might be best used for yearly meteorological
       data that has a cyclic data point.
       
       Input: 1D numpy array, window length
       Output: 1D numpy array
       '''
    cyc_avg = np.empty((len(dat)))
    for a in range(len(dat)):
        val = 0
        for b in range(window):
            val = val + dat.values[a+b-window+1]
        cyc_avg[a] = val/window
    return cyc_avg

def plot_yearly_stats(df, var, window, plt_title, figname):
    gb = df.groupby([df.index.month,df.index.day])
    gb_current_year = df.groupby([df.index.year])
    year = datetime.utcnow().year
    
    dat = gb[var]
    cur_year_data = gb_current_year[var].get_group(year)
    
    if var == 'MaxTemperature':
        plot_color = 'orangered'
    elif var == 'MinTemperature':
        plot_color = 'dodgerblue'
    
    x_days2 = []
    for day in np.arange(1, len(dat)+1):
        x_days2.append(datetime.strptime(f'2000{day}','%Y%j'))

    stn_mean = np.round(cyclic_rolling_mean(dat.mean(),window),decimals=2)
    maxyears = pd.DatetimeIndex(dat.idxmax()).year

    stn_std  = np.round(cyclic_rolling_mean(dat.std(),window),decimals=2)
    stn_max = dat.max()
    stn_min = dat.min()
    minyears = pd.DatetimeIndex(dat.idxmin()).year

    meanp = go.Scatter(x=x_days2,
                   y=stn_mean,
                   name='Mean (&deg;F)',
                   legendgroup='3',
                   line = dict(
                     color = ('black'),
                     width = 2)
                 )
    maxp  = go.Scatter(x=x_days2,
                   y=stn_max,
                   name='Max (&deg;F)',
                   text=maxyears,
                   legendgroup='1',
                   line = dict(
                        color = ('darkred'),
                        width = 2),
                  )
    minp  = go.Scatter(x=x_days2,
                   y=stn_min,
                   name='Min (&deg;F)',
                   text=minyears,
                   legendgroup='4',
                   line = dict(
                        color = ('darkblue'),
                        width = 2)
                  )
    mpstdp  = go.Scatter(x=x_days2,
                     y=stn_mean+stn_std,
                     name='+1 Stdev (&deg;F)',
                     fill='tonexty',
                     legendgroup='1',
                     line = dict(
                         color = ('dimgray'),
                         width = 2)
                  )
    mmstdp  = go.Scatter(x=x_days2,
                     y=stn_mean-stn_std,
                     name='-1 Stdev (&deg;F)',
                     legendgroup='4',
                     #fill='tonexty',
                     line = dict(
                         color = ('dimgray'),
                         width = 2)
                  )
    yearp = go.Scatter(x=x_days2[:len(cur_year_data)],
                   y=cur_year_data,
                   name=f'{year} Obs.',
                   legendgroup='3',
                   line = dict(
                     color = (plot_color),
                     width = 2)
                 )

    data = [minp, meanp, mmstdp, mpstdp, maxp, yearp]

    layout = go.Layout(
                title=plt_title,
                legend=dict(orientation= "h", x=0.5, y=.08,
                            traceorder="grouped", xanchor='center',
                            bordercolor='darkgray', borderwidth=1),
                yaxis=dict(title='Temperature (F)',
                           zeroline=False,
                           nticks=16,
                           ),
                xaxis=dict(title='Day',
                       tickangle=-45,
                       hoverformat='%d %b',
                       tickformat='%d %b',
                       range=[datetime(1999,12,31),datetime(2001,1,1)],
                       tickvals=[x_days2[a] for a in [0,31,60,91,121,152,182,213,244,274,305,335,365]],
                      ),
                width=1000,
                height=800,
                hovermode='x')

    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename=f'/home/wxweb/sfc_climo/{figname}.html', auto_open=False)
    return

# Function to make Trace precip 1e-5
#cfun = lambda x: x if (x != 'T') else 1e-5
def cfun(x):
    if x == 'T':
        x = 1e-5
    
    if x == 'M':
        x = np.nan
    return x

# URL access to ORD thredded data (Chicago, IL Area)
# http://data.rcc-acis.org/StnData?sid=ORDthr&sdate=por&edate=por&elems=1,2,4,10,11&output=csv
now = datetime.utcnow().strftime('Last Updated %d %b %Y at %H UTC')

for loc in ['ORD','RFD','VPZ']:
    if (loc == 'ORD'):
        stn = ['Chicago','IL','ORDthr']
    if (loc == 'RFD'):
        stn = ['Rockford','IL','RFDthr']
    if (loc == 'VPZ'):
        stn = ['Valparaiso','IN','VPZthr']
        
    if (loc == 'VPZ'):
        VPZthr = ['128999','128992','KVPZ']
        VPZsdate = ['por','2005-4-1','2014-5-15']
        VPZedate = ['por','2014-5-14','por']
        for i in range(len(VPZthr)):
            filename = f'http://data.rcc-acis.org/StnData?sid={VPZthr[i]}&sdate={VPZsdate[i]}&edate={VPZedate[i]}&elems=1,2,4,10,11&output=csv'
            if i == 0:
                df = pd.read_csv(filename,parse_dates=True,index_col=0,na_values='M',sep=',',skiprows=1,
                    names=['Date','MaxTemperature','MinTemperature','Precipitation','Snowfall','SnowDepth'],
                    converters={'Precipitation': cfun,'Snowfall': cfun,'SnowDepth': cfun})
            else:
                df = df.append(pd.read_csv(filename,parse_dates=True,index_col=0,na_values='M',sep=',',skiprows=1,
                    names=['Date','MaxTemperature','MinTemperature','Precipitation','Snowfall','SnowDepth'],
                    converters={'Precipitation': cfun,'Snowfall': cfun,'SnowDepth': cfun}))
    else:
        filename = urllib.request.urlopen(f'http://data.rcc-acis.org/StnData?sid={stn[2]}&sdate=por&edate=por&elems=1,2,4,10,11&output=csv')
        df = pd.read_csv(filename,parse_dates=True,index_col=0,na_values='M',sep=',',skiprows=1,
                 names=['Date','MaxTemperature','MinTemperature','Precipitation','Snowfall','SnowDepth'],
                 converters={'Precipitation': cfun,'Snowfall': cfun,'SnowDepth': cfun})


    plot_yearly_stats(df, 'MaxTemperature', 7, stn[0]+', '+stn[1]+' Max Temperature Variability: '+str(df.index.year[0])+'-'+str(df.index.year[-1])+'<br>'+now,stn[0]+'_'+stn[1]+'_Max_Temp')


    plot_yearly_stats(df, 'MinTemperature', 7, stn[0]+', '+stn[1]+' Min Temperature Variability: '+str(df.index.year[0])+'-'+str(df.index.year[-1])+'<br>'+now,stn[0]+'_'+stn[1]+'_Min_Temp')

    os.system(f'cp /home/wxweb/sfc_climo/{stn[0]}_{stn[1]}_Max_Temp.html /var/www/html/station_climo/data/.')
    os.system(f'cp /home/wxweb/sfc_climo/{stn[0]}_{stn[1]}_Min_Temp.html /var/www/html/station_climo/data/.')
