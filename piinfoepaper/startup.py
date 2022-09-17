import logging
import os
import sys

import mytime as mytime
from paper_controller import PaperController
from paper_layout import PaperLayout
from paper_elements import PaperTextElement
from paper_enums import Orientation, Alignment, Fill
from welcome.welcome import Welcome
from welcome.technical_info import TechnicalInfo

# supposed to run after plugging in the device. Shows welcome message and technical info.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info(f'## Start Welcome display at {mytime.current_time_hr()}')
    layout = Welcome(15).get_layout()
    paper_controller = PaperController(layout)
