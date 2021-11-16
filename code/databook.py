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
    RED = 'ampel-red-small.bmp',
    YELLOW = 'ampel-yellow-small.bmp',
    GREEN = 'ampel-green-small.bmp'


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
        return inz, trend

    def get_miesbach_inc(self):
        inz = round(self.districts['miesbach']['week_incidence'])
        trend = self.districts['miesbach']['incidence_trend']
        return inz, trend

    def get_munich_lk_inc(self):
        inz = round(self.districts['munich_lk']['week_incidence'])
        trend = self.districts['munich_lk']['incidence_trend']
        return inz, trend

    def get_bavaria_inc(self):
        inz = round(self.bavaria_dict['bavaria_week_incidence'])
        trend = self.bavaria_dict['incidence_trend']
        return inz, trend

    def get_bavaria_vax(self):
        return f'{self.bavaria_vax}%'

    def get_bavaria_hospital(self):
        return self.bavaria_dict['bavaria_hospital_cases_7_days']

    def get_bavaria_icu(self):
        icu_cases = round(self.bavaria_icu['icu'])
        trend = self.bavaria_icu['icu_trend']
        return icu_cases, trend

    def get_bavaria_ampel_color(self):
        return Ampel_color.RED.value

    def evaluate_ampel_status(self):
        hosp = self.get_bavaria_hospital()
        icu = self.get_bavaria_icu()[0]
        ampel = Ampel_color.GREEN
        if icu >= 600:
            ampel = Ampel_color.RED
        elif icu >= 450:
            ampel = Ampel_color.YELLOW
        elif hosp >= 1200:
            ampel = Ampel_color.YELLOW
        logging.info(f'Decided on Ampel being: {ampel}')
        return ampel
