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
import numpy as np


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
        hm = current_info["date"]
        print(f"newest data date {hm}")
        info_unix = int(time.mktime(datetime.datetime.strptime(
            current_info["date"], "%Y-%m-%d").timetuple()))
        # info_unix is 0:00 of that day, but the data shows the vaccs at the END of that day.
        # So add 24 hours to it. and then also 8 hours until it's 8am
        info_unix = info_unix + 60*60*24 + 60*60*8

        current_time = int(time.time())
        time_difference_secs = current_time - info_unix
        print(
            f"time_difference_secs {time_difference_secs} current_time {current_time} info_unix {info_unix}")
        # Let's say vaccinations happen from 8:00 to 18:00 Uhr so 10 hours or 36000 secs
        daily_vacc_time_in_secs = 36000

        time_difference_secs = max(time_difference_secs,
                                   daily_vacc_time_in_secs)
        mean = self.get_average_daily_vaccs_of_last_days(7)
        todays_vaccs = int(
            mean * (time_difference_secs/daily_vacc_time_in_secs))
        total_vaccs = int(current_info["vaccinated_abs"]) + todays_vaccs
        return total_vaccs

    def get_average_daily_vaccs_of_last_days(self, days_to_look_back):
        daylies = []
        previous = 0
        skip = True
        for row in self.all_rows:
            if skip:
                skip = False
                continue
            daylies.append(int(row[2])-previous)
            previous = int(row[2])
        daylies = daylies[-days_to_look_back:]
        mean = int(np.mean(daylies))
        print(f"Mean of last {days_to_look_back} days is: {mean}")
        return mean

    def print_all(self):
        for row in self.all_rows:
            print(row)
