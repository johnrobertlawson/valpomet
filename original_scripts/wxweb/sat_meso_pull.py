import urllib.request
import requests
from subprocess import call

old = open("/home/wxweb/public_html/KCH_monitors/oldfile.txt", "r")
old_file = old.read()
print(old_file)

url = 'https://cdn.star.nesdis.noaa.gov/GOES16/ABI/MESO/M1/13/'
fp = urllib.request.urlopen(url)
myfile = fp.readlines()
fp.close()

files=[]
for line in myfile:
    if "1000x1000" in line.decode("utf8"):
        data = line.decode("utf8")
        data = data.split('"')
        files.append(data[1])
latest_file=files[-1]
print(latest_file)

url = url+latest_file

if latest_file != old_file:
    print("NEED TO UPDATE")
    call("/home/wxweb/public_html/KCH_monitors/sat_meso_shift.sh", shell=True)
    myfile = requests.get(url)
    open('/home/wxweb/public_html/satellite/meso/ch13/ch13_0.jpg', 'wb').write(myfile.content)
    
    text_file = open("/home/wxweb/public_html/KCH_monitors/oldfile.txt", "w")
    text_file.write(latest_file)
    text_file.close()
else:
    print("No need to update...")
