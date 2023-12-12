import requests
from bs4 import BeautifulSoup
import threading
from urllib.parse import urlparse 
import time

class VIS:
    def __init__(self, url: str, username: str, password: str, name: str) -> None:
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.url = url
        self.name = name
        self._login()

    def _login(self) -> None:
        # Get CSRF token
        host = urlparse(self.url).netloc
        payload = {}
        headers = {
          'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
          'sec-ch-ua-mobile': '?0',
          'sec-ch-ua-platform': '"Windows"',
          'Upgrade-Insecure-Requests': '1',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
          'Sec-Fetch-Site': 'same-origin',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-Dest': 'document',
          'host': f'{host}'
        }
        response = self.session.get(self.url, headers=headers, data=payload)
        cookies: dict[str, str] = self.session.cookies.get_dict()
        if response.status_code != 200:
            raise Exception("Unable to connect to VIS")
        # Scrap CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        return_input = soup.find('input', {'name': 'return'})
        csrf_token = return_input.find_next_sibling('input')['name']
        # Login Post Request
        payload = f"""Submit=Log%20in&{csrf_token}=1&option=com_users&password={self.password}&return=aHR0cHM6Ly92aXMudml0cm94LmNvbS5teS9hbnRpX2JyaWJlcnkvaW5kZXgucGhwL0FudGlfYnJpYmVyeS9pbmRleA%3D%3D&task=user.login&username={self.username}"""
        headers = {
          'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
          'sec-ch-ua-mobile': '?0',
          'sec-ch-ua-platform': '"Windows"',
          'Upgrade-Insecure-Requests': '1',
          'Content-Type': 'application/x-www-form-urlencoded',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
          'Sec-Fetch-Site': 'same-origin',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-User': '?1',
          'Sec-Fetch-Dest': 'document',
          'host': f'{host}',
          'Cookie': f'{list(cookies)[0]}={list(cookies.values())[0]}'
        }
        response = self.session.post(f'{self.url}index.php', headers=headers, data=payload, allow_redirects=False)
        headers = {
          'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
          'sec-ch-ua-mobile': '?0',
          'sec-ch-ua-platform': '"Windows"',
          'Upgrade-Insecure-Requests': '1',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
          'Sec-Fetch-Site': 'same-origin',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-User': '?1',
          'Sec-Fetch-Dest': 'document',
          'host': f'{host}',
          'Cookie': f'{list(cookies)[0]}={list(cookies.values())[0]}; joomla_user_state=logged_in'
        }
        response = self.session.get(self.url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        login_greeting = soup.find(class_="login-greeting")
        if login_greeting is None:
            raise Exception("Unable to login to VIS")
        if self.name not in login_greeting.text:
            raise Exception("Login to VIS with wrong account")
        # Update new headers
        headers = {
          'Cookie': f'{list(cookies)[0]}={list(cookies.values())[0]}; joomla_user_state=logged_in'
        }
        self.session.headers.update(headers)
        return
    
    def getUserList(self, url: str) -> str:
        response = self.session.get(url)
        if (response.status_code != 200):
            raise Exception("Unable to get user list")
        content = response.text
        return content
      
    def getUserDetails(self, userID: str) -> str:
        url = f"{self.url}index.php?option=com_users&task=user.edit&id={userID}"
        pass
    
    def searchUser(self, name: str):
        pass
