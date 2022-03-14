from datetime import datetime, timedelta
from dateutil.relativedelta import *

from metpy.io import metar
from metpy.plots import declarative
from metpy.units import units

cur_date = datetime.utcnow()

date = datetime(cur_date.year, cur_date.month, cur_date.day) - timedelta(days=1)

for hour in range(24):
    print(f'/data/ldmdata/surface/sao/{date:%Y%m%d}{hour:02d}_sao.wmo')
    df = metar.parse_metar_file(f'/data/ldmdata/surface/sao/{date:%Y%m%d}{hour:02d}_sao.wmo', year=date.year, month=date.month)
    if hour == 0:
        df.date_time[df.date_time > date] = df.date_time[df.date_time > date].astype('O') - relativedelta(months=+1)
        df_day = df
    else:
        try:
            df_day = df_day.append(df)
        except:
            df_day = df

df_day.to_csv(f'/data/ldmdata/surface/csv/{date:%Y%m%d}_wmo.csv', index=False)
