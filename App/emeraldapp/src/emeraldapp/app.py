"""
emerald app is gonna be a cool project.
"""

from pathlib import Path
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.colors import rgb
import random
import asyncio
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import csv
import os
from datetime import datetime
from .queries import QUERIES

CURRENT_QUERIES = QUERIES

EMERALD_GREEN = rgb(46, 204, 113)  # emerald color 
WHITE = rgb(255, 255, 255)         # white

class QueryInterface:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.chrome_options)

    def perform_search(self, query):
        self.driver.get("https://www.google.com")
        search_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )

    def get_results(self):
        results = []
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
        )
        
        result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
        
        for element in result_elements[:10]:
            try:
                result_dict = {}
                
                try:
                    link_selectors = [
                        "div.yuRUbf > a",
                        "div.rc > a",
                        "a[jsname]",
                        "a[data-ved]",
                        "h3.r > a",
                        "h3 > a",
                        "a"
                    ]
                    
                    link_element = None
                    for selector in link_selectors:
                        try:
                            link_element = element.find_element(By.CSS_SELECTOR, selector)
                            if link_element:
                                break
                        except:
                            continue
                    
                    if link_element:
                        result_dict['url'] = link_element.get_attribute("href")
                        title_element = link_element.find_element(By.CSS_SELECTOR, "h3")
                        result_dict['title'] = title_element.text
                except Exception as e:
                    print(f"Error extracting title/URL: {str(e)}")
                    result_dict['url'] = ""
                    result_dict['title'] = ""

                try:
                    snippet_selectors = [
                        "div.VwiC3b",
                        "div.IsZvec",
                        "div.s",
                        "span.st",
                        "div[data-content-feature='1']"
                    ]
                    
                    snippet_text = ""
                    for selector in snippet_selectors:
                        try:
                            snippet_element = element.find_element(By.CSS_SELECTOR, selector)
                            if snippet_element:
                                snippet_text = snippet_element.text
                                break
                        except:
                            continue
                    
                    result_dict['snippet'] = snippet_text
                except:
                    result_dict['snippet'] = ""

                try:
                    displayed_url_selectors = [
                        "div.TbwUpd > cite",
                        "cite.iUh30",
                        "cite",
                        "div.UPmit > cite"
                    ]
                    
                    displayed_url = ""
                    for selector in displayed_url_selectors:
                        try:
                            url_element = element.find_element(By.CSS_SELECTOR, selector)
                            if url_element:
                                displayed_url = url_element.text
                                break
                        except:
                            continue
                    
                    result_dict['displayed_url'] = displayed_url
                except:
                    result_dict['displayed_url'] = ""

                if result_dict.get('url') or result_dict.get('title'):
                    results.append(result_dict)
                    
            except Exception as e:
                print(f"Error processing result: {str(e)}")
                continue
                
        return results

    def get_ads(self):
        ads = []
        try:
            top_ads = self.driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Ads']")
            side_ads = self.driver.find_elements(By.CSS_SELECTOR, "div.commercial-unit-desktop-rhs")
            bottom_ads = self.driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Ads'] > div.uEierd")
            
            all_ad_containers = top_ads + side_ads + bottom_ads
            
            for ad_container in all_ad_containers:
                try:
                    ad_dict = {}
                    
                    # ad title
                    try:
                        title_element = ad_container.find_element(By.CSS_SELECTOR, "div.CCgQ5")
                        ad_dict['title'] = title_element.text
                    except:
                        ad_dict['title'] = ""
                    
                    # ad URL
                    try:
                        url_element = ad_container.find_element(By.CSS_SELECTOR, "a")
                        ad_dict['url'] = url_element.get_attribute("href")
                    except:
                        ad_dict['url'] = ""
                    
                    # ad description
                    try:
                        desc_element = ad_container.find_element(By.CSS_SELECTOR, "div.MUxGbd")
                        ad_dict['description'] = desc_element.text
                    except:
                        ad_dict['description'] = ""
                    
                    # displayed URL
                    try:
                        displayed_url_element = ad_container.find_element(By.CSS_SELECTOR, "span.Zu0yb")
                        ad_dict['displayed_url'] = displayed_url_element.text
                    except:
                        ad_dict['displayed_url'] = ""
                    
                    if any(ad_dict.values()):  # only append if one value found
                        ads.append(ad_dict)
                        
                except Exception as e:
                    print(f"Error extracting ad: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error in get_ads: {str(e)}")
            
        return ads

    def get_cookies(self):
        return self.driver.get_cookies()

    def close(self):
        self.driver.quit()

class SearchApp(toga.App):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_dir = os.path.dirname(os.path.dirname(current_dir))
        self.results_dir = os.path.join(self.project_dir, 'Results')
        os.makedirs(self.results_dir, exist_ok=True)

    def startup(self):
        self.main_window = toga.MainWindow(title="Search Query App")
        
        # main container with bg color 
        main_container = toga.Box(style=Pack(
            direction=COLUMN,
            padding=20,
            background_color=EMERALD_GREEN
        ))
        
        # style white text 
        label_style = Pack(
            padding=(5, 10),
            color=WHITE,
            font_weight='bold'
        )
        
        # button style 
        button_style = Pack(
            padding=(10, 20),
            background_color=WHITE,
            color=EMERALD_GREEN,
            font_weight='bold'
        )
        
        # labels w/ white text 
        self.path_label = toga.Label(
            f"Results Directory: {self.results_dir}",
            style=label_style
        )
        self.json_path_label = toga.Label(
            "JSON File: Not Created",
            style=label_style
        )
        self.csv_path_label = toga.Label(
            "CSV File: Not Created",
            style=label_style
        )
        self.progress_label = toga.Label(
            "Ready to search",
            style=label_style
        )
        
        # button custom style 
        search_button = toga.Button(
            "Perform Search",
            on_press=self.handle_search,
            style=button_style
        )
        
        open_folder_button = toga.Button(
            "Open Results Folder",
            on_press=self.open_results_folder,
            style=button_style
        )
        
        # add elements to main container 
        main_container.add(self.progress_label)
        main_container.add(search_button)
        main_container.add(open_folder_button)
        main_container.add(self.path_label)
        main_container.add(self.json_path_label)
        main_container.add(self.csv_path_label)
        
        # main container = window pop-up
        self.main_window.content = main_container
        self.main_window.show()

    async def open_results_folder(self, widget):
        if os.path.exists(self.results_dir):
            if os.sys.platform == 'darwin':  # macOS
                os.system(f'open "{self.results_dir}"')
            elif os.sys.platform == 'win32':  # Windows
                os.system(f'explorer "{self.results_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{self.results_dir}"')
        else:
            self.progress_label.text = "Results folder not found!"

    async def perform_search_task(self, query):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        interface = QueryInterface()
        
        try:
            interface.perform_search(query)
            search_results = interface.get_results()
            ads = interface.get_ads()
            cookies = interface.get_cookies()
            
            # csv and kson
            csv_path = os.path.join(self.results_dir, f'search_results_{timestamp}.csv')
            self.csv_path_label.text = f"CSV File: {csv_path}"
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Query', 'Title', 'URL', 'Displayed URL', 'Snippet'])
                for result in search_results:
                    writer.writerow([
                        query,
                        result.get('title', ''),
                        result.get('url', ''),
                        result.get('displayed_url', ''),
                        result.get('snippet', '')
                    ])
            
            json_path = os.path.join(self.results_dir, f'full_results_{timestamp}.json')
            self.json_path_label.text = f"JSON File: {json_path}"
            
            with open(json_path, 'w', encoding='utf-8') as jsonfile:
                json.dump({
                    "query": query,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "search_results": search_results,
                    "advertisements": ads,
                    "cookies": cookies
                }, jsonfile, indent=4)
            
            self.progress_label.text = f"Search completed: {query}"
            
        except Exception as e:
            self.progress_label.text = f"Error: {str(e)}"
        
        finally:
            interface.close()

    async def handle_search(self, widget):
        widget.enabled = False
        self.progress_label.text = "Searching..."
        query = random.choice(CURRENT_QUERIES)
        await self.perform_search_task(query)
        widget.enabled = True

def main():
    return SearchApp()

if __name__ == '__main__':
    app = main()
    app.main_loop()