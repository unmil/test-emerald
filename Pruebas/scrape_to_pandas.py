from bs4 import BeautifulSoup
import requests 

url = 'https://www.scrapethissite.com/pages/forms/'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')

# print(soup.find_all('th')) table column names 
print(soup.find_all('td')) # data for the table 
