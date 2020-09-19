import argparse
import time
import os
from urllib import request
import pandas as pd
import requests
from bs4 import BeautifulSoup

path = "~/Downloads"
download_path = os.path.expanduser(path)
domain_link = 'https://finance.yahoo.com'
query_link = 'https://query1.finance.yahoo.com/v7/finance/download/'
column = 'Close'
new_column = '3day_before_change'
date = '3 day'


class Yagrab:
    def __init__(self, co):
        self.co = co
        self.history_url = ''
        self.file_path = ''
        self.file_csv = None

    def get_url(self):
        per1 = 0
        today = int(time.time())
        self.history_url = query_link + f'{self.co}?period1={per1}&period2=' \
                                        f'{today}&interval=1d&events=history'
        return self.history_url

    def get_path(self):
        self.file_path = os.path.join(download_path, f'{self.co}.csv')
        return self.file_path

    def save_data(self):
        request.urlretrieve(self.get_url(), self.get_path())

    def io_csv(self):
        self.file_csv = pd.read_csv(self.get_path())
        self.handling_data()
        self.file_csv.to_csv(self.get_path(), index=False)

    def handling_data(self):
        self.file_csv = self.file_csv.sort_values('Date', ascending=False)
        self.file_csv['Date'] = pd.to_datetime(self.file_csv['Date'])
        self.file_csv[new_column] = ""
        date_pd = pd.to_timedelta(date)
        for i, row in self.file_csv.iterrows():
            new_date = pd.to_datetime(row['Date']) - date_pd
            column_div = self.file_csv.loc[self.file_csv['Date'] ==
                                           new_date, column].values.tolist()
            if not column_div:
                self.file_csv.loc[i, new_column] = '-'
            else:
                ratio = (row.loc[column])/column_div[0]
                self.file_csv.loc[i, new_column] = ratio


class Yascrape:
    def __init__(self, co):
        self.co = co
        self.news_url = ''
        self.file_path = ''
        self.list_link_text = []

    def get_url(self):
        self.news_url = domain_link + f'/quote/{self.co}?p={self.co}'
        return self.news_url

    def get_path(self):
        self.file_path = os.path.join(download_path, f'{self.co}_news.csv')
        return self.file_path

    def parser(self):
        contents = requests.get(self.get_url())
        soup = BeautifulSoup(contents.text, "html.parser")
        list_result = soup.find_all('li', class_="js-stream-content Pos(r)")
        #print(li_list)
        for result in list_result:
            h_link = domain_link + result.find('a').get('href')
            h_text = result.find('a').get_text()
            self.list_link_text.append((h_link, h_text))
        #print(self.list_link_text)
        return self.list_link_text

    def save_csv(self):
        df = pd.DataFrame(self.list_link_text, columns=['link', 'title'])
        #print(df)
        df.to_csv(self.get_path(), index=False)


def main(companies):
    for company in companies:
        data = Yagrab(company)
        data.save_data()
        data.io_csv()
        news = Yascrape(company)
        news.parser()
        news.save_csv()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Test Yahoo scraper")
    parser.add_argument('companies', nargs='+', type=str, help='Company names')
    args = parser.parse_args()
    #print(args.companies)
    main(args.companies)