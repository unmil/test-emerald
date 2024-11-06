from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.google.com/search?q=best+knee+brace+for+knee+problems&oq=best+knee+brace+for+knee+problems&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIICAEQABgWGB4yCAgCEAAYFhgeMggIAxAAGBYYHjIICAQQABgWGB4yCAgFEAAYFhgeMggIBhAAGBYYHjIICAcQABgWGB4yCAgIEAAYFhgeMggICRAAGBYYHtIBCTEwMTAzajBqOagCALACAQ&sourceid=chrome&ie=UTF-8')

html = driver.page_source

with open('page.html', 'w', encoding='utf-8') as f:
    f.write(html)

driver.quit()


print("HTML has been saved")