import os
import logging
import csv
import math
import numpy as np
import pandas as pd

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

        self.inf_freshness_timestamp = 0
        self.vac_freshness_timestamp = 0
        self.inf_dl_attempt_timestamp = 0
        self.vac_dl_attempt_timestamp = 0
        self.bay_vac = -1
        self.muc_inz = -1
        self.bay_inz = -1
        self.muc_inz_prev = -1
        self.bay_inz_prev = -1
        self.load_storage()
        self.maybe_download_data()
        self.check_data_freshness()
        self.save_storage()
        self.inf_df = self.load_inf_dataframe()
        self.vac_df = self.load_vac_dataframe()

    def check_data_freshness(self):
        new_inf_ts = self.get_inf_last_update_timestamp()
        new_vac_ts = self.get_vac_last_update_timestamp()

        if new_inf_ts > self.inf_freshness_timestamp:
            logging.info(f'NEW INF DATA. Freshness: {mytime.ts2dt(new_inf_ts)}')
            self.inf_freshness_timestamp = new_inf_ts

        if new_vac_ts > self.vac_freshness_timestamp:
            logging.info(f'NEW VAC DATA. Freshness: {mytime.ts2dt(new_vac_ts)}')
            self.vac_freshness_timestamp = new_vac_ts

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
        self.inf_freshness_timestamp = storage['inf_freshness_timestamp']
        self.vac_freshness_timestamp = storage['vac_freshness_timestamp']
        self.inf_dl_attempt_timestamp = storage['inf_dl_attempt_timestamp']
        self.vac_dl_attempt_timestamp = storage['vac_dl_attempt_timestamp']
        self.bay_vac = storage['bay_vac']
        self.bay_inz = storage['bay_inz']
        self.muc_inz = storage['muc_inz']
        self.bay_inz_prev = storage['bay_inz_prev']
        self.muc_inz_prev = storage['muc_inz_prev']

        logging.debug(f'Loaded {STORAGE_FILE}')

    def save_storage(self):
        storage = {
            'inf_freshness_timestamp': int(self.inf_freshness_timestamp),
            'vac_freshness_timestamp': int(self.vac_freshness_timestamp),
            'inf_dl_attempt_timestamp': int(self.inf_dl_attempt_timestamp),
            'vac_dl_attempt_timestamp': int(self.vac_dl_attempt_timestamp),
            'bay_vac': self.bay_vac,
            'bay_inz_prev': self.bay_inz_prev,
            'bay_inz': self.bay_inz,
            'muc_inz_prev': self.muc_inz_prev,
            'muc_inz': self.muc_inz
        }
        from storage import store
        store(STORAGE_FILE, storage)

    def is_fresh_inf_data_needed(self):
        return is_fresh_data_needed(self.inf_freshness_timestamp, fet.CSV_INF['file'])

    def is_fresh_vac_data_needed(self):
        return is_fresh_data_needed(self.vac_freshness_timestamp, fet.CSV_VAC['file'])

    def maybe_download_data(self):
        seconds_since_last_attempt_inc = mytime.current_time() - self.inf_dl_attempt_timestamp
        seconds_since_last_attempt_vac = mytime.current_time() - self.vac_dl_attempt_timestamp
        is_fresh_inf_data_needed = self.is_fresh_inf_data_needed()
        is_fresh_vac_data_needed = self.is_fresh_vac_data_needed()

        fetcher = fet.Fetcher()

        if (is_fresh_inf_data_needed[0] and seconds_since_last_attempt_inc >= DOWNLOAD_TIMEOUT) or os.path.isfile(fet.CSV_INF['file']):
            fetcher.download_data(fet.CSV_INF)
            logging.info(f"Downloaded {fet.CSV_INF['file']}")
            self.inf_dl_attempt_timestamp = mytime.current_time()
        else:
            delta = mytime.seconds2delta_hr(seconds_since_last_attempt_inc)
            logging.info(
                f'Skipping inf download. Last attempt {delta} ago. isNeeded: {is_fresh_inf_data_needed}')
        if (is_fresh_vac_data_needed[0] and seconds_since_last_attempt_vac >= DOWNLOAD_TIMEOUT) or os.path.isfile(fet.CSV_VAC['file']):
            fetcher.download_data(fet.CSV_VAC)
            logging.info(f"Downloaded {fet.CSV_VAC['file']}")
            self.vac_dl_attempt_timestamp = mytime.current_time()
        else:
            delta = mytime.seconds2delta_hr(seconds_since_last_attempt_vac)
            logging.info(
                f"Skipping vac download. Last attempt {delta} ago. isNeeded: {is_fresh_vac_data_needed}")

        fetcher.save_storage()  # TODO can we remove this because it's already saved in fetcher.download_data()... ?

    def get_inf_last_update_timestamp(self):
        # TODO this should be done better, and with pandas not with csv, but pandas was being difficult...
        rows = []
        with open(fet.CSV_INF['file'], newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                rows.append(row)
        date_string = rows[-1][34]

        freshness_dt = mytime.string2datetime(time_string=date_string, time_format="%d.%m.%Y_%H:%M Uhr")
        freshness_dt = freshness_dt.replace(hour=8)
        return int(freshness_dt.timestamp())

    def get_vac_last_update_timestamp(self):
        df = pd.read_csv(fet.CSV_VAC['file'], sep=',',
                         index_col=0, parse_dates=True)
        last_update = ((df.tail(1).index.astype(
            np.int64) // 10 ** 9)).tolist()[0] + 60 * 60 * (24 + 6)
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
        the_one_row = self.inf_df[self.inf_df['county'] == 'SK München']
        new_inz = the_one_row['cases7_bl_per_100k']
        new_inz = "{:.1f}".format(new_inz.values[0])
        # store it!
        changed = not self.bay_inz == new_inz
        if changed:
            self.bay_inz_prev = self.bay_inz
            self.bay_inz = new_inz
            self.save_storage()
        trend = dp.trend(float(self.bay_inz_prev), float(self.bay_inz))
        return new_inz, changed, trend.value

    def get_inz_munich(self):
        the_one_row = self.inf_df[self.inf_df['county'] == 'SK München']
        new_inz = the_one_row['cases7_per_100k']
        new_inz = "{:.1f}".format(new_inz.values[0])
        # store it!
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
