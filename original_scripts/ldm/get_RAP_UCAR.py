from datetime import datetime, timedelta
import glob
import os

import wget

now = datetime.utcnow()

date = datetime(now.year, now.month, now.day, now.hour-2)
os.system('pwd')
print(f'Working on RAP File for {date}')
print('Writing file to disk')
os.chdir('/data/ldmdata/model/rap/')

ds = wget.download('https://thredds.ucar.edu/thredds/fileServer/grib/NCEP/RAP/CONUS_13km/'
                   f'RR_CONUS_13km_{date:%Y%m%d_%H00}.grib2')
print(ds)
print('Finished writing file to disk')

print('Converting to netCDF')
#os.system(f"java -Xmx512m -classpath /opt/ldm/process_ldm/netcdfAll-5.2.0.jar ucar.nc2.dataset.NetcdfDataset -isLargeFile -in RUC_Global_onedeg_{date:%Y%m%d_%H00}.grib2 -out {date:%Y%m%d%H}_RUC.nc")
os.system(f"java -Xmx512m -classpath /opt/ldm/process_data/netcdfAll-5.2.0.jar ucar.nc2.write.Nccopy -isLargeFile -i RR_CONUS_13km_{date:%Y%m%d_%H00}.grib2 -o {date:%Y%m%d%H}_rap.nc")

for f in glob.glob(f'RR_CONUS_13km_{date:%Y%m%d_%H00}*'):
    os.remove(f)

print('Finished Converting to netCDF')
