import requests
from bs4 import BeautifulSoup

URL = 'https://azs.belorusneft.by/sitebeloil/ru/center/azs/center/fuelandService/price/'
page_text = requests.get(URL).text
soup = BeautifulSoup(page_text, 'html.parser')
link = soup.findAll('td', {'class': 'col2'})
petrol = float(link[1].text.strip())
diesel = float(link[4].text.strip())
