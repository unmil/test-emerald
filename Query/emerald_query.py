from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import random
import csv

class QueryInterface:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.chrome_options)

    def perform_search(self, query):
        self.driver.get("https://www.google.com")
        search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "search")))

    def get_results(self):
        results = []
        result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
        for element in result_elements[:10]:
            title_element = element.find_element(By.CSS_SELECTOR, "h3")
            results.append(title_element.text)
        return results

    def get_ads(self):
        ads = []
        ad_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.uEierd")
        for ad in ad_elements:
            ad_title = ad.find_element(By.CSS_SELECTOR, "divbd.CCgQ5.vCa9Yd.QfkTvb.MUxG.v0nnCb").text
            ads.append(ad_title)
        return ads

    def get_cookies(self):
        return self.driver.get_cookies()

    def close(self):
        self.driver.quit()

def process_single_query(query):
    interface = QueryInterface()
    
    interface.perform_search(query)
    
    search_results = interface.get_results()
    ads = interface.get_ads()
    cookies = interface.get_cookies()
    
    interface.close()

    with open('search_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Query'] + [f'Result {i+1}' for i in range(10)])
        writer.writerow([query] + search_results)

    full_results = {
        "query": query,
        "results": search_results,
        "ads": ads,
        "cookies": cookies
    }
    with open('full_results.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(full_results, jsonfile, indent=4)

    print("Results saved to 'search_results.csv' and 'full_results.json'")

if __name__ == "__main__":
    sample_query = "Tips for making friends through hobby groups in Graz?"
    process_single_query(sample_query)

