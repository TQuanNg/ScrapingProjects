import requests
import csv
import time
import pandas as pd
from bs4 import BeautifulSoup


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}

tickers = []
def scrape_ticker():

    file_path = 'C:/Users/user/Downloads/nasdaq-listed.csv' ###
    df = pd.read_csv(file_path)

    # Loop through the DataFrame and extract the Symbol column
    entryList = df['Symbol']
    for entry in entryList:
        #put into an array
        tickers.append(entry)

scrape_ticker()
with open("financial_data.csv", mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Ticker", "Label", "Value"])

    for ticker in tickers:
        time.sleep(2)
        url = "https://finance.yahoo.com/quote/" + ticker + "/"
        session = requests.Session()
        session.headers.update(headers)
        response = session.get(url, headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(errh.args[0])

        soup = BeautifulSoup(response.content, "html.parser")

        table1 = soup.find('div', {'data-testid': 'quote-statistics', 'class': 'container yf-tx3nkj'})
        if table1 is None:
            print(f"Table 1 not found for ticker: {ticker}")
            continue
        storer1 = table1.find("ul")
        entry_list1 = storer1.find_all("li")

        for entry in entry_list1:
            label = entry.find('span', {'class': 'label yf-tx3nkj'}).get_text(strip=True)
            value = entry.find('span', {'class': 'value yf-tx3nkj'}).get_text(strip=True)
            writer.writerow([ticker, label, value])

        table2 = soup.find('div', {'class': 'container yf-1n4vnw8'})
        if table2 is None:
            print(f"Table 2 not found for ticker: {ticker}")
            continue
        storer2 = table2.find('ul')
        entry_list2 = storer2.find_all("li")
        for entry in entry_list2:
            label = entry.find('p', {'class': 'label yf-1n4vnw8'}).get_text(strip=True)
            value = entry.find('p', {'class': 'value yf-1n4vnw8'}).get_text(strip=True)
            writer.writerow([ticker, label, value])

        table3 = soup.find('section', {'class': 'card large yf-13ievhf bdr sticky', 'data-testid': 'financial-highlights'})
        if table3 is None:
            print(f"Table 3 not found for ticker: {ticker}")
            continue
        total_part = table3.find_all('div', {'class': 'highlights yf-lc8fp0'})

        for part in total_part:
            storer3 = part.find('ul')
            entry_list3 = storer3.find_all("li")

            for entry in entry_list3:
                label = entry.find('p', {'class': 'label'}).get_text(strip=True)
                value = entry.find('p', {'class': 'value yf-lc8fp0'}).get_text(strip=True)
                writer.writerow([ticker, label, value])

        print("Found " + ticker)

