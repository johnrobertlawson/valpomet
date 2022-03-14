#!/bin/csh


source /home/kgoebber/.bashrc
setenv PATH /anaconda/bin:$PATH

cd /var/www/html/ncep_models/gfs
if (!(-e /var/www/html/ncep_models/gfs/running.txt)) then
 touch running.txt

 python bergeron_GFS_4panel.py

 rm running.txt
else
 echo "I'm already running!"
endif


