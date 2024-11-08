from flask import Flask, jsonify, render_template_string, request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from queries import QUERIES
import json
import csv
import os
import socket
from datetime import datetime
import random

app = Flask(__name__)

FOLDER_ID = "1BebuFtSOBrJDUiElkMj0RSrb7kKPo3A8"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_google_drive_service():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Error setting up Drive service: {str(e)}")
        raise

class QueryInterface:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)

    def perform_search(self, query):
        try:
            self.driver.get("https://www.google.com")
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
        except Exception as e:
            print(f"Error in perform_search: {str(e)}")
            raise

    def get_results(self):
        results = []
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
            )
            
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            for element in result_elements[:10]:
                try:
                    result_dict = {}
                    title_element = element.find_element(By.CSS_SELECTOR, "h3")
                    link_element = element.find_element(By.CSS_SELECTOR, "a")
                    result_dict['title'] = title_element.text
                    result_dict['url'] = link_element.get_attribute("href")
                    results.append(result_dict)
                except Exception as e:
                    print(f"Error processing result: {str(e)}")
                    continue
                    
            return results
        except Exception as e:
            print(f"Error in get_results: {str(e)}")
            return results

    def close(self):
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Error closing driver: {str(e)}")

@app.route('/')
def home():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Search Interface</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background-color: #f5f5f5;
                }
                .container { 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .search-box { 
                    margin: 20px 0; 
                }
                button { 
                    padding: 10px 20px; 
                    background: #4CAF50; 
                    color: white; 
                    border: none; 
                    cursor: pointer;
                    border-radius: 4px;
                    font-size: 16px;
                }
                button:hover {
                    background: #45a049;
                }
                .results { 
                    margin-top: 20px; 
                }
                .error {
                    color: red;
                    padding: 10px;
                    border: 1px solid red;
                    border-radius: 4px;
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Search Interface</h1>
                <div class="search-box">
                    <button onclick="performSearch()">Run Random Search</button>
                </div>
                <div id="results" class="results"></div>
            </div>

            <script>
            function performSearch() {
                document.getElementById('results').innerHTML = 'Searching...';
                
                fetch('/trigger-search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('results').innerHTML = `
                            <div>
                                <h3>Search completed!</h3>
                                <p>Query: ${data.query}</p>
                                <p>Results saved to Google Drive</p>
                                <p>File ID: ${data.file_id}</p>
                                ${data.file_link ? `<p><a href="${data.file_link}" target="_blank">View file</a></p>` : ''}
                            </div>`;
                    } else {
                        document.getElementById('results').innerHTML = 
                            `<div class="error">Error: ${data.error}</div>`;
                    }
                })
                .catch(error => {
                    document.getElementById('results').innerHTML = 
                        `<div class="error">Error: ${error}</div>`;
                });
            }
            </script>
        </body>
        </html>
    """)

@app.route('/trigger-search', methods=['POST'])
def trigger_search():
    try:
        # Select random query from list
        query = random.choice(QUERIES)
        
        interface = QueryInterface()
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        try:
            # search
            interface.perform_search(query)
            search_results = interface.get_results()
            
            # temporary csv file 
            csv_filename = f'search_results_{timestamp}.csv'
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Query', 'Title', 'URL'])
                for result in search_results:
                    writer.writerow([
                        query,
                        result.get('title', ''),
                        result.get('url', '')
                    ])
            
            # upload to drive
            try:
                drive_service = get_google_drive_service()
                file_metadata = {
                    'name': csv_filename,
                    'parents': [FOLDER_ID]
                }
                
                media = MediaFileUpload(
                    csv_filename,
                    mimetype='text/csv',
                    resumable=True
                )
                
                file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, webViewLink'
                ).execute()
                
                print(f"File uploaded to Drive with ID: {file.get('id')}")
                
                return jsonify({
                    'success': True,
                    'message': 'Search completed and saved to Google Drive',
                    'file_id': file.get('id'),
                    'file_link': file.get('webViewLink'),
                    'query': query
                })
                
            except Exception as e:
                print(f"Error uploading to Drive: {str(e)}")
                raise
                
            finally:
                if os.path.exists(csv_filename):
                    os.remove(csv_filename)
            
        finally:
            interface.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True, host='0.0.0.0', port=3000)