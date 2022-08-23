#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import random
import sys
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



SPACING = 87
VERTICAL_PAD = 10
PAD = 10
RIGHT_X = 293
layout = {
    'time': (194, 0),
    'weekday': (125, 80),
    'temp_min': (110, 210),
    'temp_max': (480-110, 210),
    'dash': (240, 210),
    'icon1': (405-128, 90),
    'icon2': (405, 90),
    'one_icon': (341, 90),
    'center': (240, 140)
}


# Arrow is 48 px. Add 3 px of margin to num

class Paper:

    def __str__(self):
        return f"This is an object of the Paper class."

    def __init__(self, databook: Databook, flip=False):
        logging.debug(f'Init Paper at {mytime.current_time_hr()}')
        self.epd = epd3in7.EPD()
        self.flip = flip
        self.databook = databook
        self.font_huge = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 80)
        self.font_very_big = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 70)
        self.font_big = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 45)
        self.font_medium = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 56)
        self.font_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        self.font_very_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)

    def cancel_file_exists(self):
        if os.path.isfile("/home/pi/partial.cancel") or os.path.isfile("~/partial.cancel"):
            logging.info(f"Cancel file found")
            return True
        return False

    def write_current_time(self, epd, draw):
        string_to_display = f'{mytime.current_time_hr("%d %b %H:%M")}'
        draw.text(layout['time'], string_to_display, font=self.font_very_small, fill=epd.GRAY4)
        logging.info(f"Add to screen {string_to_display}")

    def help_draw_icon_centered(self, image, icon_nr, xy):
        if icon_nr > 31 or icon_nr < 1:
            img_file = f'weather/00.bmp'
        elif icon_nr > 0 and icon_nr < 10:
            img_file = f'weather/0{icon_nr}.bmp'
        else:
            img_file = f'weather/{icon_nr}.bmp'
        bmp = Image.open(os.path.join(picdir, img_file))
        (width, height) = (128,128)
        image.paste(bmp, (int(xy[0]-width/2), int(xy[1]-height/2)))

    def help_draw_text_centered(self, draw, text, xy, font):
        (width, height) = font.getsize(text)
        x = int(xy[0]- width/2)
        y = int(xy[1] - height / 2)

        logging.info(f"Drawing \'{text}\' at ({x}, {y})")
        # Label
        draw.text((x, y), f'{text}', font=font, fill=self.epd.GRAY4)

    def draw_data(self):
        epd = self.epd
        epd.init(0)
        epd.Clear(0xFF, 0)

        try:
            image = Image.new('L', (epd.height, epd.width), 0xFF)
            draw = ImageDraw.Draw(image)
            self.write_current_time(epd, draw)
            # # # # # # # # # # # # #
            # DAY
            self.help_draw_text_centered(draw, self.databook.get_day_of_week(), layout['weekday'], font=self.font_huge)
            # ICONS
            # icon1, icon2 = self.databook.get_random_icons()
            # self.help_draw_icon_centered(image, icon1, layout['icon1'])
            # self.help_draw_icon_centered(image, icon2, layout['icon2'])
            if self.databook.are_icons_different():
                self.help_draw_icon_centered(image, self.databook.get_icon1(), layout['icon1'])
                self.help_draw_icon_centered(image, self.databook.get_icon2(), layout['icon2'])
            else:
                self.help_draw_icon_centered(image, self.databook.get_icon1(), layout['one_icon'])
            # TEMP
            self.help_draw_text_centered(draw, self.databook.get_temp_min(), layout['temp_min'], font=self.font_huge)
            self.help_draw_text_centered(draw, "-", layout['dash'], font=self.font_huge)
            self.help_draw_text_centered(draw, self.databook.get_temp_max(), layout['temp_max'], font=self.font_huge)




            # # # # # # # # # # # # #
            # save as file, maybe flip, then push to display
            image.save(r'image.png')
            if self.flip:
                image = image.transpose(Image.ROTATE_180)
            epd.display_4Gray(epd.getbuffer_4Gray(image))
            epd.sleep()
        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd3in7.epdconfig.module_exit()
            exit()


    ##
        # # Label
        # draw.text((x, y), f'{label}',
        #           font=self.font_small, fill=self.epd.GRAY4)
        # # Number
        # number = "?" if trended_object[0] < 0 else f"{trended_object[0]}"
        # draw.text((x + 51, y + 19), number,
        #           font=self.font_medium, fill=self.freshness_to_grey(trended_object[2]))
        #
        # arrow_file = f'{trended_object[1]}.bmp'
        # bmp = Image.open(os.path.join(picdir, arrow_file))
        # image.paste(bmp, (x, y + 27))

    ##

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
