import logging
import os
import sys
from enum import Enum

from .fetcher import Fetcher
from .trend import Trend
import piinfoepaper.mytime as mytime
from piinfoepaper.paper_elements import PaperTextElement, PaperImageElement
from piinfoepaper.paper_enums import Alignment, Fill, Orientation
from piinfoepaper.paper_layout import PaperLayout

LOOK_BACK_FOR_MEAN = 3
# 34 because: imagine it's a day old, during business hours it would just download new data. But at 34 hrs old,
# it's 18:00 on the next day end of business hours. A good reason to download it anyway!
OLDNESS_THRESHOLD_LARGE = 3600 * 34  # 3600 = 1 hour
OLDNESS_THRESHOLD_SMALL = 3600 * 10  # 3600 = 1 hour
DOWNLOAD_TIMEOUT = 60 * 11

STORAGE_FILE = 'storage.json'


class Ampel_color(Enum):
    RED = 'ampel-red-small.bmp'
    YELLOW = 'ampel-yellow-small.bmp'
    GREEN = 'ampel-green-small.bmp'


class Freshness(Enum):
    FRESH = 0
    DAY_OLD = 1
    OLD = 2


class Databook:

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        fetcher = Fetcher()
        fetcher.get_relevant_data_if_needed()
        self.load_storage()
        self.resdir = os.path.join(os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))), 'res')  # path next to this file
        if os.path.exists(self.resdir):
            sys.path.append(self.resdir)

    def load_storage(self):
        if not os.path.isfile(STORAGE_FILE):
            logging.info(f'{STORAGE_FILE} does not exist (yet)')
            fetcher = Fetcher()
            fetcher.get_relevant_data()
            fetcher.save_storage()
            return  # no file?
        from piinfoepaper.storage import retrieve
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
        try:
            freshness = self.evaluate_freshness(self.districts['munich']['date'], label="München Inc")
        except:
            logging.error("something is wrong with munich_sk inc")
            return -1, Trend.UNKNOWN.value, Freshness.FRESH
        return inz, freshness, trend

    def get_miesbach_inc(self):
        inz = round(self.districts['miesbach']['week_incidence'])
        trend = self.districts['miesbach']['incidence_trend']
        try:
            freshness = self.evaluate_freshness(self.districts['miesbach']['date'], label="Miesbach Inc")
        except:
            logging.error("something is wrong with miesbach inc")
            return -1, Trend.UNKNOWN.value, Freshness.FRESH
        return inz, freshness, trend

    def get_munich_lk_inc(self):
        inz = round(self.districts['munich_lk']['week_incidence'])
        trend = self.districts['munich_lk']['incidence_trend']
        try:
            freshness = self.evaluate_freshness(self.districts['munich_lk']['date'], label="München LK Inc")
        except:
            logging.error("something is wrong with munich_lk inc")
            return -1, Trend.UNKNOWN.value, Freshness.FRESH
        return inz, freshness, trend

    def get_bavaria_inc(self):
        inz = round(self.bavaria_dict['bavaria_week_incidence'])
        trend = self.bavaria_dict['incidence_trend']
        try:
            freshness = self.evaluate_freshness(self.bavaria_dict['date'], label="Bayern Inc")
        except:
            logging.error("something is wrong with bavaria inc")
            return -1, Trend.UNKNOWN.value, Freshness.FRESH
        return inz, freshness, trend

    def get_bavaria_vax(self):
        freshness = self.evaluate_freshness(self.bavaria_vax['date'], label='Bavaria Vax')
        return f'{self.bavaria_vax["percentage"]}%', freshness, Trend.UNKNOWN

    def get_bavaria_hospital(self):
        freshness = self.evaluate_freshness(self.bavaria_dict['date'], 'Bavaria Hosp')
        return self.bavaria_dict['bavaria_hospital_cases_7_days'], freshness, Trend.UNKNOWN

    def get_bavaria_icu(self):
        icu_cases = round(self.bavaria_icu['icu'])
        trend = self.bavaria_icu['icu_trend']
        freshness = self.evaluate_freshness(self.bavaria_icu['date'], label='Bavaria ICU')
        return icu_cases, freshness, trend

    def get_bavaria_ampel_color(self):
        return Ampel_color.RED.value

    def evaluate_ampel_status(self):
        hosp = self.get_bavaria_hospital()[0]
        icu = self.get_bavaria_icu()[0]
        ampel = Ampel_color.GREEN
        if icu >= 600:
            ampel = Ampel_color.RED
        elif icu >= 450:
            ampel = Ampel_color.YELLOW
        elif hosp >= 1200:
            ampel = Ampel_color.YELLOW
        logging.info(f'Decided on Ampel being: {ampel} based on hosp:{hosp} and icu:{icu}')
        return ampel

    SHIFT_DICT = {
        'Bayern Inc': 1,
        'München Inc': 0,
        'Miesbach Inc': 0,
        'München LK Inc': 0,
        'Bavaria ICU': 0,
        'Bavaria Hosp': 1,
        'Bavaria Vax': 0,
    }

    FORMAT_DICT = {
        'Bayern Inc': '%Y-%m-%dT%H:%M:%S.%fZ',
        'München Inc': '%Y-%m-%dT%H:%M:%S.%fZ',
        'Miesbach Inc': '%Y-%m-%dT%H:%M:%S.%fZ',
        'München LK Inc': '%Y-%m-%dT%H:%M:%S.%fZ',
        'Bavaria ICU': '%Y-%m-%d',
        'Bavaria Hosp': '%Y-%m-%dT%H:%M:%S.%fZ',
        'Bavaria Vax': '%Y-%m-%dT%H:%M:%S.%fZ',
    }

    # shift for disctricts = 0
    # shift for bav inc = 1
    def evaluate_freshness(self, date, label):
        try:
            format = self.FORMAT_DICT[label]
            shift = self.SHIFT_DICT[label]
        except:
            shift = 0
            format = '%Y-%m-%dT%H:%M:%S.%fZ'

        timestamp = mytime.string2timestamp(date, time_format=format)
        delta_in_secs = mytime.current_time() - timestamp - 24 * 60 * 60 * shift
        delta_in_hours = round(delta_in_secs / 60 / 60)
        logging.info(f"{label} is {delta_in_hours} hours old")

        if delta_in_hours < 24:
            return Freshness.FRESH
        elif delta_in_hours < 40:
            return Freshness.DAY_OLD
        else:
            return Freshness.OLD

    def freshness_to_grey(self, freshness):
        if freshness.value == 0:
            return Fill.GRAY4
        if freshness.value == 1:
            return Fill.GRAY3
        if freshness.value == 2:
            return Fill.GRAY2
        return Fill.GRAY1

    def help_get_trended_layout(self, text_elements, image_elements, trended_object, label, x, y, show_trend=True):
        inz, freshness, trend = trended_object
        arrow_file = os.path.join(self.resdir, f'covid/{trend}.bmp')
        fill = self.freshness_to_grey(freshness)
        text_elements.append(PaperTextElement(x, y, Alignment.TOP_LEFT, Fill.GRAY4, label, 18))
        if show_trend:
            textx = x + 51
            image_elements.append(PaperImageElement(x, y + 27, Alignment.TOP_LEFT, arrow_file))
        else:
            textx = x
        text_elements.append(PaperTextElement(textx, y + 19, Alignment.TOP_LEFT, fill, str(inz), 56))

        return text_elements, image_elements

    def get_paper_layout(self):
        text_elements = []
        image_elements = []
        # LEFT SIDE
        self.help_get_trended_layout(text_elements, image_elements,
                                     self.get_bavaria_vax(), "Bayern Impfquote:", 10, 10, show_trend=False)
        self.help_get_trended_layout(text_elements, image_elements,
                                     self.get_bavaria_hospital(), "Bayern Cov-19 KH Inz:", 10, 97, show_trend=False)
        self.help_get_trended_layout(text_elements, image_elements,
                                     self.get_bavaria_icu(), "Bayern ICU Fälle:", 10, 184, show_trend=True)

        # MIDDLE
        text_elements.append(PaperTextElement(240, 0, Alignment.TOP_CENTER, Fill.GRAY4, f'{mytime.current_time_hr("%d %b %H:%M")}', 12),)
        ampel_file = os.path.join(self.resdir, f'covid/{self.evaluate_ampel_status().value}')
        image_elements.append(PaperImageElement(240, 140, Alignment.CENTERED, ampel_file))

        # RIGHT SIDE
        self.help_get_trended_layout(text_elements, image_elements,
                                     self.get_munich_inc(), "München Inz:", 293, 10)
        self.help_get_trended_layout(text_elements, image_elements,
                                     self.get_munich_lk_inc(), "München LK Inz:", 293, 97)
        self.help_get_trended_layout(text_elements, image_elements,
                                     self.get_bavaria_inc(), "Bayern Inz:", 293,
                                     184)
        font_path = os.path.join(self.resdir, 'Font.ttc')
        return PaperLayout(Orientation.LANDSCAPE, font_path, text_elements, image_elements, None, None)
