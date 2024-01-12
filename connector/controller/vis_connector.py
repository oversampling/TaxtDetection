import json
import re
import requests
from bs4 import BeautifulSoup
import threading
from urllib.parse import urlparse 
import time
from model.cache_model import UserList
from model import cache_controller
from sqlalchemy.orm import Session

class VIS:
    def __init__(self, vis_url: str, userlist_url: str, username: str, password: str) -> None:
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.vis_url = vis_url
        self.userlist_url = userlist_url
        self.csrf_token: str | None = None
        self.cookies: dict[str, str] | None = None
        self.host = urlparse(self.vis_url).netloc
        self.name = self._login()

    def _login(self) -> str:
        # Get CSRF token
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
          'host': f'{self.host}'
        }
        response = self.session.get(self.vis_url, headers=headers, data=payload)
        cookies: dict[str, str] = self.session.cookies.get_dict()
        if response.status_code != 200:
            raise Exception("Unable to connect to VIS")
        # Scrap CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        return_input = soup.find('input', {'name': 'return'})
        csrf_token = return_input.find_next_sibling('input')['name']
        self.csrf_token = csrf_token
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
          'host': f'{self.host}',
          'Cookie': f'{list(cookies)[0]}={list(cookies.values())[0]}'
        }
        response = self.session.post(f'{self.vis_url}index.php', headers=headers, data=payload, allow_redirects=False)
        cookies: dict[str, str] = self.session.cookies.get_dict()
        self.cookies = cookies
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
          'host': f'{self.host}',
          'Cookie': f'{list(cookies)[0]}={list(cookies.values())[0]}; joomla_user_state=logged_in'
        }
        response = self.session.get(self.vis_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        login_greeting = soup.find(class_="login-greeting")
        if login_greeting is None:
            raise Exception("Unable to login to VIS")
        self.session.headers.update(headers)
        return login_greeting.text.replace("Hi ", "").replace(",", "").strip()
    
    def logout(self) -> bool:
        payload = f"""Submit=Log%20out&{self.csrf_token}=1&option=com_users&return=aHR0cHM6Ly92aXMudml0cm94LmNvbS5teS9hbnRpX2JyaWJlcnkvaW5kZXgucGhwL0FudGlfYnJpYmVyeS9pbmRleA%3D%3D&task=user.logout"""
        response = self.session.post(f"{self.vis_url}index.php", data=payload, allow_redirects=False)
        if response.status_code != 302:
            raise Exception("Unable to logout from VIS")
        self.cookies = None
        self.csrf_token = None
        return True

    @staticmethod
    def getUserList(db: Session, cookies: str, vis_url: str, ) -> str:
        cache_controller.remove_all_users(db=db)
        headers = {
            "Cookie": cookies,
            "host": urlparse(vis_url).netloc
        }
        response = requests.get(vis_url, headers=headers) 
        # Check if "Proceed to login" word in response.content
        content = response.text
        with open("test.html", "w", encoding='utf-8') as f:
            f.write(content)
        if "Please Login to proceed..." in content:
            raise Exception("Unable to login to VIS")
        return content
    
    @staticmethod
    def storeUserList(db: Session, content: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(content, 'html.parser')
        employee_data = soup.find('tbody').find_all('tr')
        employees = list()
        for employee in employee_data:
            name = employee.find('a').text
            # Extracting employee ID
            empl_id = employee.find_all('font')[1].text
            # Extracting employee department
            department = employee.find_all('font')[2].text
            # Extracting <db_id> from the href attribute using regex
            link = employee.find('a')['href']
            db_id = re.search(r'&jid=([^\']+)', link).group(1)
            cache_controller.add_user(db=db, name=name, db_id=db_id, empl_id=empl_id, department=department)
            employees.append({
                "name": name,
                "db_id": db_id,
                "empl_id": empl_id,
                "department": department
            })
        return employees
    
    @staticmethod
    def getUserDetails(userID: str, cookies: str, vis_url: str) -> str:
        headers = {
            "Cookie": cookies,
            "host": urlparse(vis_url).netloc
        }
        vis_url = f"{vis_url}&jid={userID}"
        response = requests.get(vis_url, headers=headers) 
        # Check if "Proceed to login" word in response.content
        content = response.text
        if "Please Login to proceed..." in content:
            raise Exception("Unable to login to VIS")
        soup = BeautifulSoup(content, 'html.parser')
        user_detail = VIS._user_table_to_dict(0, soup=soup)
        asset_table_details = VIS._table_to_dict(1, soup=soup)
        hardisk_table_details = VIS._harddisk_table_to_dict(2, soup=soup)
        accessory_table_details = VIS._accessory_table_to_dict(3, soup=soup)
        software_table_details = VIS._software_table_to_dict(4, soup=soup)
        user_detail["harddisk"] = hardisk_table_details
        user_detail["accessory"] = accessory_table_details
        user_detail["software"] = software_table_details
        user_detail["assets"] = asset_table_details
        return user_detail
        
    def searchUser(self, uername: str):
        pass
    
    @staticmethod
    def _user_table_to_dict(table_index, soup):
        user_table = soup.find_all('table')[table_index]
        user_detail = {}
        for row in user_table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) == 3:
                user_detail[columns[1].text.strip().replace(":", "")] = columns[2].text.strip()
            elif len(columns) == 2:
                user_detail[columns[0].text.strip().replace(":", "")] = columns[1].text.strip()
        return user_detail

    @staticmethod
    def _table_to_dict(table_index, soup):
        table = soup.find_all('table')[table_index]
        table_keys = []
        for row in table.find_all('tr'):
            columns = row.find_all("th")
            for column in columns:
                if column.text != "Acknowledge":
                    table_keys.append(column.text)
        table_details = []
        for row in (table.find_all('tr')):
            columns = row.find_all('td')
            if len(columns) > 1:
                table_detail = {
                    table_keys[0]: columns[0].text.strip(),
                    table_keys[1]: columns[1].text.strip(),
                    table_keys[2]: columns[2].text.strip(),
                    table_keys[3]: columns[3].text.strip(),
                    table_keys[4]: columns[4].find('input').get("value").strip(),
                    table_keys[5]: columns[5].find('input').get("value").strip() if len(columns) > 5 else "",
                    table_keys[6]: columns[6].find('input').get("value").strip() if len(columns) > 6 else "",
                    table_keys[7]: columns[7].find('input').get("value").strip() if len(columns) > 7 else "",
                    table_keys[8]: columns[8].find('input').get("value").strip() if len(columns) > 8 else "",
                }
                table_details.append(table_detail)
    
        json_string = json.dumps(table_details)
        return json_string
    
    @staticmethod
    def _harddisk_table_to_dict(table_index, soup):
        table = soup.find_all('table')[table_index]
        table_keys = []
        ignore_key = ["Acknowledge", "Hard Disk Information"]
        table_details = []
        for index, row in enumerate(table.find_all('tr')):
            if (index < 2):
                columns = row.find_all("td")
                for column in columns:
                    if column.text not in ignore_key:
                        table_keys.append(column.text)
            elif (index == 2):
                columns = row.find_all("th")
                for column in columns:
                    if column.text not in ignore_key:
                        table_keys.append(column.text)
            else:
                columns = row.find_all("td")
                table_detail = {
                    table_keys[0]: columns[0].text.strip(),
                    table_keys[1]: columns[1].text.strip(),
                    table_keys[2]: columns[2].find('input').get("value").strip() if len(columns) > 2 else "",
                    table_keys[3]: columns[3].find('input').get("value").strip() if len(columns) > 3 else "",
                    table_keys[4]: columns[4].find('input').get("value").strip() if len(columns) > 4 else "",
                    table_keys[5]: columns[5].find('input').get("value").strip() if len(columns) > 5 else "",
                    table_keys[6]: columns[6].find('input').get("value").strip() if len(columns) > 6 else "",
                }
                table_details.append(table_detail)
        json_string = json.dumps(table_details)
        return json_string
    
    @staticmethod
    def _accessory_table_to_dict(table_index, soup):
        table = soup.find_all('table')[table_index]
        table_keys = []
        ignore_key = ["Acknowledge", "Accessory Information"]
        table_details = []
        for index, row in enumerate(table.find_all('tr')):
            if (index < 2):
                columns = row.find_all("td")
                for column in columns:
                    if column.text not in ignore_key:
                        table_keys.append(column.text)
            elif (index == 2):
                columns = row.find_all("th")
                for column in columns:
                    if column.text not in ignore_key:
                        table_keys.append(column.text)
            else:
                columns = row.find_all("td")
                table_detail = {
                    table_keys[0]: columns[0].text.strip(),
                    table_keys[1]: columns[1].text.strip(),
                    table_keys[2]: columns[2].text.strip(),
                    table_keys[3]: columns[3].find('input').get("value").strip() if len(columns) > 3 else "",
                    table_keys[4]: columns[4].find('input').get("value").strip() if len(columns) > 4 else "",
                    table_keys[5]: columns[5].find('input').get("value").strip() if len(columns) > 5 else "",
                    table_keys[6]: columns[6].find('input').get("value").strip() if len(columns) > 6 else "",
                    table_keys[7]: columns[7].find('input').get("value").strip() if len(columns) > 7 else "",
                    table_keys[8]: columns[8].find('input').get("value").strip() if len(columns) > 8 else "",
                }
                table_details.append(table_detail)
        json_string = json.dumps(table_details)
        return json_string
    
    @staticmethod
    def _software_table_to_dict(table_index, soup):
        table = soup.find_all('table')[table_index]
        table_keys = []
        ignore_key = ["Acknowledge", "Software Information"]
        table_details = []
        for index, row in enumerate(table.find_all('tr')):
            if (index < 2):
                columns = row.find_all("th")
                for column in columns:
                    if column.text not in ignore_key:
                        table_keys.append(column.text)
            elif (index == 2):
                columns = row.find_all("th")
                for column in columns:
                    if column.text not in ignore_key:
                        table_keys.append(column.text)
            else:
                columns = row.find_all("td")
                table_detail = {
                    table_keys[0]: columns[0].text.strip(),
                    table_keys[1]: columns[1].text.strip(),
                    table_keys[2]: columns[2].text.strip(),
                    table_keys[3]: columns[3].find('input').get("value").strip() if len(columns) > 3 else "",
                    table_keys[4]: columns[4].find('input').get("value").strip() if len(columns) > 4 else "",
                    table_keys[5]: columns[5].find('input').get("value").strip() if len(columns) > 5 else "",
                    table_keys[6]: columns[6].find('input').get("value").strip() if len(columns) > 6 else "",
                    table_keys[7]: columns[7].find('input').get("value").strip() if len(columns) > 7 else "",
                }
                table_details.append(table_detail)
        json_string = json.dumps(table_details)
        return json_string

    def _get_user_detail(self, username: str):
        file_path = "./static/user_list/" + username + ".htm"
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        return self._user_table_to_dict(0, soup)
