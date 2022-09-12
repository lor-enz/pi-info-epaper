import logging
import os
import sys

from piinfoepaper.weather.fetcher import Fetcher
import piinfoepaper.mytime as mytime
from piinfoepaper.paper_elements import PaperTextElement, PaperImageElement
from piinfoepaper.paper_enums import Alignment, Fill, Orientation
from piinfoepaper.paper_layout import PaperLayout

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
        self.resdir = os.path.join(os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))), 'res')  # path next to this file
        if os.path.exists(self.resdir):
            sys.path.append(self.resdir)

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
        return icon1, icon1 + 1

    def get_icon1(self):
        logging.info(f"returning icon {self.icon1}")
        return self.icon1

    def get_icon_path(self, icon_nr):
        if 10 <= icon_nr <= 31:
            file_name = f'weather/{icon_nr}.bmp'
        elif 1 <= icon_nr <= 9:
            file_name = f'weather/0{icon_nr}.bmp'
        else:
            file_name = f'weather/00.bmp'

        return os.path.join(self.resdir, file_name)

    def get_icon2(self):
        logging.info(f"returning icon {self.icon2}")
        return self.icon2

    def get_paper_layout(self):
        text_elements = [
            PaperTextElement(480, 0, Alignment.TOP_RIGHT, Fill.GRAY4, f'{mytime.current_time_hr("%d %b %H:%M")}', 12),
            PaperTextElement(115, 55, Alignment.CENTERED, Fill.GRAY4, f'{self.get_day_of_week()}', 80),
            PaperTextElement(115, 125, Alignment.CENTERED, Fill.GRAY4, f'{self.get_pretty_date()}', 45),
            PaperTextElement(22, 280 - 27, Alignment.BOTTOM_LEFT, Fill.GRAY4, f'{self.get_temp_min()}', 80),
            PaperTextElement(480 - 22, 280 - 27, Alignment.BOTTOM_RIGHT, Fill.GRAY4, f'{self.get_temp_max()}', 80),
            PaperTextElement(240, 280 - 27, Alignment.BOTTOM_CENTER, Fill.GRAY4, '-', 80),
        ]

        if self.are_icons_different():
            image_elements = [
                PaperImageElement(405 - 128, 90, Alignment.CENTERED,
                                  f'{self.get_icon_path(self.get_icon1())}'),
                PaperImageElement(405, 90, Alignment.CENTERED,
                                  f'{self.get_icon_path(self.get_icon2())}')
            ]
        else:
            image_elements = [
                PaperImageElement(341, 90, Alignment.CENTERED,
                                  f'{self.get_icon_path(self.get_icon1())}')
            ]
        font_path = os.path.join(self.resdir, 'Font.ttc')
        return PaperLayout(Orientation.LANDSCAPE, font_path, text_elements, image_elements, None, None)
