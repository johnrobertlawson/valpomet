from datetime import datetime, timedelta
import glob
import os

import wget

now = datetime.utcnow()

if (now.hour >= 9) and (now.hour <=13):
    hour = 6
elif (now.hour >= 14) and (now.hour <= 19):
    hour = 12
elif (now.hour >= 20) or (now.hour <= 1):
    if now.hour <= 4:
        now -= timedelta(days=1)
    hour = 18
else:
    hour = 0

date = datetime(now.year, now.month, now.day, hour)
os.system('pwd')
print(f'Working on NAM File for {date}')
print('Writing file to disk')
os.chdir('/data/ldmdata/model/nam/')
ds = wget.download('https://thredds.ucar.edu/thredds/fileServer/grib/NCEP/NAM/CONUS_12km/'
                   f'NAM_CONUS_12km_{date:%Y%m%d_%H00}.grib2')
print(ds)
print('Finished writing file to disk')

print('Converting to netCDF')
#os.system(f"java -Xmx512m -classpath /opt/ldm/process_ldm/netcdfAll-5.2.0.jar ucar.nc2.dataset.NetcdfDataset -isLargeFile -in NAM_Global_onedeg_{date:%Y%m%d_%H00}.grib2 -out {date:%Y%m%d%H}_NAM.nc")
os.system(f"java -Xmx512m -classpath /opt/ldm/process_data/netcdfAll-5.2.0.jar ucar.nc2.write.Nccopy -isLargeFile -i NAM_CONUS_12km_{date:%Y%m%d_%H00}.grib2 -o {date:%Y%m%d%H}_nam.nc")

for f in glob.glob(f'NAM_CONUS_12km_{date:%Y%m%d_%H00}*'):
    os.remove(f)

print('Finished Converting to netCDF')
