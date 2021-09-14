# import requests
# from bs4 import BeautifulSoup
#
# URL = 'https://primepress.by/news/kompanii/roznichnye_tseny_na_toplivo_v_belarusi_na_3_avgusta_2021_g-36087/'
# page_text = requests.get(URL).text
# soup = BeautifulSoup(page_text, 'html.parser')
# link = soup.findAll('p', {'align': 'center'})
# result = link[19].text.strip()
# diesel = float(result.replace(',', '.'))
