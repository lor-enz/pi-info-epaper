import datetime

import os
import logging

import csv
import requests

import mytime as tt

logging.basicConfig(level=logging.INFO)

CSV_VAC = {
    'url': 'https://raw.githubusercontent.com/ard-data/2020-rki-impf-archive/master/data/9_csv_v2/region_BY.csv',
    'file': 'vac.csv',
    'key': 'vac_download_timestamp'
}
CSV_INF = {
    'url': 'https://opendata.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0.csv',
    'file': 'inf.csv',
    'key': 'inf_download_timestamp'
}


def fix_comma_in_csv(filename):
    fin = open(filename, "rt")
    data = fin.read()

    data = data.replace('"," ', '_')
    data = data.replace('","', '.')
    data = data.replace('\"', '')
    fin.close()
    fin = open(filename, "wt")
    fin.write(data)
    fin.close()


def vac_file_path():
    return CSV_VAC['file']


def inf_file_path():
    return CSV_INF['file']


STORAGE_FILE = 'fetcher-storage.json'


class Fetcher:

    def __init__(self):
        self.load_storage()

        self.vac_download_timestamp = 0
        self.inf_download_timestamp = 0

    def load_storage(self):
        if not os.path.isfile(STORAGE_FILE):
            logging.info(f'{STORAGE_FILE} does not exist (yet)')
            return  # no file?
        from storage import retrieve
        storage = retrieve(STORAGE_FILE)
        self.inf_download_timestamp = storage[CSV_INF['key']]
        self.vac_download_timestamp = storage[CSV_VAC['key']]

        logging.info(f'Loaded {STORAGE_FILE}')

    def save_storage(self):
        storage = {
            CSV_INF['key']: self.inf_download_timestamp,
            CSV_VAC['key']: self.vac_download_timestamp
        }
        from storage import store
        store(STORAGE_FILE, storage)

    def print_storage(self):
        return f'vac.csv downloaded at: {self.inf_download_timestamp}  inf.csv downloaded at: {self.vac_download_timestamp}'

    def download_all_data(self):
        self.download_data(CSV_INF)
        self.download_data(CSV_VAC)
        fix_comma_in_csv(CSV_INF['file'])

    def download_data(self, csv_data):
        response = requests.get(csv_data['url'])

        with open(csv_data['file'], 'w') as f:
            writer = csv.writer(f)
            for line in response.iter_lines():
                writer.writerow(line.decode('utf-8').split(','))
        if csv_data['file'] == 'vac.csv':
            self.vac_download_timestamp = tt.current_time()
        elif csv_data['file'] == 'inf.csv':
            self.inf_download_timestamp = tt.current_time()
            fix_comma_in_csv(CSV_INF['file'])
        else:
            logging.error(
                f"Unknown filename! Expected vac.csv or inf.csv. Got {csv_data['file']}")
