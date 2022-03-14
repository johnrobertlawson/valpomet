import csv
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.ticker import FormatStrFormatter
import matplotlib.patches as mpatches
import datetime

cmap = plt.get_cmap('gnuplot_r')

def quarter_round(x):
    return math.ceil(x*4)/4

def csv_reader(file_string):
    data = []
    reader = csv.reader(open(file_string), delimiter=';')
    for row in reader:
        if len(row)>0:
            data.append(row)
    data = np.asarray(data)
    return data

type_c = np.array([
#    [[0.0,1.0,0,0.4],[0,1.0,0,1.0],[0,1.0,0,0.7]],
#    [[0.0,0.75,0.0,0.4],[0,0.75,0,1.0],[0,0.75,0,0.7]],
    [[0.0,0.5,0,0.4],[0,0.5,0,1.0],[0,0.5,0,0.7]],
    [[0.2,0.80,0.7,0.4],[0.2,0.8,0.7,1.0],[0.2,0.8,0.7,0.7]],
    [[0.0,0,0.9,0.4],[0,0,0.9,1.0],[0,0,0.9,0.7]],
    [[0.3,0,0.9,0.4],[0.3,0,0.9,1.0],[0.3,0,0.9,0.7]],
    [[0.6,0,0.9,0.4],[0.6,0,0.9,1.0],[0.6,0,0.9,0.7]],
    ['red','red','red'],
    [[0,0,0,0.4],[0,0,0,1.0],[0,0,0,0.7]],
    [[1,1,0,1.0],[1,1,0,1.0],[1,1,0,1.0]]])
    
#type_strings = ['Drizzle','Rain/Drizzle','Rain','Rain/Snow','Snow',
#    'Ice Needles','Ice Pellets','Hail','Unknown','Error'] 
type_strings = ['Rain','Rain/Snow','Snow',
    'Ice Needles','Ice Pellets','Hail','Unknown','Error']


rasn = np.array([[0.2,0.80,0.7,0.4],[0.2,0.8,0.7,1.0],[0.2,0.8,0.7,0.7]])
radz = np.array([[0.0,0.75,0.0,0.4],[0,0.75,0,1.0],[0,0.75,0,0.7]])
ra = np.array([[0.0,0.5,0,0.4],[0,0.5,0,1.0],[0,0.5,0,0.7]])
dz = np.array([[0.0,1.0,0,0.4],[0,1.0,0,1.0],[0,1.0,0,0.7]])
sn = np.array([[0.0,0,0.9,0.4],[0,0,0.9,1.0],[0,0,0.9,0.7]])
sg = np.array([[0.3,0,0.9,0.4],[0.3,0,0.9,1.0],[0.3,0,0.9,0.7]])
gs = np.array([[0.6,0,0.9,0.4],[0.6,0,0.9,1.0],[0.6,0,0.9,0.7]])

def p_type_calc(p_type):
    '''Converts ASOS Code to Precip type text'''
    if 'NP' in p_type:
        p_type_text = 'No Precipitation'
        p_color='k'
    elif 'UP' in p_type:
        p_type_text = prefix + 'Unidentified Precipitation'
        p_color='k'
    elif 'RASN' in p_type:
        if '-' in p_type:
            p_color = rasn[0,:]
            prefix = 'Light '
        elif '+' in p_type:
            p_color = rasn[1,:]
            prefix = 'Heavy '
        else:
            p_color = rasn[2,:]
            prefix = 'Moderate '
        p_type_text = prefix + 'Rain/Snow'
    elif 'RADZ' in p_type:
        if '-' in p_type:
            p_color = ra[0,:]
            prefix = 'Light '
        elif '+' in p_type:
            p_color = ra[1,:]
            prefix = 'Heavy '
        else:
            p_color = ra[2,:]
            prefix = 'Moderate '
        p_type_text = prefix + 'Drizzle/Rain'
    elif 'RA' in p_type:
        if '-' in p_type:
            p_color = ra[0,:]
            prefix = 'Light '
        elif '+' in p_type:
            p_color = ra[1,:]
            prefix = 'Heavy '
        else:
            p_color = ra[2,:]
            prefix = 'Moderate '
        p_type_text = prefix + 'Rain'
    elif 'DZ' in p_type:
        if '-' in p_type:
            p_color = ra[0,:]
            prefix = 'Light '
        elif '+' in p_type:
            p_color = ra[1,:]
            prefix = 'Heavy '
        else:
            p_color = ra[2,:]
            prefix = 'Moderate '
        p_type_text = prefix + 'Drizzle'
    elif 'SN' in p_type:
        if '-' in p_type:
            p_color = sn[0,:]
            prefix = 'Light '
        elif '+' in p_type:
            p_color = sn[1,:]
            prefix = 'Heavy '
        else:
            p_color = sn[2,:]
            prefix = 'Moderate '
        p_type_text = prefix + 'Snow'
    elif 'SG' in p_type:
        if '-' in p_type:
            p_color = sg[0,:]
            prefix = 'Light '
        elif '+' in p_type:
            p_color = sg[1,:]
            prefix = 'Heavy '
        else:
            p_color = sg[2,:]
            prefix = 'Moderate '
        p_type_text = prefix + 'Ice prisms/needles'
    elif 'GS' in p_type:
        if '-' in p_type:
            p_color = gs[0,:]
            prefix = 'Light '
        elif '+' in p_type:
            p_color = gs[1,:]
            prefix = 'Heavy '
        else:
            p_color = gs[2,:]
            prefix = 'Moderate '
        p_type_text = prefix + 'Ice grain/pellets'
    elif 'GR' in p_type:
        p_type_text = 'Hail'
        p_color='red'
    else:
        p_type_text = 'Sensor Error'
        p_color='gray'
    return p_type_text,p_color
#alphas = np.linspace(0.1, 1, 10)
#rgba_colors = np.zeros((10,4))
# for red the first column needs to be one
#rgba_colors[:,0] = 1.0
# the fourth column needs to be your alphas
#rgba_colors[:, 3] = alphas

start_time = datetime.datetime.now()
start_time = start_time - datetime.timedelta(minutes=1)
file_string = start_time.strftime('/archive/data_vudist/%Y/%m/%d/%Y%m%d%H.txt')
print(file_string)
date_string = start_time.strftime('%m/%d/%Y')

size_bins = np.hstack((np.arange(0.125,0.5,0.125),np.arange(0.5,2.0,0.25),np.arange(2.0,9.0,0.5)))
speed_bins = np.hstack((np.arange(0,1.0,0.2), np.arange(1.0,3.4,0.4), np.arange(3.4,9.0,0.8), [9,10,20]))

data = csv_reader(file_string)
print(data.shape)
#go back an hour
time_lasthour = start_time - datetime.timedelta(hours=1)
file_string = time_lasthour.strftime('/archive/data_vudist/%Y/%m/%d/%Y%m%d%H.txt')
data_previous = csv_reader(file_string)
data = np.vstack((data_previous,data))
print(data.shape)
#go back another hour
time_lasthour = start_time - datetime.timedelta(hours=2)
file_string = time_lasthour.strftime('/archive/data_vudist/%Y/%m/%d/%Y%m%d%H.txt')
data_previous = csv_reader(file_string)
data = np.vstack((data_previous,data))
print(data.shape)
#go back another hour
time_lasthour = start_time - datetime.timedelta(hours=3)
file_string = time_lasthour.strftime('/archive/data_vudist/%Y/%m/%d/%Y%m%d%H.txt')
data_previous = csv_reader(file_string)
data = np.vstack((data_previous,data))
print(data.shape)


dsd_data = np.empty((len(size_bins)-1,len(speed_bins)-1,121))
p_type = [] #ASOS Code
p_rate = [] #mm/hr
p_color_timeline = [] #color text
p_time = []
for h in range(1,122):
    #print(data[-h,4][0:-3])
    #print(data[-h,7])
    k=79 #start of data
    p_type.append(data[-h,7])
    p_color_timeline.append(p_type_calc(data[-h,7])[1])
    p_rate.append(float(data[-h,12]))
    p_time.append(data[-h,4][0:-3])
    for i in range(dsd_data.shape[0]):
        for j in range(dsd_data.shape[1]):
            dsd_data[i,j,-h] = data[-h,k]
            k+=1

#print(p_type[::-1])
#print(p_color_timeline[::-1])
#p_type_recent = max(set(p_type[0:5]), key = p_type[0:5].count) #most common in the last 5 minutes
p_type_recent = p_type[0]
p_type_recent_text = p_type_calc(p_type_recent)[0]
p_type_recent_color = p_type_calc(p_type_recent)[1]

#take 5-minute sums
#dsd_data_hour = np.empty((len(size_bins)-1,len(speed_bins)-1,24))
#for i,j in zip(range(24),range(0,121,5)):
#    dsd_data_hour[:,:,i] = np.sum(dsd_data[:,:,j:j+5],axis=2)
#dsd_data = dsd_data_hour[:,:,:]


total_count = np.nansum(dsd_data[:,:,-1])

y,x = np.meshgrid(speed_bins[:-1],size_bins[:-1])
dsd_data[np.where(dsd_data==0.0)] = np.nan

fig = plt.figure(figsize=(15,10))
gs = fig.add_gridspec(4,1)
ax1 = fig.add_subplot(gs[0:3,0])
c = ax1.pcolormesh(x,y,dsd_data[:,:,-1],cmap=cmap,vmin=1,vmax=1000,norm=matplotlib.colors.LogNorm())
plt.xticks(size_bins)
plt.yticks(speed_bins)
for label in ax1.xaxis.get_ticklabels()[::2]:
    label.set_visible(False)
plt.xticks(rotation=0)
ax1.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
for label in ax1.yaxis.get_ticklabels()[::2]:
    label.set_visible(False)
plt.xlim(0,7)
plt.ylim(0,10)
plt.grid()
plt.xlabel('Particle Diameter (mm)',fontsize=10)
plt.ylabel('Fall Velocity (m/s)',fontsize=10)
plt.title('Valparaiso University Kallay-Christopher Hall\nParticle Size/Velocity Distrometer Spectrum (1-minute)')
#fig.colorbar(c)


ax1.annotate('Precipitation Type:  '+p_type_recent_text+'\nPrecipitation Rate:  '+str(p_rate[0])+' mm/hr  (liquid equiv.)', xy=(0.75, 1.04), xytext=(-15, -15), fontsize=12,
    xycoords='axes fraction', textcoords='offset points',
    bbox=dict(facecolor='None', edgecolor='None', alpha=1.0, boxstyle='round,pad=0.5'),
    horizontalalignment='left', verticalalignment='bottom',zorder=3)

ax1.annotate(date_string+'\n'+str(data[-1,4][0:-3])+' UTC', xy=(0.3, 1.04), xytext=(-15, -15), fontsize=12,
    xycoords='axes fraction', textcoords='offset points',
    bbox=dict(facecolor='None', edgecolor='None', alpha=1.0, boxstyle='round,pad=0.5'),
    horizontalalignment='right', verticalalignment='bottom',zorder=3)

#ax1.annotate('Precipitation Type:  '+p_type_recent_text+'\nPrecipitation Rate: '+str(p_rate[0])+' mm/hr', xy=(0.80, 1.00), xytext=(-15, -15), fontsize=12,
#    xycoords='axes fraction', textcoords='offset points',
#    bbox=dict(facecolor='white', edgecolor='black', alpha=1.0, boxstyle='round,pad=0.5'),
#    horizontalalignment='left', verticalalignment='top',zorder=3)

ax2 = fig.add_subplot(gs[-1,0])
b=plt.bar(np.arange(0.5,len(p_rate),1),p_rate[::-1],color=p_color_timeline[::-1])
plt.xlim(0,121)
if quarter_round(np.nanmax(p_rate))>0.25:
    ymax = quarter_round(np.nanmax(p_rate))
else:
    ymax = 0.25
plt.ylim(0,ymax)
x_labels = p_time[::-10]
x_labels.append(p_time[0])
plt.xticks(np.arange(0.5,len(p_rate),10),x_labels)
plt.xlabel('Time (UTC)',fontsize=10)
plt.ylabel('Rate (mm/hr)',fontsize=10)
plt.title('The Past 2-Hours of Precipitation Type and Liquid-Equivalent Rate',fontsize=12)
plt.grid()

#rain_patch = mpatches.Patch(color='green', label='Rain')
#drizzle_patch = mpatches.Patch(color='palegreen', label='Drizzle')
#snow_patch = mpatches.Patch(color='dodgerblue', label='Snow')
#unknown_patch = mpatches.Patch(color='k', label='Unknown')
#plt.legend(bbox_to_anchor=(1.12, 1), loc='upper right',handles=[(rain_patch,drizzle_patch,snow_patch,unknown_patch])

#red_patch = mpatches.Patch(color='red', label='Foo')
#plt.legend(handles=[red_patch])

fig.tight_layout(pad=0.7)


cbar_ax = fig.add_axes([0.96, 0.32, 0.020, 0.60])
fig.colorbar(c, cax=cbar_ax, extend="max")
plt.ylabel('Number of particles',fontsize=12)


leg_thick = 0.11625
leg_space = 0.01
k=0

for color_now,type_str in zip(type_c[::-1],type_strings[::-1]):
    lower = k
    k = k + leg_thick
    upper = k
    k = k + leg_space
    for i,j in zip([0,2,1],[122,123,124]):
        r1 = mpatches.Rectangle((j, (lower*ymax)), 1, (leg_thick*ymax),
            fill=True, color=color_now[i],clip_on=False)
        ax2.add_patch(r1)
    ax2.annotate(type_str, (125.25, (lower*ymax)),fontsize=10,
        bbox=dict(facecolor='None', edgecolor='None'),
        horizontalalignment='left', verticalalignment='bottom',
        zorder=3, annotation_clip=False)

ax2.annotate('Light', (121.0, (1.01*ymax)),fontsize=9,
    bbox=dict(facecolor='None', edgecolor='None'),
    horizontalalignment='left', verticalalignment='bottom',
    zorder=3, annotation_clip=False, rotation=45)
ax2.annotate('Moderate', (122.75, (1.01*ymax)),fontsize=9,
    bbox=dict(facecolor='None', edgecolor='None'),
    horizontalalignment='left', verticalalignment='bottom',
    zorder=3, annotation_clip=False, rotation=45)
ax2.annotate('Heavy', (124.5, (1.01*ymax)),fontsize=9,
    bbox=dict(facecolor='None', edgecolor='None'),
    horizontalalignment='left', verticalalignment='bottom',
    zorder=3, annotation_clip=False, rotation=45)

#snow
#for i,j in zip([0,2,1],[122,123,124]):
#    r1 = mpatches.Rectangle((j, (0.75*ymax)), 1, (0.1*ymax), 
#        fill=True, color=sn[i,:],clip_on=False)
#    ax2.add_patch(r1)
#ax2.annotate('Snow', (125.25, (0.75*ymax)),fontsize=10,
#    bbox=dict(facecolor='None', edgecolor='None'),
#    horizontalalignment='left', verticalalignment='bottom',
#    zorder=3, annotation_clip=False)

plt.savefig('/home/wxweb/http/experimental/dist_data/dist_spectrum_timeline.png',bbox_inches='tight',dpi=300)
print("Done.")
