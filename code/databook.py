import logging
import os

import urllib.request, json

import mytime as mytime
import fetcher as fet
from enum import Enum
import trend as mytrend

LOOK_BACK_FOR_MEAN = 3
# 34 because: imagine it's a day old, during business hours it would just download new data. But at 34 hrs old,
# it's 18:00 on the next day end of business hours. A good reason to download it anyway!
OLDNESS_THRESHOLD_LARGE = 3600 * 34  # 3600 = 1 hour
OLDNESS_THRESHOLD_SMALL = 3600 * 10  # 3600 = 1 hour
DOWNLOAD_TIMEOUT = 60 * 11

STORAGE_FILE = 'storage.json'


class Ampel_color(Enum):
    RED = 'ampel-red-small.bmp'
    YELLOW = 'ampel-yellow-small.bmp'
    GREEN = 'ampel-green-small.bmp'

class Freshness(Enum):
    FRESH = 0
    DAY_OLD = 1
    OLD = 2


class Databook:

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        fetcher = fet.Fetcher()
        fetcher.get_relevant_data_if_needed()
        self.load_storage()

    def load_storage(self):
        if not os.path.isfile(STORAGE_FILE):
            logging.info(f'{STORAGE_FILE} does not exist (yet)')
            fetcher = fet.Fetcher()
            fetcher.get_relevant_data()
            fetcher.save_storage()
            return  # no file?
        from storage import retrieve
        storage = retrieve(STORAGE_FILE)

        self.last_check_timestamp = storage['last_check_timestamp']
        self.districts = storage['districts']
        self.bavaria_dict = storage['bavaria']
        self.bavaria_vax = storage['bavaria_vax']
        self.bavaria_icu = storage['bavaria_icu']
        logging.debug(f'Loaded {STORAGE_FILE}')

    def get_munich_inc(self):
        inz = round(self.districts['munich']['week_incidence'])
        trend = self.districts['munich']['incidence_trend']
        freshness = self.evaluate_freshness(self.districts['munich']['date'], label="München Inc")
        return inz, trend, freshness

    def get_miesbach_inc(self):
        inz = round(self.districts['miesbach']['week_incidence'])
        trend = self.districts['miesbach']['incidence_trend']
        freshness = self.evaluate_freshness(self.districts['miesbach']['date'], label="Miesbach Inc")
        return inz, trend, freshness

    def get_munich_lk_inc(self):
        inz = round(self.districts['munich_lk']['week_incidence'])
        trend = self.districts['munich_lk']['incidence_trend']
        freshness = self.evaluate_freshness(self.districts['munich_lk']['date'], label="München LK Inc")
        return inz, trend, freshness

    def get_bavaria_inc(self):
        inz = round(self.bavaria_dict['bavaria_week_incidence'])
        trend = self.bavaria_dict['incidence_trend']
        freshness = self.evaluate_freshness(self.bavaria_dict['date'], label="Bayern Inc")
        return inz, trend, freshness

    def get_bavaria_vax(self):
        freshness = self.evaluate_freshness(self.bavaria_vax['date'], label='Bavaria Vax')
        return f'{self.bavaria_vax["percentage"]}%', freshness

    def get_bavaria_hospital(self):
        freshness = self.evaluate_freshness(self.bavaria_dict['date'], 'Bavaria Hosp')
        return self.bavaria_dict['bavaria_hospital_cases_7_days'], freshness

    def get_bavaria_icu(self):
        icu_cases = round(self.bavaria_icu['icu'])
        trend = self.bavaria_icu['icu_trend']
        freshness = self.evaluate_freshness(self.bavaria_icu['date'], label='Bavaria ICU')
        return icu_cases, trend, freshness

    def get_bavaria_ampel_color(self):
        return Ampel_color.RED.value

    def evaluate_ampel_status(self):
        hosp = self.get_bavaria_hospital()[0]
        icu = self.get_bavaria_icu()[0]
        ampel = Ampel_color.GREEN
        if icu >= 600:
            ampel = Ampel_color.RED
        elif icu >= 450:
            ampel = Ampel_color.YELLOW
        elif hosp >= 1200:
            ampel = Ampel_color.YELLOW
        logging.info(f'Decided on Ampel being: {ampel} based on hosp:{hosp} and icu:{icu}')
        return ampel

    SHIFT_DICT = {
        'Bayern Inc': 1,
        'München Inc': 0,
        'Miesbach Inc': 0,
        'München LK Inc': 0,
        'Bavaria ICU': 0,
        'Bavaria Hosp': 1,
        'Bavaria Vax': 0,
    }

    FORMAT_DICT = {
        'Bayern Inc': '%Y-%m-%dT%H:%M:%S.%fZ',
        'München Inc': '%Y-%m-%dT%H:%M:%S.%fZ',
        'Miesbach Inc': '%Y-%m-%dT%H:%M:%S.%fZ',
        'München LK Inc': '%Y-%m-%dT%H:%M:%S.%fZ',
        'Bavaria ICU': '%Y-%m-%d',
        'Bavaria Hosp': '%Y-%m-%dT%H:%M:%S.%fZ',
        'Bavaria Vax': '%Y-%m-%dT%H:%M:%S.%fZ',
    }
    # shift for disctricts = 0
    # shift for bav inc = 1
    def evaluate_freshness(self, date, label):
        try:
            format = self.FORMAT_DICT[label]
            shift = self.SHIFT_DICT[label]
        except:
            shift = 0
            format='%Y-%m-%dT%H:%M:%S.%fZ'

        timestamp = mytime.string2timestamp(date, time_format=format)
        delta_in_secs = mytime.current_time() - timestamp - 24*60*60*shift
        delta_in_hours = round(delta_in_secs / 60 / 60)
        logging.info(f"{label} is {delta_in_hours} hours old")

        if delta_in_hours < 24:
            return Freshness.FRESH
        elif delta_in_hours < 40:
            return Freshness.DAY_OLD
        else:
            return Freshness.OLD
