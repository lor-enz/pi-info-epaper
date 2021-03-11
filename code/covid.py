import base64
import email
import random
import smtplib
import time
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from socket import gaierror

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select

import csv
import requests

class Checker():
    CSV_URL = 'https://raw.githubusercontent.com/ard-data/2020-rki-impf-archive/master/data/2_csv/region_BY.csv'

    def __str__(self):
        return f"website: {self.website} \nnumber: {self.some_number}"

    def __init__(self):
        self.website = "something"
        self.some_number = 42
        self.get_data()

    def get_data(self):
        with requests.Session() as s:
            download = s.get(self.CSV_URL)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            self.all_rows = list(cr)
            return self.all_rows
            
    def get_abs_vaccinated(self):   
        vaccinated_abs = int(self.all_rows[len(self.all_rows)-1][2])
        return vaccinated_abs

    def print_all(self):
        for row in self.all_rows:
                print(row)

checker = Checker()
checker.get_abs_vaccinated()
