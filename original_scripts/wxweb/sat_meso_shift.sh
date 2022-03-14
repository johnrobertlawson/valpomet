#!/usr/bin/bash

i=120
while [ $i -ge 0 ];
do
  j=$((i+1))
  mv /home/wxweb/public_html/satellite/meso/ch13/ch13_$i.jpg /home/wxweb/public_html/satellite/meso/ch13/ch13_$j.jpg
  i=$((i-1))
done
