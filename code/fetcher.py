import os
import logging
import urllib.request, json

import requests

import trend as mytrend

import mytime as mytime

API_URL_BASE = 'https://api.corona-zahlen.org/'

AGS = {
    'muenchen': '09162',
    'muenchen_lk': '09184',
    'miesbach': '09182'
}

STORAGE_FILE = 'storage.json'


class Fetcher:
    last_check_timestamp = 0

    bavaria_population = 13_140_183

    def __init__(self):
        self.load_storage()

    def load_storage(self):
        if not os.path.isfile(STORAGE_FILE):
            logging.info(f'{STORAGE_FILE} does not exist (yet)')
            return  # no file?
        from storage import retrieve
        storage = retrieve(STORAGE_FILE)

        self.last_check_timestamp = storage['last_check_timestamp']
        self.districts = storage['districts']
        self.bavaria_dict = storage['bavaria']
        self.bavaria_vax = storage['bavaria_vax']
        logging.debug(f'Loaded {STORAGE_FILE}')

    def save_storage(self):
        storage = {
            'last_check_timestamp': int(self.last_check_timestamp),
            'districts': self.districts,
            'bavaria': self.bavaria_dict,
            'bavaria_vax': self.bavaria_vax,
        }
        from storage import store
        store(STORAGE_FILE, storage)

    def get_relevant_data_if_needed(self):
        delta = mytime.current_time() - self.last_check_timestamp
        if delta < 7200:
            print(f'Skipping Data Download. Last Update was {round(delta/1)} seconds ago.')
            return False
        self.get_relevant_data()
        return True

    def get_relevant_data(self):
        self.districts = self.get_district_incidence()
        self.bavaria_dict = self.get_bavaria_incidence_and_hospital_cases()
        self.bavaria_vax = self.get_bavaria_vaccination()

        self.last_check_timestamp = mytime.current_time()

    def get_district_incidence(self):
        response = requests.get(f'{API_URL_BASE}districts/history/frozen-incidence/3')
        if (response.status_code != 200):
            # Do error handling
            return

        districts = {}
        # # # # # # # # # # # #
        # # #     Muc     # # #

        history = response.json()['data'][AGS['muenchen']]['history']
        trend = mytrend.trend(float(history[-2]['weekIncidence']), float(history[-1]['weekIncidence']))
        current = history[-1]['weekIncidence']

        districts['munich'] = {
            'week_incidence': current,
            'incidence_trend': trend.value
        }

        # # # # # # # # # # # #
        # # #   Muc LK    # # #

        history = response.json()['data'][AGS['muenchen_lk']]['history']
        trend = mytrend.trend(float(history[-2]['weekIncidence']), float(history[-1]['weekIncidence']))
        current = history[-1]['weekIncidence']

        districts['munich_lk'] = {
            'week_incidence': current,
            'incidence_trend': trend.value
        }

        # # # # # # # # # # # #
        # # #  Miesbach   # # #

        history = response.json()['data'][AGS['miesbach']]['history']
        trend = mytrend.trend(float(history[-2]['weekIncidence']), float(history[-1]['weekIncidence']))
        current = history[-1]['weekIncidence']

        districts['miesbach'] = {
            'week_incidence': current,
            'incidence_trend': trend.value
        }

        return districts


    def get_bavaria_incidence_and_hospital_cases(self):
        # https: // api.corona - zahlen.org / states / BY / history / cases / 7
        response = requests.get(f'{API_URL_BASE}states/BY')
        if (response.status_code != 200):
            # Do error handling
            return
        bavaria_week_incidence = round(response.json()['data']['BY']['weekIncidence'], 1)
        bavaria_hospital_cases_7_days = response.json()['data']['BY']['hospitalization']['cases7Days']
        self.bavaria_population = response.json()['data']['BY']['population']
        delta_cases = response.json()['data']['BY']['delta']['cases']

        response = requests.get(f'{API_URL_BASE}states/BY/history/cases/8')
        if (response.status_code != 200):
            # Do error handling
            return
        history = response.json()['data']['BY']['history']

        cases_last_7_days = 0
        for el in history:
            cases_last_7_days += el['cases']
        # print(f'cases_last_7_days {cases_last_7_days}')

        previous_inz = round((cases_last_7_days - delta_cases) / (self.bavaria_population / 100_000), 1)
        # print(f'previous_inz {previous_inz}')
        trend = mytrend.trend(float(previous_inz), float(bavaria_week_incidence))
        # print(trend)
        return {'bavaria_week_incidence': bavaria_week_incidence, 'incidence_trend': trend.value,
                'bavaria_hospital_cases_7_days': bavaria_hospital_cases_7_days}

    def get_bavaria_vaccination(self):
        response = requests.get(f'{API_URL_BASE}vaccinations')
        if (response.status_code != 200):
            # Do error handling
            return
        fully_vaccinated = response.json()['data']['states']['BY']['secondVaccination']['vaccinated']
        bavaria_double_vaccinated_percentage = round((fully_vaccinated / self.bavaria_population) * 100, 1)
        return bavaria_double_vaccinated_percentage