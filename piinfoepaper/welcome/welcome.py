import os
import sys
import logging

import piinfoepaper.mytime as mytime
from piinfoepaper.paper_elements import PaperTextElement, PaperImageElement
from piinfoepaper.paper_enums import Alignment, Fill, Orientation
from piinfoepaper.paper_layout import PaperLayout
from piinfoepaper.welcome.technical_info import TechnicalInfo


class Welcome:

    def __init__(self):
        self.resdir = os.path.join(os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))), 'res')  # path next to this file
        if os.path.exists(self.resdir):
            sys.path.append(self.resdir)

        info = TechnicalInfo()
        self.ip = info.local_ip

    def get_layout(self):
        x = 35
        sp = 38
        text_elements = [
            PaperTextElement(475, 5, Alignment.TOP_RIGHT, Fill.GRAY4, f'{mytime.current_time_hr("%d %b %H:%M")}', 15),
            PaperTextElement(240, x-10, Alignment.TOP_CENTER, Fill.GRAY4, f'Hello!', 30),
            PaperTextElement(240, x+sp*1, Alignment.TOP_CENTER, Fill.GRAY4, f'Thanks for using pi-info-epaper!', 30),
            PaperTextElement(240, x+sp*2, Alignment.TOP_CENTER, Fill.GRAY4, f'Wait until the next full hour', 30),
            PaperTextElement(240, x+sp*3, Alignment.TOP_CENTER, Fill.GRAY4, f'for the screen to change.', 30),
            PaperTextElement(240, 240, Alignment.BOTTOM_CENTER, Fill.GRAY4, f'{self.ip}', 30),

        ]
        image_elements = []
        font_path = os.path.join(self.resdir, 'Font.ttc')
        return PaperLayout(Orientation.LANDSCAPE, font_path, text_elements, image_elements, None, None)
