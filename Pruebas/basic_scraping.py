from bs4 import BeautifulSoup
import requests


url = 'https://carbajo.xyz/'

r = requests.get(url)
print(r.status_code)

soup = BeautifulSoup(r.text, 'html.parser')

print(soup)
