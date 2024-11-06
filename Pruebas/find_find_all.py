from bs4 import BeautifulSoup
import requests 

url = 'https://carbajo.xyz/'
r  = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
# print(soup) <-- will print all the html code in a structured way 
print(soup.find("div")) #finding the first div / use find_all for all 'div' in the html code 

print(soup.find('div', class_='content').text) # pulls in content from specific div class .text will give you just the text from that div

