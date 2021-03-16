import base64
import email
import random
import smtplib
import time
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


class Databook():

    storage = {
        'last_download_vacc': 0,
        'last_download_infe': 0,
        'bay_vac':-1,
        'muc_inz':-1,
        'bay_inz':-1,
    }

    def __init__(self):
        self.load_pickle()
        self.load_dataframes()

    def load_pickle(self):
        if (os.path.isfile(PICKLE_FILE)):
            with open(PICKLE_FILE, 'br') as f:
                self.storage = pickle.load(f)
        logging.info(
            f"Loaded Pickle... {self.print_storage()}")

    def save_pickle(self):
        logging.info(
            f"Saving Pickle...")

        with open(PICKLE_FILE, 'bw') as f:
            pickle.dump(self.storage, f)
        logging.info(
            f"Saved Pickle!")

    def print_storage(self):
        s1 = f'last_download_vacc: {self.storage["last_download_vacc"]}  last_download_infe: {self.storage["last_download_infe"]}  '
        s2 = f'bay_vac: {self.storage["bay_vac"]}  muc_inz: {self.storage["muc_inz"]}  bay_inz: {self.storage["bay_inz"]}'
        return s1 + s2


    def is_fresh_data_needed(self, what):
        is_needed = False
        reason = "Unknown reason"
        filename = what[1]
        keyname = what[2]
    
        oldness = ((time.time() - self.storage[keyname]) / 60)
        now = datetime.datetime.now()
        is_working_hours = now.hour >= 7 and now.hour <= 18
        
        if (is_working_hours and oldness > OLDNESS_THRESHOLD):
            is_needed = True
        elif is_working_hours:
            reason = f'Data is still fresh. Oldness: {"{:.1f}".format(oldness/60/60)} hours'
        else:
            reason = "Outside working hours right now."

        if not os.path.isfile(filename):
            is_needed = True
            reason = "No local data"

        if is_needed:
            logging.info(f"New {keyname} data is needed. Reason {reason}")
        else:
            logging.info(f"Download of {keyname} can be skipped. Reason {reason}")
        return is_needed

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
        changed =  not (self.storage["bay_inz"] == inz)
        #print(f'stored {self.storage["bay_inz"]}  ==  {inz} new_value -> {not changed}')
        self.storage["bay_inz"] = inz
        self.save_pickle()
        return (inz, changed)

    def get_inz_munich(self):
        the_one_row = self.df_infe[self.df_infe['county'] == 'SK München']
        inz = the_one_row['cases7_per_100k']
        inz = "{:.1f}".format(inz.values[0])
        # store it!
        changed =  not (self.storage["muc_inz"] == inz)
        #print(f'stored {self.storage["muc_inz"]}  ==  {inz} new_value -> {not changed}')
        self.storage["muc_inz"] = inz
        self.save_pickle()
        return (inz, changed)

    def get_official_abs_doses(self):
        new_value = self.df_vacc.tail(1)['dosen_kumulativ'].values[0]
        return new_value

    def get_data_date(self):
        # Remove this? Unused?
        return self.df_vacc.tail(1).index.values[0]

    def get_extrapolated_abs_doses(self):
        official_doses = self.get_official_abs_doses()
        # current_info["vaccinated_abs"]
        official_doses_timestamp = self.storage['last_download_vacc']

        current_time = int(time.time())
        time_difference_secs = current_time - official_doses_timestamp
        logging.info(
            f"current_time {current_time} MINUS official_doses_timestamp {official_doses_timestamp} EQUALS time_difference_secs {time_difference_secs} ")

        mean = self.get_average_daily_vaccs_of_last_days(LOOK_BACK_FOR_MEAN)
        todays_vaccs = self.extrapolate(mean, time_difference_secs)
        total_vaccs = official_doses + todays_vaccs
        total_vaccs = '{:,}'.format(total_vaccs).replace(',', '.')
        logging.info(f"""Using mean {mean} of last {LOOK_BACK_FOR_MEAN} days
        to calculate todays newest vaccs estimate based on {time_difference_secs} seconds (or {"{:.1f}".format((time_difference_secs / 60 / 60))} hours)
        since 8am. Resulting in todays vaccs til now being {todays_vaccs}
        Adding that to offical vaccs of {official_doses}
        results in total vaccs of {total_vaccs}""")
        # store it!
        changed =  not (self.storage["bay_vac"] == total_vaccs)
        print(f'stored {self.storage["bay_vac"]}  ==  {total_vaccs} new_value -> {not changed}')
        self.storage["bay_vac"] = total_vaccs
        self.save_pickle()
        return (total_vaccs, changed)

    def extrapolate(self, daily_mean, seconds):
        seconds = min(seconds, DAILY_VACC_TIME_IN_SECS)
        progress = (seconds/DAILY_VACC_TIME_IN_SECS)
        todays_vaccs = int(daily_mean * progress)
        return todays_vaccs

    def get_average_daily_vaccs_of_last_days(self, days_to_look_back):
        mean = self.df_vacc.tail(days_to_look_back)[
            'dosen_kumulativ_differenz_zum_vortag'].values.mean()
        return int(mean)


#databook = Databook()
#print(f"get_official_abs_doses   {databook.get_official_abs_doses()}")
#print(f"inz_munich   {databook.get_inz_munich()}")
