from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json

def google_search_and_save_data(query):
    chrome_options = Options()
    chrome_options.add_argument("--headless") #runs automation in the background

    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)

    try:
        driver.get("https://www.google.com")

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q")) #waits until browser 
        )
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )

        cookies = driver.get_cookies()

        search_results = []
        result_elements = driver.find_elements(By.CSS_SELECTOR, "div.g")
        for element in result_elements[:5]:
            title_element = element.find_element(By.CSS_SELECTOR, "h3")
            link_element = element.find_element(By.CSS_SELECTOR, "a")
            snippet_element = element.find_element(By.CSS_SELECTOR, "div.VwiC3b")
            
            search_results.append({
                "title": title_element.text,
                "link": link_element.get_attribute("href"),
                "snippet": snippet_element.text
            })

        with open('google_cookies.json', 'w') as f:
            json.dump(cookies, f, indent=4)

        with open('search_results.json', 'w') as f:
            json.dump(search_results, f, indent=4)

        print(f"Cookies saved to 'google_cookies.json'")
        print(f"Search results saved to 'search_results.json'")

    finally:
        driver.quit()

search_query = "Best restaurants in Graz for solo diners?"
google_search_and_save_data(search_query)



