import os
import logging
import csv
import math
import numpy as np
import pandas as pd

import urllib.request, json

import dataprep as dp
import mytime as mytime
import fetcher as fet


LOOK_BACK_FOR_MEAN = 3
# 34 because: imagine it's a day old, during business hours it would just download new data. But at 34 hrs old,
# it's 18:00 on the next day end of business hours. A good reason to download it anyway!
OLDNESS_THRESHOLD_LARGE = 3600 * 34  # 3600 = 1 hour
OLDNESS_THRESHOLD_SMALL = 3600 * 10  # 3600 = 1 hour
DOWNLOAD_TIMEOUT = 60 * 11

STORAGE_FILE = 'databook-storage.json'


def week_day_string(weekday):
    if weekday == 0:
        return 'Mon'
    elif weekday == 1:
        return 'Tue'
    elif weekday == 2:
        return 'Wed'
    elif weekday == 3:
        return 'Thu'
    elif weekday == 4:
        return 'Fri'
    elif weekday == 5:
        return 'Sat'
    elif weekday == 6:
        return 'Sun'
    else:
        return 'other'


def is_weekend(weekday):
    if weekday == 5:
        return True
    elif weekday == 6:
        return True
    else:
        return False


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

    return is_needed, reason


class Databook:

    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        # TIMESTAMPS
        self.timestamp_vac = 0
        self.timestamp_inf = 0
        self.timestamp_hos = 0

        self.vac_dl_attempt_timestamp = 0
        self.inf_dl_attempt_timestamp = 0
        self.hos_dl_attempt_timestamp = 0

        # VACCINE DOSES
        self.bay_vac = -1

        # INZIDENZ
        self.muc_inz = -1
        self.bay_inz = -1
        self.muc_inz_prev = -1
        self.bay_inz_prev = -1

        # HOSPITAL
        self.hospital_cases7 = -1
        self.hospital_icu_cases = -1

        self.load_storage()
        self.maybe_download_data()
        self.check_data_freshness()
        self.save_storage()

        self.inf_js = self.load_infect_json()
        self.hos_js = self.load_hospital_json()
        self.vac_df = self.load_vac_dataframe()

    def load_storage(self):
        if not os.path.isfile(STORAGE_FILE):
            logging.info(f'{STORAGE_FILE} does not exist (yet)')
            return  # no file?
        from storage import retrieve
        try:
            storage = retrieve(STORAGE_FILE)
        except:
            logging.info(f'{STORAGE_FILE} is broken. Pretending it does not exist.')
            return
        self.timestamp_vac = storage['timestamp_vac']
        self.timestamp_inf = storage['timestamp_inf']
        self.timestamp_hos = storage['timestamp_hos']

        self.vac_dl_attempt_timestamp = storage['vac_dl_attempt_timestamp']
        self.inf_dl_attempt_timestamp = storage['inf_dl_attempt_timestamp']
        self.hos_dl_attempt_timestamp = storage['hos_dl_attempt_timestamp']

        # VACCINE DOSES
        self.bay_vac = storage['bay_vac']

        # INZIDENZ
        self.muc_inz = storage['muc_inz']
        self.bay_inz = storage['bay_inz']
        self.muc_inz_prev = storage['muc_inz_prev']
        self.bay_inz_prev = storage['bay_inz_prev']

        # HOSPITAL
        self.hospital_cases7 = storage['hospital_cases7']
        self.hospital_icu_cases = storage['hospital_icu_cases']
        logging.debug(f'Loaded {STORAGE_FILE}')

    def save_storage(self):
        storage = {
            'timestamp_vac': int(self.timestamp_vac),
            'timestamp_inf': int(self.timestamp_inf),
            'timestamp_hos': int(self.timestamp_hos),

            'vac_dl_attempt_timestamp': int(self.vac_dl_attempt_timestamp),
            'inf_dl_attempt_timestamp': int(self.inf_dl_attempt_timestamp),
            'hos_dl_attempt_timestamp': int(self.hos_dl_attempt_timestamp),
            # VAC
            'bay_vac': self.bay_vac,
            # INF
            'bay_inz_prev': self.bay_inz_prev,
            'bay_inz': self.bay_inz,
            'muc_inz_prev': self.muc_inz_prev,
            'muc_inz': self.muc_inz,
            # HOS
            'hospital_cases7': self.hospital_cases7,
            'hospital_icu_cases': self.hospital_icu_cases,
        }
        from storage import store
        store(STORAGE_FILE, storage)

    def check_data_freshness(self):
        new_vac_ts = self.get_vac_file_timestamp()
        new_inf_ts = self.get_inf_file_timestamp()
        new_hos_ts = self.get_hos_file_timestamp()

        if new_vac_ts > self.timestamp_vac:
            logging.info(f'NEW VAC DATA. Freshness: {mytime.ts2dt(new_vac_ts)}')
            self.vac_freshness_timestamp = new_vac_ts

        if new_inf_ts > self.timestamp_inf:
            logging.info(f'NEW INF DATA. Freshness: {mytime.ts2dt(new_inf_ts)}')
            self.inf_freshness_timestamp = new_inf_ts

        if new_hos_ts > self.timestamp_hos:
            logging.info(f'NEW HOS DATA. Freshness: {mytime.ts2dt(new_hos_ts)}')
            self.hos_freshness_timestamp = new_hos_ts

    def is_fresh_vac_data_needed(self):
        # TODO undo hardcoded filename
        return is_fresh_data_needed(self.timestamp_vac, "vac.csv")

    def is_fresh_inf_data_needed(self):
        # TODO undo hardcoded filename
        return is_fresh_data_needed(self.timestamp_inf, "inf.json")

    def is_fresh_hos_data_needed(self):
        # TODO undo hardcoded filename
        return is_fresh_data_needed(self.timestamp_hos, "hos.json")

    # Only downloads data if it is not existent or old
    def maybe_download_data(self):
        seconds_since_last_attempt_vac = mytime.current_time() - self.vac_dl_attempt_timestamp
        seconds_since_last_attempt_inf = mytime.current_time() - self.inf_dl_attempt_timestamp
        seconds_since_last_attempt_hos = mytime.current_time() - self.hos_dl_attempt_timestamp

        is_fresh_vac_data_needed = self.is_fresh_vac_data_needed()
        is_fresh_inf_data_needed = self.is_fresh_inf_data_needed()
        is_fresh_hos_data_needed = self.is_fresh_hos_data_needed()

        fetcher = fet.Fetcher()


        if (is_fresh_vac_data_needed[0] and seconds_since_last_attempt_vac >= DOWNLOAD_TIMEOUT) or os.path.isfile(fet.CSV_VAC['file']):
            fetcher.download_csv_vac_data()
            logging.info(f"Downloaded {fet.CSV_VAC['file']}")
            self.vac_dl_attempt_timestamp = mytime.current_time()
        else:
            delta = mytime.seconds2delta_hr(seconds_since_last_attempt_vac)
            logging.info(
                f"Skipping vac download. Last attempt {delta} ago. isNeeded: {is_fresh_vac_data_needed}")

        if (is_fresh_inf_data_needed[0] and seconds_since_last_attempt_inf >= DOWNLOAD_TIMEOUT) or os.path.isfile(fet.CASES['file']):
            fetcher.download_infect_json()
            logging.info(f"Downloaded infect.json")
            self.inf_dl_attempt_timestamp = mytime.current_time()
        else:
            delta = mytime.seconds2delta_hr(seconds_since_last_attempt_inf)
            logging.info(
                f'Skipping inf download. Last attempt {delta} ago. isNeeded: {is_fresh_inf_data_needed}')

        if (is_fresh_hos_data_needed[0] and seconds_since_last_attempt_hos >= DOWNLOAD_TIMEOUT) or os.path.isfile(fet.HOSPIT['file']):
            fetcher.download_hospit_json()
            logging.info(f"Downloaded {fet.HOSPIT['file']}")
            self.hos_dl_attempt_timestamp = mytime.current_time()
        else:
            delta = mytime.seconds2delta_hr(seconds_since_last_attempt_hos)
            logging.info(
                f"Skipping hos download. Last attempt {delta} ago. isNeeded: {is_fresh_hos_data_needed}")


        fetcher.save_storage()  # TODO can we remove this because it's already saved in fetcher.download_data()... ?

    def get_inf_file_timestamp(self):
        with open('infect.json') as json_file:
            data = json.load(json_file)
            time_string = data['features'][0]['attributes']['last_update']
            print(f"time_string: {time_string}")
            time_string = time_string.replace(" Uhr", "")
            print(f"time_string after replace: {time_string}")
            self.timestamp_hospital = mytime.string2timestamp(time_string, time_format="%d.%m.%Y, %H:%M")
            print(f"self.timestamp_hospital: {self.timestamp_hospital}")

    def get_hos_file_timestamp(self):
        with open('hospital.json') as json_file:
            data = json.load(json_file)
            time_string = data["datenstand_lgl"]
            print(f"time_string: {time_string}")
            time_string = time_string.replace("00:00 Uhr", "08:00 Uhr")
            time_string = time_string.replace(" Uhr", "")
            print(f"time_string after replace: {time_string}")
            self.timestamp_hospital = mytime.string2timestamp(time_string, time_format="%d.%m.%Y, %H:%M")
            print(f"self.timestamp_hospital: {self.timestamp_hospital}")

    def get_vac_file_timestamp(self):
        df = pd.read_csv(fet.CSV_VAC['file'], sep=',',
                         index_col=0, parse_dates=True)
        last_update = ((df.tail(1).index.astype(
            np.int64) // 10 ** 9)).tolist()[0] + 60 * 60 * (24 + 6)
        return last_update

    def load_hospital_json(self):
        with open('hospital.json') as json_file:
            data = json.load(json_file)
            # self.hospitalisierung = data["hospitalisierung"]
            # self.intensiv = data["intensiv"]
            return data

    def load_infect_json(self):
        with open('infect.json') as json_file:
            data = json.load(json_file)
            return data


    def load_vac_dataframe(self):
        # VACC
        csv_path = fet.CSV_VAC['file']
        df = pd.read_csv(
            csv_path, sep=',', index_col=0, parse_dates=True)

        df = df[['publication_date', 'dosen_kumulativ']]
        df = self.add_dif_column(df)
        df = self.fix_missing_days(df)
        self.fix_nan_dosen(df)
        self.add_weekday_stuff(df)
        df = self.add_shots_sum(df)
        return df

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # #                                                                                 # # # # # #
    # # # # # #                            Datascience Prep                                     # # # # # #
    # # # # # #                                                                                 # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def add_dif_column(self, df):
        df['shots_today'] = df.dosen_kumulativ - df.dosen_kumulativ.shift(1)
        df['shots_today'] = df['shots_today'].fillna(0)
        return df.astype({'shots_today': 'int64'})

    def fix_missing_days(self, df):
        # fill in the dates
        idx = pd.date_range(start='2020-12-26', end=df.index.max())

        df = df.reindex(idx)

        # Create new index column because that's waay easier than having the date column be the index
        df = df.reset_index()
        df.at[0, 'dosen_kumulativ'] = 0
        df.at[0, 'shots_today'] = 0
        df.at[1, 'shots_today'] = df.iloc[1, :]['dosen_kumulativ']

        return df.rename(columns={'index': 'date'})

    def fix_nan_dosen(self, df):
        i = 0
        while i < len(df.index):
            row = df.iloc[i, :]
            # print(f'{row} with type: {type(row)}')
            if pd.isnull(row['shots_today']):
                j = 1
                new_row = df.iloc[i + j, :]
                while pd.isnull(new_row['shots_today']):
                    j = j + 1
                    new_row = df.iloc[i + j, :]
                next_valid_row = df.iloc[i + j, :]
                quotient = next_valid_row['shots_today'] / (j + 1)
                df.at[i + j, 'shots_today'] = quotient
                for to_change in range(i, i + j):
                    df.at[to_change, 'shots_today'] = quotient
                i = i + j
            else:
                i = i + 1

    def add_weekday_stuff(self, df):
        df['weekday'] = df.date.dt.dayofweek
        df['is_weekend'] = df.apply(lambda x: is_weekend(x['weekday']), axis=1)
        df['weekday_name'] = df.apply(lambda x: week_day_string(x['weekday']), axis=1)
        df['calendar_week'] = df.date.dt.week

    def add_shots_sum(self, df):
        df['shots_sum'] = 0
        df['shots_sum'] = df['shots_today'].cumsum().round()
        df['shots_sum'] = df.shots_sum.astype(int)  # hmm
        return df

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # #                                                                                 # # # # # #
    # # # # # #                            Datascience get Data                                 # # # # # #
    # # # # # #                                                                                 # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_inz_bavaria(self):
        data = self.load_infect_json()
        new_inz = round(data['features'][0]['attributes']['cases7_bl_per_100k'],1)
        changed = not self.bay_inz == new_inz
        if changed:
            self.bay_inz_prev = self.bay_inz
            self.bay_inz = new_inz
            self.save_storage()
        trend = dp.trend(float(self.bay_inz_prev), float(self.bay_inz))
        return new_inz, changed, trend.value

    def get_inz_munich(self):
        data = self.load_infect_json()
        new_inz = round(data['features'][0]['attributes']['cases7_per_100k'], 1)
        changed = not self.muc_inz == new_inz
        if changed:
            self.muc_inz_prev = self.muc_inz
            self.muc_inz = new_inz
            self.save_storage()

        trend = dp.trend(float(self.muc_inz_prev), float(self.muc_inz))
        return new_inz, changed, trend.value

    def get_official_abs_doses(self):
        new_value = self.vac_df.tail(1)['shots_sum'].values[0]
        return new_value

    def get_extrapolated_abs_doses(self):
        official_doses = self.get_official_abs_doses()
        official_doses_timestamp = self.vac_freshness_timestamp

        time_difference_secs = mytime.business_time_since(official_doses_timestamp)

        is_weekend = self.is_next_day_weekend(self.vac_df)
        mean = self.guess_next_days_vacs(self.vac_df, is_weekend)
        extra_vacs = self.extrapolate(mean, time_difference_secs)
        total_vacs = official_doses + extra_vacs
        total_vacs = '{:,}'.format(total_vacs).replace(',', '.')
        log_string = f'Mean {mean} of {LOOK_BACK_FOR_MEAN} days (weekend: {is_weekend}), {str(mytime.seconds2delta(time_difference_secs)).split(".")[0]} passed -> {extra_vacs} extra vacs + {official_doses} previous doses = {total_vacs}'
        # store it!
        changed = not (self.bay_vac == total_vacs)
        self.bay_vac = total_vacs
        self.save_storage()
        return total_vacs, changed, log_string

    def extrapolate(self, daily_mean, seconds):
        progress = (seconds / mytime.daily_business_time_seconds())
        extra_vacs = int(daily_mean * progress)
        return extra_vacs

    def guess_next_days_vacs(self, df, is_weekend):
        df_filtered = df[df['is_weekend'] == is_weekend]
        mean = df_filtered.tail(LOOK_BACK_FOR_MEAN)['shots_today'].values.mean()
        return math.ceil(mean)

    def is_next_day_weekend(self, df):
        next_day = df.tail(1).date + pd.DateOffset(1)
        if next_day.dt.dayofweek.values[0] > 4:
            return True
        else:
            return False
