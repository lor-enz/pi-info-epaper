import logging
import os
from fetcher import Fetcher
import piinfoepaper.mytime as mytime
STORAGE_FILE = 'storage.json'

class Databook:

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        fetcher = Fetcher()
        self.json = fetcher.get_relevant_data_if_needed()
        day_index = self.get_day_index_smart()
        forecast_day = self.json['days'][day_index]
        self.day_date = forecast_day['dayDate']
        self.temp_min = forecast_day['temperatureMin']
        self.temp_max = forecast_day['temperatureMax']
        self.icon1 = forecast_day['icon1']
        self.icon2 = forecast_day['icon2']

    def set_dummy_data(self):
        self.temp_min = -2732  # -273.2
        self.temp_max = 9990  # 999.0
        self.icon1 = 0
        self.icon2 = 0
        self.day_date = "1970-01-01"

    def get_day_index_smart(self):
        current_dt = mytime.ts2dt(mytime.current_time())
        do_we_want_tomorrows_forecast = current_dt.hour >= 19
        forecast_index = 0
        for i, obj in enumerate(self.json['days']):
            forecast_dt = mytime.string2datetime(f"{obj['dayDate']}_07:00")
            if current_dt.day == forecast_dt.day:
                forecast_index = i
        if do_we_want_tomorrows_forecast:
            forecast_index = forecast_index + 1
        return forecast_index


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

