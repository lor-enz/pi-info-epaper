
import os
import logging
import csv
import numpy as np
import pandas as pd

import mytime as mytime
import fetcher as fet

LOOK_BACK_FOR_MEAN = 3
OLDNESS_THRESHOLD_LARGE = 3600 * 36  # 3600 = 1 hour
OLDNESS_THRESHOLD_SMALL = 3600 * 10  # 3600 = 1 hour

STORAGE_FILE = 'databook-storage.json'


def is_fresh_data_needed(freshness_timestamp, filename):
    is_needed = False
    current_time = mytime.current_time()
    # print(f"current_time {current_time} freshness_timestamp {freshness_timestamp}")
    oldness = (current_time - freshness_timestamp)

    if mytime.is_business_hours() and oldness > OLDNESS_THRESHOLD_SMALL:
        is_needed = True
        reason = f"Old files and during business hours. Oldness: {mytime.seconds2delta(oldness)} Small Threshold: {mytime.seconds2delta(OLDNESS_THRESHOLD_SMALL)}"
    elif mytime.is_business_hours():
        reason = f'Data is still fresh. Oldness: {mytime.seconds2delta(oldness)}'
    elif oldness > OLDNESS_THRESHOLD_LARGE:
        is_needed = True
        reason = f"Very old files. Oldness: {mytime.seconds2delta(oldness)} Large Threshold: {mytime.seconds2delta(OLDNESS_THRESHOLD_LARGE)}"
    else:
        reason = f"Outside working hours right now and data not that old. Oldness: {mytime.seconds2delta(oldness)}"

    if not os.path.isfile(filename):
        is_needed = True
        reason = "No local data"

    if is_needed:
        logging.info(f"New {filename} data is needed. Reason {reason}")
    else:
        logging.info(
            f"Download of {filename} can be skipped. Reason {reason}")
    return is_needed


class Databook:

    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        self.inf_freshness_timestamp = 0
        self.vac_freshness_timestamp = 0
        self.dl_attempt_timestamp = 0
        self.bay_vac = -1
        self.muc_inz = -1
        self.bay_inz = -1
        self.load_storage()
        self.maybe_download_data()
        self.inf_freshness_timestamp = self.get_inf_last_update_timestamp()
        self.vac_freshness_timestamp = self.get_vac_last_update_timestamp()
        self.save_storage()
        self.inf_df = self.load_inf_dataframe()
        self.vac_df = self.load_vac_dataframe()

    def load_storage(self):
        if not os.path.isfile(STORAGE_FILE):
            logging.info(f'{STORAGE_FILE} does not exist (yet)')
            return  # no file?
        from storage import retrieve
        storage = retrieve(STORAGE_FILE)
        self.inf_freshness_timestamp = storage['inf_freshness_timestamp']
        self.vac_freshness_timestamp = storage['vac_freshness_timestamp']
        self.bay_vac = storage['bay_vac']
        self.bay_inz = storage['bay_inz']
        self.muc_inz = storage['muc_inz']

        logging.info(f'Loaded {STORAGE_FILE}')

    def save_storage(self):
        storage = {
            'inf_freshness_timestamp': int(self.inf_freshness_timestamp),
            'vac_freshness_timestamp': int(self.vac_freshness_timestamp),
            'last_dl_attempt': int(self.dl_attempt_timestamp),
            'bay_vac': self.bay_vac,
            'bay_inz': self.bay_inz,
            'muc_inz': self.muc_inz
        }
        from storage import store
        store(STORAGE_FILE, storage)

    def is_fresh_inf_data_needed(self):
        return is_fresh_data_needed(self.inf_freshness_timestamp, fet.CSV_INF['file'])

    def is_fresh_vac_data_needed(self):
        return is_fresh_data_needed(self.vac_freshness_timestamp, fet.CSV_VAC['file'])

    def maybe_download_data(self):
        seconds_since_last_attempt = mytime.current_time() - self.dl_attempt_timestamp
        if seconds_since_last_attempt < 60 * 19:
            logging.info(
                f'Not attempting another download. Last one was {mytime.seconds2delta(seconds_since_last_attempt)} ago')
            return

        fetcher = fet.Fetcher()
        if self.is_fresh_inf_data_needed():
            fetcher.download_data(fet.CSV_INF)
            logging.info(f"Downloaded new version of {fet.CSV_INF['file']}")
        if self.is_fresh_vac_data_needed():
            fetcher.download_data(fet.CSV_VAC)
            logging.info(f"Downloaded new version of {fet.CSV_VAC['file']}")
        self.dl_attempt_timestamp = mytime.current_time()
        fetcher.save_storage()  # TODO can we remove this because it's already saved in fetcher.download_data()... ?

    def get_inf_last_update_timestamp(self):
        # TODO this should be done better, and with pandas not with csv, but pandas was being difficult...
        rows = []
        with open(fet.CSV_INF['file'], newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                rows.append(row)
        date_string = rows[-1][34]

        freshness_timestamp = mytime.dt2ts(time_string=date_string, time_format="%d.%m.%Y_%H:%M Uhr")
        return freshness_timestamp

    def get_vac_last_update_timestamp(self):
        df = pd.read_csv(fet.CSV_VAC['file'], sep=',',
                         index_col=0, parse_dates=True)
        last_update = ((df.tail(1).index.astype(
            np.int64) // 10 ** 9)).tolist()[0] + 60 * 60 * (24 + 7)
        return last_update

    def load_inf_dataframe(self):
        # INFE
        csv_path = fet.CSV_INF['file']
        df = pd.read_csv(csv_path, sep=',', index_col=0)
        return df

    def load_vac_dataframe(self):
        # VACC
        csv_path = fet.CSV_VAC['file']
        df = pd.read_csv(
            csv_path, sep=',', index_col=0, parse_dates=True)
        df = df[['dosen_kumulativ', 'impf_inzidenz_dosen']]
        df['dosen_kumulativ_differenz_zum_vortag'] = df.dosen_kumulativ - \
                                                     df.dosen_kumulativ.shift(1)

        df['dosen_kumulativ_differenz_zum_vortag'] = df['dosen_kumulativ_differenz_zum_vortag'].fillna(
            0)
        df = df.astype({'dosen_kumulativ_differenz_zum_vortag': 'int64'})
        return df

    def get_inz_bavaria(self):
        the_one_row = self.inf_df[self.inf_df['county'] == 'SK München']
        inz = the_one_row['cases7_bl_per_100k']
        inz = "{:.1f}".format(inz.values[0])
        # store it!
        changed = not self.bay_inz == inz
        self.bay_inz = inz
        self.save_storage()
        return inz, changed

    def get_inz_munich(self):
        the_one_row = self.inf_df[self.inf_df['county'] == 'SK München']
        inz = the_one_row['cases7_per_100k']
        inz = "{:.1f}".format(inz.values[0])
        # store it!
        changed = not self.muc_inz == inz
        # print(f'stored {self.storage["muc_inz"]}  ==  {inz} new_value -> {not changed}')
        self.muc_inz = inz
        self.save_storage()
        return inz, changed

    def get_official_abs_doses(self):
        new_value = self.vac_df.tail(1)['dosen_kumulativ'].values[0]
        return new_value

    def get_extrapolated_abs_doses(self):
        official_doses = self.get_official_abs_doses()
        official_doses_timestamp = self.vac_freshness_timestamp

        time_difference_secs = mytime.business_time_since(official_doses_timestamp)

        mean = self.get_average_daily_vacs_of_last_days(LOOK_BACK_FOR_MEAN)
        extra_vacs = self.extrapolate(mean, time_difference_secs)
        total_vacs = official_doses + extra_vacs
        total_vacs = '{:,}'.format(total_vacs).replace(',', '.')
        log_string = f'Mean {mean} of {LOOK_BACK_FOR_MEAN} days, {"{:.1f}".format((time_difference_secs / 60 / 60))} hrs passed -> {extra_vacs} extra vacs + {official_doses} previous doses = {total_vacs}'
        # store it!
        changed = not (self.bay_vac == total_vacs)
        self.bay_vac = total_vacs
        self.save_storage()
        return total_vacs, changed, log_string

    def extrapolate(self, daily_mean, seconds):
        progress = (seconds / mytime.daily_business_time_seconds())
        extra_vacs = int(daily_mean * progress)
        return extra_vacs

    def get_average_daily_vacs_of_last_days(self, days_to_look_back):
        mean = self.vac_df.tail(days_to_look_back)[
            'dosen_kumulativ_differenz_zum_vortag'].values.mean()
        return int(mean)
