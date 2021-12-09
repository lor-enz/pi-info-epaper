import os
import logging
import urllib.request, json

import requests

import trend as mytrend

import mytime as mytime

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#    This class knows two APIs to retrieve it's information: Most is from corona-zahlen.org but the ICU numbers   #
#    aren't available there. We use an API made available by the BR News Network for that.                        #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# First API. Has Vax percentage, incidence numbers, hospital patients.
API_CZ_BASE_URL = 'https://api.corona-zahlen.org/'

# modifiers for the URL are directly in the function

# Additional API from https://github.com/br-data/corona-divi-api . Has ICU numbers.
API_BR_BASE_URL = 'https://europe-west3-brdata-corona.cloudfunctions.net/diviApi/'
# Anzahl gemeldeter intensivmedizinisch behandelter COVID-19-Fälle (in Bayern)
API_BR_MODIFIER_BY_ICU = 'query?area=BY&indicator=Patienten'
# Anzahl gemeldeter intensivmedizinisch behandelter COVID-19-Fälle an Anzahl belegter Intensivbetten (in Bayern)
API_BR_MODIFIER_BY_BED_PROP = 'query?area=BY&indicator=Bettenanteil'

# AGS = Allgemeiner Gemeindeschlüssel. List with the ids for the areas that are relevant to us. Found through Google
AGS = {
    'muenchen': '09162',
    'muenchen_lk': '09184',
    'miesbach': '09182'
}

STORAGE_FILE = 'storage.json'


class Fetcher:
    last_check_timestamp = 0

    # is actually saved with retrieved data, so this could be 0?
    bavaria_population = 13_140_183

    def __init__(self):
        storage = self.load_storage()

    def load_storage(self):
        if not os.path.isfile(STORAGE_FILE):
            logging.info(f'{STORAGE_FILE} does not exist (yet)')
            return {}  # no file?
        from storage import retrieve
        storage = retrieve(STORAGE_FILE)
        try:
            self.districts = storage['districts']
            self.bavaria_dict = storage['bavaria']
            self.bavaria_vax = storage['bavaria_vax']
            self.last_check_timestamp = storage['last_check_timestamp']
            self.bavaria_icu = storage['bavaria_icu']
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
            'last_check_timestamp': int(self.last_check_timestamp),
            'districts': self.districts,
            'bavaria': self.bavaria_dict,
            'bavaria_vax': self.bavaria_vax,
            'bavaria_icu': self.bavaria_icu,
        }
        from storage import store
        store(STORAGE_FILE, storage)

    def get_relevant_data_if_needed(self):
        delta = mytime.current_time() - self.last_check_timestamp
        if delta < 3500:
            logging.info(f'Skipping Data Download. Last Update was {round(delta / 1)} seconds ago.')
            return False
        self.get_relevant_data()
        return True

    def get_relevant_data(self):
        self.districts = self.get_district_incidence()
        self.bavaria_dict = self.get_bavaria_incidence_and_hospital_cases()
        self.bavaria_vax = self.get_bavaria_vaccination()

        self.last_check_timestamp = mytime.current_time()
        self.bavaria_icu = self.get_bavaria_icu()
        self.save_storage()  # TODO move this?

    def get_district_incidence(self):
        # TODO Workaround: Changed from frozen-incidence to incidence since frozen-incidence is currently broken on the API. This just breaks our ability to get the trend.
        response = requests.get(f'{API_CZ_BASE_URL}districts/history/incidence/20')
        if (response.status_code != 200):
            # Do error handling
            logging.error(f'Problem! {API_CZ_BASE_URL} returned status code: {response.status_code}')
            return

        districts = {}
        districts['munich'] = self.district_helper_function(response, AGS['muenchen'])
        districts['munich_lk'] = self.district_helper_function(response, AGS['muenchen_lk'])
        districts['miesbach'] = self.district_helper_function(response, AGS['miesbach'])

        return districts

    def district_helper_function(self, response, ags_id):
        history = response.json()['data'][ags_id]['history']
        trend = mytrend.trend(float(history[-2]['weekIncidence']), float(history[-1]['weekIncidence']))
        current = history[-1]['weekIncidence']
        # TODO Workaround: Since we're currently using the incidence instead of frozen-incidence we don't have the correct trend.
        # TODO Workaround: The date is shifted by one. So we're just putting it 23 hours and 59 minutes into the future
        return {
            'week_incidence': current,
            'incidence_trend': mytrend.Trend.UNKNOWN.value,
            'date': history[-1]['date'].replace('00:00:00.000Z', '23:59:00.000Z')
        }

    def get_bavaria_incidence_and_hospital_cases(self):
        # https: // api.corona - zahlen.org / states / BY / history / cases / 7
        response = requests.get(f'{API_CZ_BASE_URL}states/BY')
        if (response.status_code != 200):
            logging.error(f'Problem! {API_CZ_BASE_URL} returned status code: {response.status_code}')
            return {'bavaria_week_incidence': -1, 'incidence_trend': 'STEADY',
                    'bavaria_hospital_cases_7_days': -1}
        bavaria_week_incidence = round(response.json()['data']['BY']['weekIncidence'], 1)
        bavaria_hospital_cases_7_days = response.json()['data']['BY']['hospitalization']['cases7Days']
        self.bavaria_population = response.json()['data']['BY']['population']
        delta_cases = response.json()['data']['BY']['delta']['cases']
        timestamp_hosp = response.json()['meta']['lastUpdate']

        response = requests.get(f'{API_CZ_BASE_URL}states/BY/history/cases/8')
        if (response.status_code != 200):
            logging.error(f'Problem! {API_CZ_BASE_URL} returned status code: {response.status_code}')
            return {'bavaria_week_incidence': -1, 'incidence_trend': 'STEADY',
                    'bavaria_hospital_cases_7_days': -1}
        history = response.json()['data']['BY']['history']

        cases_last_7_days = 0
        for el in history:
            cases_last_7_days += el['cases']

        previous_inz = round((cases_last_7_days - delta_cases) / (self.bavaria_population / 100_000), 1)

        trend = mytrend.trend(float(previous_inz), float(bavaria_week_incidence))
        timestamp_bav_inc = history[-1]['date']
        return {'bavaria_week_incidence': bavaria_week_incidence,
                'incidence_trend': trend.value,
                'bavaria_hospital_cases_7_days': bavaria_hospital_cases_7_days,
                'date': timestamp_bav_inc
                }

    def get_bavaria_vaccination(self):
        response = requests.get(f'{API_CZ_BASE_URL}vaccinations')
        if (response.status_code != 200):
            logging.error(f'Problem! {API_CZ_BASE_URL} returned status code: {response.status_code}')
            return -344.04
        fully_vaccinated = response.json()['data']['states']['BY']['secondVaccination']['vaccinated']

        bavaria_double_vaccinated_percentage = round((fully_vaccinated / self.bavaria_population) * 100, 1)
        return {
            'percentage': bavaria_double_vaccinated_percentage,
            'date': response.json()['meta']['lastUpdate']
        }

    # # # # # #

    def get_bavaria_icu(self):
        response = requests.get(f'{API_BR_BASE_URL}{API_BR_MODIFIER_BY_ICU}')
        if (response.status_code != 200):
            logging.error(f'Problem! {API_BR_BASE_URL} returned status code: {response.status_code}')
            return {
                'icu': '?',
                'icu_trend': 'STEADY'
            }
        history = response.json()[-2:]

        trend = mytrend.trend(float(history[-2]['faelleCovidAktuell']), float(history[-1]['faelleCovidAktuell']))
        current = history[-1]['faelleCovidAktuell']

        result = {
            'icu': current,
            'icu_trend': trend.value,
            'date': response.json()[-1]['date']
        }
        return result
