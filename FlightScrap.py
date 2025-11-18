import requests
from bs4 import BeautifulSoup

url = "https://finance.yahoo.com/quote/AMZN"

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}

session = requests.Session()
session.headers.update(headers)

response = session.get(url, headers=headers)
response.raise_for_status()


soup = BeautifulSoup(response.content, "html.parser")

file = open("flight.csv", "w")
print(response.content)
table1 = soup.find('div', {'data-testid': 'quote-statistics', 'class': 'container yf-tx3nkj'})
table1 = soup.find('div', {'data-testid': 'quote-statistics'})
storer1 = table1.find("ul")
entry_list1 = storer1.find_all("li")

for entry in entry_list1:
    label = entry.find('span', {'class': 'label yf-tx3nkj'}).get_text(strip=True)
    value = entry.find('span', {'class': 'value yf-tx3nkj'}).get_text(strip=True)
    print(label)
    print(value)

table2 = soup.find('div', {'class': 'container yf-1n4vnw8'})
storer2 = table2.find('ul')
entry_list2 = storer2.find_all("li")
for entry in entry_list2:
    label = entry.find('p', {'class': 'label yf-1n4vnw8'}).get_text(strip=True)
    value = entry.find('p', {'class': 'value yf-1n4vnw8'}).get_text(strip=True)
    print(label)
    print(value)

table3 = soup.find('section', {'class': 'card large yf-13ievhf bdr sticky', 'data-testid': 'financial-highlights'})
total_part = table3.find_all('div', {'class': 'highlights yf-lc8fp0'})

for part in total_part:
    storer3 = part.find('ul')
    entry_list3 = storer3.find_all("li")

    for entry in entry_list3:
        label = entry.find('p', {'class': 'label'}).get_text(strip=True)
        print(label)
        value = entry.find('p', {'class': 'value yf-lc8fp0'}).get_text(strip=True)
        print(value)


url2 = "https://github.com/datasets/nasdaq-listings/blob/master/data/nasdaq-listed.csv"
session = requests.Session()
session.headers.update(headers)

response = session.get(url, headers=headers)

soup2 = BeautifulSoup(response.content, "html.parser")

tbody = soup.find("tbody")
entryList = tbody.find_all("tr", {'class': 'react-csv-row'})
tickers = []
for entry in entryList:
    ticker = entry.find('td', {'class': 'react-csv-cell'}).get_text(strip=True)
    #put into an array
    tickers.append(ticker)
file.close()
