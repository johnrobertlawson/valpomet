#!/usr/bin/bash

DIRECTORY=https://cdn.star.nesdis.noaa.gov/GOES16/ABI/CONUS/GEOCOLOR/
FILETIME=$(date +"%Y%j%H%M" --date='7 minutes ago')

echo "7 minutes ago:"
echo $FILETIME

FILEFULL="${DIRECTORY}${FILETIME}_GOES16-ABI-CONUS-GEOCOLOR-2500x1500.jpg"
echo $FILEFULL

if curl --head --silent --fail $FILEFULL 2> /dev/null;
 then
  echo "This page exists."
  /usr/bin/wget -S $FILEFULL -O /home/wxweb/public_html/satellite/conus/temp/geocolor_temp.jpg
 else
  echo "This page does not exist."
fi

FILE_TEMP=/home/wxweb/public_html/satellite/conus/temp/geocolor_temp.jpg
FILE_CUR=/home/wxweb/public_html/satellite/conus/geocolor/geocolor_0.jpg
OLDTIME=0
TEMPTIME=$(stat $FILE_TEMP -c %Y)
CURTIME=$(stat $FILE_CUR -c %Y)
TIMEDIFF=$(expr $TEMPTIME - $CURTIME)

echo $TIMEDIFF

if [ $TIMEDIFF -gt $OLDTIME ]; then
  i=36
  while [ $i -ge 0 ];
  do
    j=$((i+1))
    mv /home/wxweb/public_html/satellite/conus/geocolor/geocolor_$i.jpg /home/wxweb/public_html/satellite/conus/geocolor/geocolor_$j.jpg
    i=$((i-1))
  done
  cp --preserve=timestamps /home/wxweb/public_html/satellite/conus/temp/geocolor_temp.jpg /home/wxweb/public_html/satellite/conus/geocolor/geocolor_0.jpg
fi
