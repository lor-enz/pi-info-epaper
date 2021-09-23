import os
import logging
import csv
import requests
from bs4 import BeautifulSoup

import mytime as mytime

AMPEL_SCRAPE = {
    'url': 'https://datawrapper.dwcdn.net/2L501/13/',
    'file': 'ampel.json',
    'key': 'ampel_download_timestamp'
}

class Scraper:

    def __init__(self):
        self.ampel_download_timestamp = 0
        # We're not doing storage here.

    def __str__(self):
        return f'vac.csv downloaded at: {self.ampel_download_timestamp}  '

    def download(self):
        import bs4 as bs
        import urllib.request
        page = page = requests.get('https://datawrapper.dwcdn.net/2L501/13/')
        #source = urllib.request.urlopen(AMPEL_SCRAPE['url']).read()
        soup = BeautifulSoup(page.text, 'html.parser')
        print(f'Title is {soup.title}')
        list = soup.children()

        for thing in list:
            print(f'Thing {thing}')

        self.ampel_download_timestamp = mytime.current_time()