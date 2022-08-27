#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import random
import sys
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
import time
import piinfoepaper.mytime as mytime
from waveshare_epd import epd3in7
import logging
from databook import Databook

picdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)


def flip_partial(partial, paper_w, paper_h):
    if len(partial) == 2:
        return paper_w - partial[0], paper_h - partial[1]
    elif len(partial) == 4:
        new_x_e = paper_w - partial[0]
        new_y_e = paper_h - partial[1]
        new_x_s = paper_w - partial[2]
        new_y_s = paper_h - partial[3]
        return new_x_s, new_y_s, new_x_e, new_y_e


class Alignment(Enum):
    TOP_LEFT = 0,
    TOP_RIGHT = 1,
    CENTERED = 2


class Fill(Enum):
    GRAY1 = 1,
    GRAY2 = 2,
    GRAY3 = 3,
    GRAY4 = 4,


layout_landscape = {
    # x- position, y-position, alignment, fontsize
    'time': (480, 0, Alignment.TOP_RIGHT, 12),
    'weekday': (125, 55, Alignment.CENTERED, 80),
    'day_date': (125, 125, Alignment.CENTERED, 45),
    'temp_min': (110, 210, Alignment.CENTERED, 80),
    'temp_max': (480 - 110, 210, Alignment.CENTERED, 80),
    'dash': (240, 210, Alignment.CENTERED, 80),
    'icon1': (405 - 128, 90, Alignment.CENTERED, 0),
    'icon2': (405, 90, Alignment.CENTERED, 0),
    'one_icon': (341, 90, Alignment.CENTERED, 0),
}

layout_portrait = {
    # x- position, y-position, alignment, fontsize
    'time': (0, 0, Alignment.TOP_RIGHT, 12),
    'weekday': (0, 0, Alignment.CENTERED, 80),
    'day_date': (0, 0, Alignment.CENTERED, 45),
    'temp_min': (0, 0, Alignment.CENTERED, 80),
    'temp_max': (0, 0, Alignment.CENTERED, 80),
    'dash': (0, 0, Alignment.CENTERED, 80),
    'icon1': (0, 0, Alignment.CENTERED, 0),
    'icon2': (0, 0, Alignment.CENTERED, 0),
    'one_icon': (0, 0, Alignment.CENTERED, 0),
}

layout = layout_landscape


class Paper:

    def __str__(self):
        return f"This is an object of the Paper class."

    def __init__(self, databook: Databook, flip=False, debug=False):
        logging.debug(f'Init Paper at {mytime.current_time_hr()}')
        self.epd = epd3in7.EPD()
        self.flip = flip
        self.debug = debug
        self.databook = databook
        self.paper_image = Image.new('L', (self.epd.height, self.epd.width), 0xFF)
        self.draw = ImageDraw.Draw(self.paper_image)

    def cancel_file_exists(self):
        if os.path.isfile("/home/pi/partial.cancel") or os.path.isfile("~/partial.cancel"):
            logging.info(f"Cancel file found")
            return True
        return False

    def draw_weather_icon(self, icon_nr, lay):
        if 10 <= icon_nr <= 31:
            img_file = f'weather/{icon_nr}.bmp'
        elif 1 <= icon_nr <= 9:
            img_file = f'weather/0{icon_nr}.bmp'
        else:
            img_file = f'weather/00.bmp'

        self.draw_image(img_file, lay)

    def draw_image(self, img_filename, lay):
        icon = Image.open(os.path.join(picdir, img_filename))
        width, height = icon.size
        x, y = self.calc_pos_from_alignment(lay, width, height)
        self.paper_image.paste(icon, (x, y))

    def draw_text(self, text, lay, fill=Fill.GRAY4):
        font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), lay[3])
        (width, height) = font.getsize(text)
        x, y = self.calc_pos_from_alignment(lay, width, height)

        logging.info(f"Drawing size {lay[3]} \'{text}\' at ({x}, {y})")
        # Label
        self.draw.text((x, y), f'{text}', font=font, fill=self.fill2grey(fill))
        if self.debug:
            self.draw.rectangle((20, 50, 70, 100), outline=0)

    def calc_pos_from_alignment(self, lay, width, height):
        if lay[2] == Alignment.TOP_LEFT:
            x = int(lay[0])
            y = int(lay[1])
        elif lay[2] == Alignment.TOP_RIGHT:
            x = int(lay[0] - width)
            y = int(lay[1])
        elif lay[2] == Alignment.CENTERED:
            x = int(lay[0] - width / 2)
            y = int(lay[1] - height / 2)
        return x, y

    def draw_data(self):

        self.epd.init(0)
        self.epd.Clear(0xFF, 0)

        try:
            self.paper_image = Image.new('L', (self.epd.height, self.epd.width), 0xFF)
            self.draw = ImageDraw.Draw(self.paper_image)
            # Current time - small in the corner
            self.draw_text(f'{mytime.current_time_hr("%d %b %H:%M")}', layout['time'])
            # # # # # # # # # # # # #
            # DAY
            self.draw_text(self.databook.get_day_of_week(), layout['weekday'])
            self.draw_text(self.databook.get_pretty_date(), layout['day_date'])

            # ICONS
            if self.databook.are_icons_different():
                self.draw_weather_icon(self.databook.get_icon1(), layout['icon1'])
                self.draw_weather_icon(self.databook.get_icon2(), layout['icon2'])
            else:
                self.draw_weather_icon(self.databook.get_icon1(), layout['one_icon'])
            # TEMP
            self.draw_text(self.databook.get_temp_min(), layout['temp_min'])
            self.draw_text("-", layout['dash'], fill=Fill.GRAY3)
            self.draw_text(self.databook.get_temp_max(), layout['temp_max'])

            # # # # # # # # # # # # #
            # save as file, maybe flip, then push to display
            self.paper_image.save(r'image.png')
            if self.flip:
                self.paper_image = self.paper_image.transpose(Image.ROTATE_180)
            self.epd.display_4Gray(self.epd.getbuffer_4Gray(self.paper_image))
            self.epd.sleep()
        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd3in7.epdconfig.module_exit()
            exit()

    def fill2grey(self, fill: Fill):
        if fill == Fill.GRAY4:
            return self.epd.GRAY4
        elif fill == Fill.GRAY3:
            return self.epd.GRAY3
        elif fill == Fill.GRAY2:
            return self.epd.GRAY2
        else:
            return self.epd.GRAY1

    def freshness_to_grey(self, freshness):
        if (freshness.value == 0):
            return self.epd.GRAY4
        if (freshness.value == 1):
            return self.epd.GRAY3
        if (freshness.value == 2):
            return self.epd.GRAY2
        return self.epd.GRAY1

    def clear(self):
        self.epd.init(0)
        self.epd.Clear(0xFF, 0)
