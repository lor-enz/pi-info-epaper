import base64
import email
import random
import smtplib
import time
import datetime
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
    CSV_URL = 'https://raw.githubusercontent.com/ard-data/2020-rki-impf-archive/master/data/9_csv_v2/region_BY.csv'

    def __str__(self):
        return f"website: {self.website} \nnumber: {self.some_number}"

    def __init__(self):
        self.download_data()

    def download_data(self):
        with requests.Session() as s:
            download = s.get(self.CSV_URL)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            self.all_rows = list(cr)
            return self.all_rows

    def get_current_abs_doses(self):
        i = 1
        last_row = []
        while len(last_row) < 4:
            last_row = self.all_rows[len(self.all_rows)-i]
            i = i+1
        vaccinated_abs = int(last_row[2])
        date = last_row[0]
        return {
            "date": date,
            "vaccinated_abs": vaccinated_abs,
        }

    def get_extrapolated_abs_doses(self):
        current_info = self.get_current_abs_doses()
        # current_info["vaccinated_abs"]

        info_unix = int(time.mktime(datetime.datetime.strptime(
            current_info["date"], "%Y-%m-%d").timetuple()))

        current_time = int(time.time())
        time_difference = current_time - info_unix
        print(
            f"time_difference {time_difference} current_time {current_time} info_unix {info_unix}")
        return time_difference

    def print_all(self):
        for row in self.all_rows:
            print(row)
