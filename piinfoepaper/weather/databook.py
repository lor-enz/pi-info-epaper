import logging
import os
from fetcher import Fetcher
import piinfoepaper.mytime as mytime
STORAGE_FILE = 'storage.json'

class Databook:

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        fetcher = Fetcher()
        fetcher.get_relevant_data_if_needed()
        self.load_storage()

    def load_storage(self):
        if not os.path.isfile(STORAGE_FILE):
            logging.info(f'{STORAGE_FILE} does not exist (yet)')
            fetcher = Fetcher()
            fetcher.get_relevant_data()
            fetcher.save_storage()
            return  # no file?
        from piinfoepaper.storage import retrieve
        storage = retrieve(STORAGE_FILE)

        self.temp_min = storage['temp_min']
        self.temp_max = storage['temp_max']
        self.icon1 = storage['icon1']
        self.icon2 = storage['icon2']
        self.day_date = storage['day_date']
        logging.debug(f'Loaded {STORAGE_FILE}')

    def get_day_date(self):
        return self.day_date

    def get_pretty_date(self):
        datestring = f"{self.day_date}_07:00"
        datetime = mytime.string2datetime(datestring)
        return datetime.strftime("%d. %b")

    def get_temp_min(self):
        string = str(self.temp_min)
        string = string[:-1] + '.' + string[-1:] + '°'
        return string

    def get_temp_max(self):
        string = str(self.temp_max)
        string = string[:-1] + '.' + string[-1:] + '°'
        return string

    def get_day_of_week(self):
        datestring = f"{self.day_date}_07:00"
        datetime = mytime.string2datetime(datestring)
        weekday = mytime.weekday_to_german_short(datetime.weekday())
        logging.info(f"Weekday: {weekday}")
        return f"{weekday}."

    def are_icons_different(self):
        return not self.icon1 == self.icon2

    def get_random_icons(self):
        from random import randrange
        icon1 = randrange(32)
        return icon1, icon1+1

    def get_icon1(self):
        logging.info(f"returning icon {self.icon1}")
        return self.icon1

    def get_icon2(self):
        logging.info(f"returning icon {self.icon2}")
        return self.icon2

