import requests 
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# def google_search_cookies(query):
#     url = f"https://www.google.com/search?q={query}"
#     response  = requests.get(url)
#     cookies = response.cookies 
#     cookie_dict = requests.utils.dict_from_cookiejar(cookies)

#     with open('google_cookies.txt', 'w') as f: 
#         json.dump(cookie_dict, f , indent=4)

#     print(f"Cookies saved to file.")

# search_query = "Best restaurants in Graz for solo diners?"
# google_search_cookies(search_query)

def google_search_and_save_cookies(query):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)

    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)

    try:
        driver.get("https://www.google.com")

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )

        cookies = driver.get_cookies()

        with open('detailed_google_cookies.txt', 'w') as f:
            json.dump(cookies, f, indent=4)

        print(f"Detailed cookies saved to 'detailed_google_cookies.txt'")

    finally:
        driver.quit()

search_query = "example search"
google_search_and_save_cookies(search_query)    