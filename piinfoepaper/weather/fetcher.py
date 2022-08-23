import os
import logging
import urllib.request, json

import requests
from piinfoepaper.storage import retrieve, store

import piinfoepaper.mytime as mytime


API_BASE_URL = 'https://s3.eu-central-1.amazonaws.com/app-prod-static.warnwetter.de/v16/'
API_MODIFIER = 'forecast_mosmix_%s.json'

#Not to be confused with station ID!
stations_kennungen = {
    'muenchen': '10865',
}

STORAGE_FILE = 'storage.json'

class Fetcher:
    last_check_timestamp = 0

    def __init__(self):
        self.load_storage()
        self.temp_min = -2732 # -273.2
        self.temp_max = 9990  # 999.0
        self.icon1 = 0
        self.icon2 = 0
        self.day_date = "1970-01-01"

    def load_storage(self):
        if not os.path.isfile(STORAGE_FILE):
            logging.info(f'{STORAGE_FILE} does not exist (yet)')
            return {}  # no file?

        storage = retrieve(STORAGE_FILE)
        try:
            self.temp_min = storage['temp_min']
            self.temp_max = storage['temp_max']
            self.icon1 = storage['icon1']
            self.icon2 = storage['icon2']
            self.day_date = storage['day_date']
            logging.debug(f'Loaded {STORAGE_FILE}')
        except:
            logging.error(f'Error loading storage. Deleting storage.json to start fresh.')
            if os.path.exists(STORAGE_FILE):
                os.remove(STORAGE_FILE)
            else:
                logging.error(f"Deletion didn't work. File doesn't exist?")
        return storage

    def save_storage(self):
        storage = {
            'temp_min': self.temp_min,
            'temp_max': self.temp_max,
            'icon1': self.icon1,
            'icon2': self.icon2,
            'day_date': self.day_date,
        }
        store(STORAGE_FILE, storage)

    def get_relevant_data_if_needed(self):
        delta = mytime.current_time() - self.last_check_timestamp
        if delta < 1680:
            logging.info(f'Skipping Data Download. Last Update was {round(delta / 1)} seconds ago.')
            return False
        self.get_relevant_data()
        self.save_storage()  # TODO move this?
        return True


    def get_relevant_data(self):
        try:
            url = f'{API_BASE_URL}{API_MODIFIER.replace("%s", stations_kennungen["muenchen"])}'
            response = requests.get(url)
            if (response.status_code != 200):
                # Do error handling
                logging.error(f'Problem! {url} returned status code: {response.status_code}')
                return
            # All is well
            today = response.json()['days'][0]
            self.day_date = today['dayDate']
            self.temp_min = today['temperatureMin']
            self.temp_max = today['temperatureMax']
            self.icon1 = today['icon1']
            self.icon2 = today['icon2']

        except Exception as e:
            logging.exception(f"ERROR when getting data. Using old values if available.")