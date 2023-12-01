from bs4 import BeautifulSoup
import requests

response = requests.get("http://127.0.0.1:8080/static/user_list/chan_jin_yee.htm")
soup = BeautifulSoup(response.content, 'html.parser')
td_tags = soup.find_all("td")

for tag in td_tags:
    for child in tag.children:
        print(child)

    # if div_exists:
    #     for child in tag.children:
    #         print(child.string)
    # else:
    #     print("div tag does not exist directloy inside body tag")