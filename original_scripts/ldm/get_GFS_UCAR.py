from datetime import datetime, timedelta
import glob
import os

import wget

now = datetime.utcnow()

if (now.hour >= 11) and (now.hour <=16):
    hour = 6
elif (now.hour >= 17) and (now.hour <= 22):
    hour = 12
elif (now.hour >= 23) or (now.hour <= 4):
    if now.hour <= 4:
        now -= timedelta(days=1)
    hour = 18
else:
    hour = 0

date = datetime(now.year, now.month, now.day, hour)
os.system('pwd')
print(f'Working on GFS File for {date}')
print('Writing file to disk')
os.chdir('/data/ldmdata/model/gfs/')
ds = wget.download('https://thredds.ucar.edu/thredds/fileServer/grib/NCEP/GFS/'
                   f'Global_onedeg/GFS_Global_onedeg_{date:%Y%m%d_%H00}.grib2')
print(ds)
print('Finished writing file to disk')

print('Converting to netCDF')
#os.system(f"java -Xmx512m -classpath /opt/ldm/process_ldm/netcdfAll-5.2.0.jar ucar.nc2.dataset.NetcdfDataset -isLargeFile -in GFS_Global_onedeg_{date:%Y%m%d_%H00}.grib2 -out {date:%Y%m%d%H}_GFS.nc")
os.system(f"java -Xmx512m -classpath /opt/ldm/process_data/netcdfAll-5.2.0.jar ucar.nc2.write.Nccopy -isLargeFile -i GFS_Global_onedeg_{date:%Y%m%d_%H00}.grib2 -o {date:%Y%m%d%H}_gfs.nc")

for f in glob.glob(f'GFS_Global_onedeg_{date:%Y%m%d_%H00}*'):
    os.remove(f)

print('Finished Converting to netCDF')
