import os
import logging
import csv
import requests
import urllib.request, json
import mytime as mytime

CSV_VAC = {
    'url': 'https://raw.githubusercontent.com/ard-data/2020-rki-impf-archive/master/data/9_csv_v3/region_BY.csv',
    'file': 'vac.csv',
    'key': 'vac_download_timestamp'
}

HOSPIT = {
    # Bundesland id for bayern is 9 (I think?)
    # bayern_ampel_url
    'url_noid':'https://krankenhausampel.info/corona/?bl_id=',
    'url_9':'https://krankenhausampel.info/corona/?bl_id=9',
    'file': 'hospital.json',
    'key': 'hos_download_timestamp'
}
landkreisObjectId = 224
CASES = {
    # rki_rest_sk_muc
    'url': f'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=OBJECTID%20%3E%3D%20{landkreisObjectId}%20AND%20OBJECTID%20%3C%3D%20{landkreisObjectId}&outFields=OBJECTID,death_rate,cases,deaths,cases_per_100k,cases_per_population,BL,BL_ID,county,last_update,cases7_per_100k,recovered,cases7_bl_per_100k&outSR=4326&f=json',
    'file': 'infect.json',
    'key': 'inf_download_timestamp'
}

STORAGE_FILE = 'fetcher-storage.json'

class Fetcher:

    def __init__(self):
        # is probably 9 but might change in future, and we wouldn't notice. So we'll fill it with the correct value
        self.bl_id = 0
        self.load_storage()

    def load_storage(self):
        if not os.path.isfile(STORAGE_FILE):
            logging.info(f'{STORAGE_FILE} does not exist (yet)')
            return  # no file?
        from storage import retrieve
        storage = retrieve(STORAGE_FILE)

        self.bl_id = storage['bl_id']
        logging.debug(f'Loaded {STORAGE_FILE}')

    def save_storage(self):
        storage = {
            'bl_id': int(self.bl_id)
        }
        from storage import store
        store(STORAGE_FILE, storage)

    def download_all_data(self):
        self.download_csv_vac_data()
        self.download_infect_json()
        self.download_hospit_json()

    # csv_data_object holds url, file and key
    def download_csv_vac_data(self):
        response = requests.get(CSV_VAC['url'])

        with open(CSV_VAC['file'], 'w') as f:
            writer = csv.writer(f)
            for line in response.iter_lines():
                writer.writerow(line.decode('utf-8').split(','))

        self.save_storage()

    def download_infect_json(self):
        with urllib.request.urlopen(CASES['url']) as url:
            data = json.loads(url.read().decode("utf-8"))
            self.bl_id = data['features'][0]['attributes']['BL_ID']
            with open(CASES['file'], 'w') as f:
                json.dump(data, f)

    def download_hospit_json(self):
        with urllib.request.urlopen(f"{HOSPIT['url_noid']}{self.bl_id}") as url:
            data = json.loads(url.read().decode("utf-8"))
            with open(HOSPIT['file'], 'w') as f:
                json.dump(data, f)

