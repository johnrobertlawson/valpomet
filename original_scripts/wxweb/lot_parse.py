import requests
from bs4 import BeautifulSoup

url0 = 'https://www.weather.gov'
url1 = '/lot/weatherstory'
page = requests.get(url0+url1)

# Create a BeautifulSoup object
soup = BeautifulSoup(page.text, 'html.parser')

# Pull all text from the BodyText div
image_list = soup.find_all(class_='image') #finds all of the image tags in the html source
item = image_list[0].find('img').get('src') #pulls the img tag from the first image and then gets the src
print(item)

text_file = open("lot_img.txt", "w")
n = text_file.write(item)
text_file.close()
print('DONE!')
