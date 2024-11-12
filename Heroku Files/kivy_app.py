from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import json
from datetime import datetime

SERVER_URL = "http://192.168.1.140:3000/trigger-search"  # server IP
EMAIL_ADDRESS = "pcarbajoderennes@gmail.com"  # email that sends notifications
EMAIL_PASSWORD = "azyn ntva wqsx bwxq" 
RECIPIENT_EMAIL = "pcarbajoderennes@gmail.com"

class SearchApp(App):
    def build(self):
        # main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # status 
        self.status_label = Label(
            text='Ready to search',
            size_hint_y=None,
            height=50
        )
        
        # results 
        self.results_label = Label(
            text='',
            size_hint_y=None,
            height=100,
            text_size=(400, None)
        )
        
        # search button
        search_button = Button(
            text='Run Random Search',
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5}
        )
        search_button.bind(on_press=self.trigger_search)
        
        # widgets to layout
        layout.add_widget(self.status_label)
        layout.add_widget(self.results_label)
        layout.add_widget(search_button)
        
        return layout
    
    def send_email(self, query, timestamp, file_links):
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = RECIPIENT_EMAIL
            msg['Subject'] = f"Search Results - {query}"
            
            body = f"""
            Search Query: {query}
            Timestamp: {timestamp}
            
            Results Files:
            """
            
            for file in file_links:
                body += f"\n{file['type'].capitalize()} File: {file['link']}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, text)
            server.quit()
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
    
    def trigger_search(self, instance):
        def search_task():
            try:
                self.status_label.text = 'Running search...'
                self.results_label.text = ''
                
                # request to server
                response = requests.post(SERVER_URL)
                result = response.json()
                
                if result.get('success'):
                    # update status labels
                    self.status_label.text = 'Search completed successfully!'
                    self.results_label.text = (
                        f"Query: {result['query']}\n"
                        f"Timestamp: {result['timestamp']}\n"
                        f"Ads Found: {'Yes' if result['had_ads'] else 'No'}"
                    )
                    
                    #email     
                    threading.Thread(
                        target=self.send_email,
                        args=(
                            result['query'],
                            result['timestamp'],
                            result['files']
                        )
                    ).start()
                else:
                    self.status_label.text = f'Error: {result.get("error", "Unknown error")}'
                    
            except Exception as e:
                self.status_label.text = f'Error: {str(e)}'
        
        threading.Thread(target=search_task).start()

if __name__ == '__main__':
    SearchApp().run()