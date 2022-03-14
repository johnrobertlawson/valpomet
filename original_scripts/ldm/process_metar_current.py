from datetime import datetime, timedelta

from metpy.io import metar
from metpy.plots import declarative
from metpy.units import units
import pandas as pd

cur_date = datetime.utcnow()

if cur_date.minute < 14:
    date = cur_date -  timedelta(hours=1)
else:
    date = cur_date

df_cur = metar.parse_metar_file(f'/data/ldmdata/surface/sao/{date:%Y%m%d%H}_sao.wmo', year=date.year, month=date.month)

if date.hour == 0:
    df_cur.date_time[df_cur.date_time > cur_date] = (df_cur.date_time[df_cur.date_time > cur_date].astype('O')
                                                     - relativedelta(months=+1))

try:
    df_day = pd.read_csv(f'/data/ldmdata/surface/csv/{date:%Y%m%d}_wmo.csv')
    df_day = df_day.append(df_cur, ignore_index=True)
except:
    print('I GOT TO THE EXCEPT')
    print(date)
    df_day = df_cur

df_day = df_day.drop_duplicates()
df_day.to_csv(f'/data/ldmdata/surface/csv/{date:%Y%m%d}_wmo.csv', index=False)
