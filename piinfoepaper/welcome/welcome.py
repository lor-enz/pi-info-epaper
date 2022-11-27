import os
import sys
import logging
import subprocess

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import mytime as mytime
from paper_elements import PaperTextElement, PaperImageElement
from paper_enums import Alignment, Fill, Orientation
from paper_layout import PaperLayout
import time


class Welcome:

    def __init__(self, wait_time_seconds):
        self.resdir = os.path.join(os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))), 'res')  # path next to this file
        if os.path.exists(self.resdir):
            sys.path.append(self.resdir)
        time.sleep(wait_time_seconds)
        self.ip = f"IP: {self.get_host_ip()}"

    def get_host_ip(self):
        return subprocess.getoutput('hostname -I')

    def get_plugmein_layout(self):
        text_elements = [
            PaperTextElement(475, 5, Alignment.TOP_RIGHT, Fill.GRAY4, f'{mytime.current_time_hr("%d %b %H:%M")}', 15),
            PaperTextElement(255, 100, Alignment.LEFT_CENTER, Fill.GRAY4, f'Hello!', 40),
            PaperTextElement(255, 170, Alignment.LEFT_CENTER, Fill.GRAY4, f'Plug me in!', 40),
        ]
        plug_image_file = os.path.join(self.resdir, 'welcome/plug.bmp')
        image_elements = [PaperImageElement(10, 140, Alignment.LEFT_CENTER, plug_image_file)]
        font_path = os.path.join(self.resdir, 'Font.ttc')
        return PaperLayout(Orientation.LANDSCAPE, font_path, text_elements, image_elements, None, None)

    def get_layout(self, plugmein=False):
        if plugmein:
            return self.get_plugmein_layout()
        x = 35
        sp = 38
        text_elements = [
            PaperTextElement(475, 5, Alignment.TOP_RIGHT, Fill.GRAY4, f'{mytime.current_time_hr("%d %b %H:%M")}', 15),
            PaperTextElement(240, x - 10, Alignment.TOP_CENTER, Fill.GRAY4, f'Hello!', 30),
            PaperTextElement(240, x + sp * 1, Alignment.TOP_CENTER, Fill.GRAY4, f'Thanks for using pi-info-epaper!',
                             30),
            PaperTextElement(240, x + sp * 2, Alignment.TOP_CENTER, Fill.GRAY4, f'Wait until the next full hour', 30),
            PaperTextElement(240, x + sp * 3, Alignment.TOP_CENTER, Fill.GRAY4, f'for the screen to change.', 30),
            PaperTextElement(240, 240, Alignment.BOTTOM_CENTER, Fill.GRAY4, f'{self.ip}', 30),

        ]
        image_elements = []
        font_path = os.path.join(self.resdir, 'Font.ttc')
        return PaperLayout(Orientation.LANDSCAPE, font_path, text_elements, image_elements, None, None)
