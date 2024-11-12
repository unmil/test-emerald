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
import logging

class Config:
    def __init__(self):
        self.is_production = False  # change to true when deploying
        self.server_url = "http://192.168.1.140:3000" if not self.is_production else "YOUR_PRODUCTION_URL"
        self.folder_id = "1BebuFtSOBrJDUiElkMj0RSrb7kKPo3A8"

config = Config()

# save in case of adding email functionality 
# EMAIL_ADDRESS = "pcarbajoderennes@gmail.com"  
# EMAIL_PASSWORD = "app password"  
# RECIPIENT_EMAIL = "pcarbajoderennes@gmail.com"

app = Flask(__name__)

FOLDER_ID = config.folder_id 
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
        
        if config.is_production:
            # prod settings 
            self.chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            service = Service(os.environ.get("CHROMEDRIVER_PATH"))
        else:
            # local dev settings 
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
            
            for position, element in enumerate(result_elements[:10], 1):
                try:
                    result_dict = {
                        'position': position,
                        'title': '',
                        'url': '',
                        'snippet': ''
                    }
                    
                    # getting title and url 
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, "h3")
                        link_element = element.find_element(By.CSS_SELECTOR, "a")
                        result_dict['title'] = title_element.text
                        result_dict['url'] = link_element.get_attribute("href")
                    except Exception as e:
                        print(f"Error getting title/url: {str(e)}")
                    
                    # snippet
                    try:
                        snippet_element = element.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                        result_dict['snippet'] = snippet_element.text
                    except Exception as e:
                        print(f"Error getting snippet: {str(e)}")
                    
                    results.append(result_dict)
                except Exception as e:
                    print(f"Error processing result {position}: {str(e)}")
                    continue
            
            return results
        except Exception as e:
            print(f"Error in get_results: {str(e)}")
            return results

    def get_ads(self):
        ads = []
        try:
            # see if there are ads
            ad_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.uEierd")
            
            if not ad_elements:
                print("No ads found")
                return []
            
            for position, ad in enumerate(ad_elements, 1):
                try:
                    ad_dict = {
                        'position': position,
                        'title': '',
                        'display_url': '',
                        'actual_url': '',
                        'description': ''
                    }
                    
                    # title
                    try:
                        title_element = ad.find_element(By.CSS_SELECTOR, "div.CCgQ5 span")
                        ad_dict['title'] = title_element.text
                    except Exception as e:
                        print(f"Error getting ad title: {str(e)}")
                    
                    # URLs
                    try:
                        url_element = ad.find_element(By.CSS_SELECTOR, "div.v5yQqb a")
                        ad_dict['actual_url'] = url_element.get_attribute("href")
                        ad_dict['display_url'] = url_element.text
                    except Exception as e:
                        print(f"Error getting ad URLs: {str(e)}")
                    
                    # Get description
                    try:
                        desc_element = ad.find_element(By.CSS_SELECTOR, "div.MUxGbd")
                        ad_dict['description'] = desc_element.text
                    except Exception as e:
                        print(f"Error getting ad description: {str(e)}")
                    
                    ads.append(ad_dict)
                    
                except Exception as e:
                    print(f"Error processing ad {position}: {str(e)}")
                    continue
            
            return ads
        except Exception as e:
            print(f"Error in get_ads: {str(e)}")
            return []

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
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 40px;
                    background-color: #f5f5f5;
                    min-height: 100vh;
                }
                
                .container { 
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                
                h1 {
                    text-align: center;
                    color: #2c3e50;
                    margin-bottom: 30px;
                    font-weight: 600;
                }
                
                .search-box { 
                    margin: 30px 0;
                    text-align: center;
                }
                
                button { 
                    padding: 15px 35px;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    cursor: pointer;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 500;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
                }
                
                button:hover {
                    background: #45a049;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
                }
                
                button:active {
                    transform: translateY(0);
                    box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
                }
                
                button:disabled {
                    background: #cccccc;
                    cursor: not-allowed;
                    transform: none;
                    box-shadow: none;
                }
                
                .results { 
                    margin-top: 25px;
                    padding: 15px;
                }
                
                .error {
                    color: #e74c3c;
                    padding: 15px;
                    border: 1px solid #e74c3c;
                    border-radius: 8px;
                    margin-top: 15px;
                    background-color: #fdf3f2;
                }
                
                .success {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                    border: 1px solid #e9ecef;
                    animation: fadeIn 0.5s ease-out;
                }
                
                .success h3 {
                    color: #2c3e50;
                    margin-top: 0;
                    margin-bottom: 15px;
                }
                
                .success p {
                    margin: 10px 0;
                    color: #34495e;
                    line-height: 1.5;
                }
                
                .success h4 {
                    color: #2c3e50;
                    margin: 20px 0 10px 0;
                }
                
                .file-link {
                    color: #4CAF50;
                    text-decoration: none;
                    margin: 8px 0;
                    display: inline-block;
                    padding: 8px 15px;
                    background-color: #f1f8f1;
                    border-radius: 6px;
                    transition: all 0.2s ease;
                }
                
                .file-link:hover {
                    background-color: #e8f5e9;
                    text-decoration: none;
                    transform: translateX(5px);
                }
                
                .loading {
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 16px;
                }
                
                .loading::after {
                    content: '';
                    animation: dots 1.4s infinite;
                }
                
                @keyframes dots {
                    0%, 20% { content: '.'; }
                    40% { content: '..'; }
                    60% { content: '...'; }
                    80%, 100% { content: ''; }
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Search Interface</h1>
                <div class="search-box">
                    <button onclick="performSearch()" id="searchButton">Run Random Search</button>
                </div>
                <div id="results" class="results"></div>
            </div>

            <script>
            async function performSearch() {
                const resultsDiv = document.getElementById('results');
                const searchButton = document.getElementById('searchButton');
                
                try {
                    // Disable button while searching
                    searchButton.disabled = true;
                    resultsDiv.innerHTML = '<div class="loading">Searching</div>';
                    
                    const response = await fetch('/trigger-search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({})
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        let html = `
                            <div class="success">
                                <h3>🎉 Search completed!</h3>
                                <p><strong>Query:</strong> ${data.query}</p>
                                <p><strong>Timestamp:</strong> ${data.timestamp}</p>
                                <p><strong>Ads found:</strong> ${data.had_ads ? '✅ Yes' : '❌ No'}</p>
                                <h4>📁 Uploaded files:</h4>
                        `;
                        
                        data.files.forEach(file => {
                            html += `
                                <a href="${file.link}" target="_blank" class="file-link">
                                    ${file.type === 'results' ? '📊' : '🎯'} View ${file.type} file
                                </a>
                            `;
                        });
                        
                        html += '</div>';
                        resultsDiv.innerHTML = html;
                    } else {
                        resultsDiv.innerHTML = `
                            <div class="error">
                                ❌ Error: ${data.error}
                            </div>
                        `;
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `
                        <div class="error">
                            ❌ Error: ${error}
                        </div>
                    `;
                } finally {
                    // Re-enable button after search completes
                    searchButton.disabled = false;
                }
            }
            </script>
        </body>
        </html>
    """)

def create_or_get_folder(drive_service, folder_name, parent_id=FOLDER_ID):
    """Create a folder in Google Drive or get its ID if it exists."""
    try:
        # check folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents"
        results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        
        # create folder if it doesn't exist 
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = drive_service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        return folder.get('id')
        
    except Exception as e:
        print(f"Error creating/getting folder {folder_name}: {str(e)}")
        raise

@app.route('/trigger-search', methods=['POST'])
def trigger_search():
    try:
        query = random.choice(QUERIES)
        date = datetime.now().strftime('%Y-%m-%d')
        timestamp = datetime.now().strftime('%H-%M-%S')
        
        interface = QueryInterface()
        drive_service = get_google_drive_service()
        
        try:            
            interface.perform_search(query)
            search_results = interface.get_results()
            ads = interface.get_ads()
            
            query_folder_id = create_or_get_folder(drive_service, query.replace(" ", "_"))
            date_folder_id = create_or_get_folder(drive_service, date, query_folder_id)
            
            uploaded_files = []
            
            # save and upload search results 
            results_filename = f'results_{timestamp}.csv'
            with open(results_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Position', 'Title', 'URL', 'Snippet'])
                for result in search_results:
                    writer.writerow([
                        f"{date} {timestamp}",
                        result['position'],
                        result['title'],
                        result['url'],
                        result['snippet']
                    ])
            
            # upload results file
            file_metadata = {
                'name': results_filename,
                'parents': [date_folder_id]
            }
            media = MediaFileUpload(results_filename, mimetype='text/csv', resumable=True)
            results_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            uploaded_files.append({
                'type': 'results',
                'id': results_file.get('id'),
                'link': results_file.get('webViewLink')
            })
            
            if ads:
                ads_filename = f'ads_{timestamp}.csv'
                with open(ads_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Timestamp', 'Position', 'Title', 'Display URL', 'Actual URL', 'Description'])
                    for ad in ads:
                        writer.writerow([
                            f"{date} {timestamp}",
                            ad['position'],
                            ad['title'],
                            ad['display_url'],
                            ad['actual_url'],
                            ad['description']
                        ])
                
                file_metadata = {
                    'name': ads_filename,
                    'parents': [date_folder_id]
                }
                media = MediaFileUpload(ads_filename, mimetype='text/csv', resumable=True)
                ads_file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, webViewLink'
                ).execute()
                uploaded_files.append({
                    'type': 'ads',
                    'id': ads_file.get('id'),
                    'link': ads_file.get('webViewLink')
                })
                
                if os.path.exists(ads_filename):
                    os.remove(ads_filename)
            
            if os.path.exists(results_filename):
                os.remove(results_filename)
            
            return jsonify({
                'success': True,
                'message': 'Search completed and saved',
                'query': query,
                'timestamp': f"{date} {timestamp}",
                'files': uploaded_files,
                'had_ads': bool(ads)
            })
            
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
