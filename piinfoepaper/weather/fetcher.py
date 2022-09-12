import os
import logging
import urllib.request, json

import requests
from piinfoepaper.storage import retrieve, store

import piinfoepaper.mytime as mytime

API_BASE_URL = 'https://s3.eu-central-1.amazonaws.com/app-prod-static.warnwetter.de/v16/'
API_MODIFIER = 'forecast_mosmix_%s.json'

# Not to be confused with station ID!
stations_kennungen = {
    'muenchen': '10865',
}

STORAGE_FILE = 'storage.json'


class Fetcher:
    last_check_timestamp = 0

    def get_relevant_data_if_needed(self, min_delta=1680):
        delta = mytime.current_time() - self.last_check_timestamp
        if delta < min_delta:  # 1680 = 28 minutes
            logging.info(f'Skipping Data Download. Last Update was {round(delta / 1)} seconds ago.')
            return retrieve(STORAGE_FILE)
        json = self.get_relevant_data()

        try:
            if json is not None:
                store(STORAGE_FILE, json)
        except:
            pass
        return json

    def get_relevant_data(self):
        try:
            url = f'{API_BASE_URL}{API_MODIFIER.replace("%s", stations_kennungen["muenchen"])}'
            response = requests.get(url)
            if (response.status_code != 200):
                # Do error handling
                logging.error(f'Problem! {url} returned status code: {response.status_code}')
                return None
            # All is well

            return response.json()

        except Exception as e:
            logging.exception(f"ERROR when getting data. Using old values if available.")
