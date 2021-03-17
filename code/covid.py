import base64
import email
import random
import smtplib
import time
from datetime import datetime as dt
import datetime
import sys
import os
import logging
from io import BytesIO
from socket import gaierror

import csv
import requests
import numpy as np
import pandas as pd
import pickle

logging.basicConfig(level=logging.INFO)

# url, filename, keyname
CSV_URL_VACC = (
    'https://raw.githubusercontent.com/ard-data/2020-rki-impf-archive/master/data/9_csv_v2/region_BY.csv', 'vacc.csv', 'last_download_vacc')
CSV_URL_INFE = (
    "https://opendata.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0.csv", 'infe.csv', 'last_download_infe')


DAILY_VACC_TIME_IN_SECS = 36000  # 36000 = 10 hours
LOOK_BACK_FOR_MEAN = 3
OLDNESS_THRESHOLD = 3600 * 10  # 3600 = 1 hour
PICKLE_FILE = 'storage.p'


def is_business_hours(self):
    now = datetime.datetime.now()
    if (now.hour == 18 and now.minute == 00):
        return True
    return now.hour >= 7 and now.hour <= 18


class Databook():

    storage = {
        'last_download_vacc': 0,
        'last_download_infe': 0,
        'bay_vac': -1,
        'muc_inz': -1,
        'bay_inz': -1,
    }

    def __init__(self):
        self.load_pickle()
        self.load_dataframes()

    def load_pickle(self):
        if (os.path.isfile(PICKLE_FILE)):
            with open(PICKLE_FILE, 'br') as f:
                self.storage = pickle.load(f)
        logging.info(
            f"LOAD Pickle... {self.print_storage()}")

    def save_pickle(self):
        with open(PICKLE_FILE, 'bw') as f:
            pickle.dump(self.storage, f)
        logging.info(
            f"SAVE Pickle!   {self.print_storage()}")

    def print_storage(self):
        s1 = f'last_download_vacc: {self.storage["last_download_vacc"]}  last_download_infe: {self.storage["last_download_infe"]}  '
        s2 = f'bay_vac: {self.storage["bay_vac"]}  muc_inz: {self.storage["muc_inz"]}  bay_inz: {self.storage["bay_inz"]}'
        return s1 + s2

    def is_business_hours(self):
        now = dt.now()
        if (now.hour == 18 and now.minute == 00):
            return True
        return now.hour >= 7 and now.hour <= 18

    def is_fresh_data_needed(self, what):
        is_needed = False
        reason = "Unknown reason"
        filename = what[1]
        keyname = what[2]

        oldness = ((time.time() - self.storage[keyname]) / 60)

        is_business_hours = self.is_business_hours()

        if (is_business_hours and oldness > OLDNESS_THRESHOLD):
            is_needed = True
        elif is_business_hours:
            reason = f'Data is still fresh. Oldness: {"{:.1f}".format(oldness/60/60)} hours'
        else:
            reason = "Outside working hours right now."

        if not os.path.isfile(filename):
            is_needed = True
            reason = "No local data"

        if is_needed:
            logging.info(f"New {keyname} data is needed. Reason {reason}")
        else:
            logging.info(
                f"Download of {keyname} can be skipped. Reason {reason}")
        return is_needed

    def maybe_download_data(self, what):
        if self.is_fresh_data_needed(what):
            self.download_data(what)
            logging.info(f"Downloaded new version of {what[1]}")

    def download_data(self, what):
        keyname = what[2]
        response = requests.get(what[0])
        filename = what[1]

        with open(filename, 'w') as f:
            writer = csv.writer(f)
            for line in response.iter_lines():
                writer.writerow(line.decode('utf-8').split(','))
        if (filename == 'vacc.csv'):
            df = pd.read_csv(filename, sep=',',
                             index_col=0, parse_dates=True)
            last_update = ((df.tail(1).index.astype(
                np.int64) // 10**9)).tolist()[0] + 60*60*(24+8)
            self.storage[keyname] = last_update
            self.save_pickle()
        elif (filename == 'infe.csv'):
            last_update = self.get_infe_last_update_timestamp(
                filename)
            self.storage[keyname] = last_update
            self.save_pickle()
        else:
            logging.error(
                f"Unknown filename! Expected vacc.csv or infe.csv. Got {filename}")

    def get_infe_last_update_timestamp(self, filename):
        # TODO this should be done better, and with pandas not with csv, but pandas was being difficult...
        rows = []
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                rows.append(row)
        date_string = rows[-1][34][3:13]
        date_time_obj = datetime.datetime.strptime(
            date_string, '%d.%m.%Y')

        timestamp = int(date_time_obj.replace(
            tzinfo=datetime.timezone.utc).timestamp())
        return timestamp

    def load_dataframes(self):
        self.maybe_download_data(CSV_URL_VACC)
        self.maybe_download_data(CSV_URL_INFE)
        self.load_vacc_dataframe()
        self.load_infe_dataframe()

    def fix_comma_in_csv(self, filename):
        fin = open(filename, "rt")
        data = fin.read()
        data = data.replace(',\" 00:00 Uhr', ' 00:00 Uhr')
        data = data.replace('","', '.')
        fin.close()
        fin = open(filename, "wt")
        fin.write(data)
        fin.close()

    def load_infe_dataframe(self):
        # INFE
        csv = CSV_URL_INFE[1]
        self.fix_comma_in_csv(csv)
        df = pd.read_csv(csv, sep=',', index_col=0)
        self.df_infe = df

    def load_vacc_dataframe(self):
        # VACC
        csv = CSV_URL_VACC[1]
        df = pd.read_csv(
            csv, sep=',', index_col=0, parse_dates=True)
        df = df[['dosen_kumulativ', 'impf_inzidenz_dosen']]
        df['dosen_kumulativ_differenz_zum_vortag'] = df.dosen_kumulativ - \
            df.dosen_kumulativ.shift(1)

        df['dosen_kumulativ_differenz_zum_vortag'] = df['dosen_kumulativ_differenz_zum_vortag'].fillna(
            0)
        df = df.astype({'dosen_kumulativ_differenz_zum_vortag': 'int64'})
        self.df_vacc = df

    def get_inz_bavaria(self):
        the_one_row = self.df_infe[self.df_infe['county'] == 'SK München']
        inz = the_one_row['cases7_bl_per_100k']
        inz = "{:.1f}".format(inz.values[0])
        # store it!
        changed = not (self.storage["bay_inz"] == inz)
        #print(f'stored {self.storage["bay_inz"]}  ==  {inz} new_value -> {not changed}')
        self.storage["bay_inz"] = inz
        self.save_pickle()
        return (inz, changed)

    def get_inz_munich(self):
        the_one_row = self.df_infe[self.df_infe['county'] == 'SK München']
        inz = the_one_row['cases7_per_100k']
        inz = "{:.1f}".format(inz.values[0])
        # store it!
        changed = not (self.storage["muc_inz"] == inz)
        #print(f'stored {self.storage["muc_inz"]}  ==  {inz} new_value -> {not changed}')
        self.storage["muc_inz"] = inz
        self.save_pickle()
        return (inz, changed)

    def get_official_abs_doses(self):
        new_value = self.df_vacc.tail(1)['dosen_kumulativ'].values[0]
        return new_value

    def get_extrapolated_abs_doses(self):
        official_doses = self.get_official_abs_doses()
        official_doses_timestamp = self.storage['last_download_vacc']

        time_difference_secs = self.business_time_since(
            unix_time1=official_doses_timestamp)

        mean = self.get_average_daily_vaccs_of_last_days(LOOK_BACK_FOR_MEAN)
        extra_vacs = self.extrapolate(mean, time_difference_secs)
        total_vaccs = official_doses + extra_vacs
        total_vaccs = '{:,}'.format(total_vaccs).replace(',', '.')
        logging.info(f"""Using mean {mean} of last {LOOK_BACK_FOR_MEAN} days
        to calculate extra vacs estimate based on {time_difference_secs} seconds (or {"{:.1f}".format((time_difference_secs / 60 / 60))} hours)
        since 8am. Resulting in extra vacs til now being {extra_vacs}
        Adding that to offical vaccs of {official_doses}
        results in total vaccs of {total_vaccs}""")
        # store it!
        changed = not (self.storage["bay_vac"] == total_vaccs)
        #print(f'stored {self.storage["bay_vac"]}  ==  {total_vaccs} new_value -> {not changed}')
        self.storage["bay_vac"] = total_vaccs
        self.save_pickle()
        return (total_vaccs, changed)

    def extrapolate(self, daily_mean, seconds):
        progress = (seconds/DAILY_VACC_TIME_IN_SECS)
        extra_vacs = int(daily_mean * progress)
        return extra_vacs

    def business_time_since(self, unix_time1, unix_time2=0):
        if unix_time2 < 1:
            unix_time2 = dt.timestamp(dt.now())
        
        dt_a = dt.fromtimestamp(unix_time1)
        dt_b = dt.fromtimestamp(unix_time2)

        dif = unix_time2 - unix_time1
        nb_full_days = int(dif / (60*60*24))
        partial_day = min(int(dif % (60*60*24)), 36000)

        result = (10*60*60) * nb_full_days + partial_day
        delta = datetime.timedelta(seconds=result)
        logging.info(f"Input time from {dt_a}  to  {dt_b}")
        logging.info(
            f"  -> full days: {nb_full_days} + seconds of remaning day {partial_day} = {result} secs or {delta}")
        return result

    def get_average_daily_vaccs_of_last_days(self, days_to_look_back):
        mean = self.df_vacc.tail(days_to_look_back)[
            'dosen_kumulativ_differenz_zum_vortag'].values.mean()
        return int(mean)
