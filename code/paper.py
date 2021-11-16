#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import random
import sys
from PIL import Image, ImageDraw, ImageFont
import time
import mytime as mytime
from waveshare_epd import epd3in7
import logging

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

    'inc_muc': (RIGHT_X, PAD),
    'inc_miesbach': (RIGHT_X, PAD + SPACING),
    'inc_bav': (RIGHT_X, PAD + 2 * SPACING),

    'vax_bav': (PAD, PAD),
    'hosp_bav': (PAD, PAD + SPACING),
    'icu_bav': (PAD, PAD + 2 * SPACING),

    'ampel': (194, 20),
}


# Arrow is 48 px. Add 3 px of margin to num

class Paper:

    def __str__(self):
        return f"This is an object of the Paper class."

    def __init__(self, databook, flip=False):
        logging.debug(f'Init Paper at {mytime.current_time_hr()}')
        self.epd = epd3in7.EPD()
        self.flip = flip
        self.databook = databook
        self.partial_rect = (23, 77, 433, 149)
        if self.flip:
            # ToDo: Understand why we put height first then width.
            self.partial_rect = flip_partial(self.partial_rect, self.epd.height, self.epd.width)
        self.font_huge = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 90)
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

    def help_draw_trended_number(self, image, draw, label, trended_object, xy):
        x = xy[0]
        y = xy[1]
        # Label
        draw.text((x, y), f'{label}',
                  font=self.font_small, fill=self.epd.GRAY4)
        # Number
        draw.text((x + 51, y + 19), f'{trended_object[0]}',
                  font=self.font_medium, fill=self.epd.GRAY4)

        arrow_file = f'{trended_object[1]}.bmp'
        bmp = Image.open(os.path.join(picdir, arrow_file))
        image.paste(bmp, (x, y + 27))

    def help_draw_generic_info(self, image, draw, label, number, xy):
        x = xy[0]
        y = xy[1]
        # Label
        draw.text((x, y), f'{label}',
                  font=self.font_small, fill=self.epd.GRAY4)
        # Number
        draw.text((x, y + 19), f'{number}',
                  font=self.font_medium, fill=self.epd.GRAY4)

    def draw_data(self):
        epd = self.epd
        epd.init(0)
        epd.Clear(0xFF, 0)

        self.databook.get_munich_inc()

        try:
            image = Image.new('L', (epd.height, epd.width),
                              0xFF)  # 0xFF: clear the frame
            draw = ImageDraw.Draw(image)

            self.write_current_time(epd, draw)
            # # # # # # # # # # # # #
            self.help_draw_trended_number(image, draw, "München Inz:", self.databook.get_munich_inc(), layout['inc_muc'])
            self.help_draw_trended_number(image, draw, "Miesbach Inz:", self.databook.get_miesbach_inc(), layout['inc_miesbach'])
            self.help_draw_trended_number(image, draw, "Bayern Inz:", self.databook.get_bavaria_inc(), layout['inc_bav'])

            self.help_draw_generic_info(image, draw, "Bayern Impfquote:", self.databook.get_bavaria_vax(), layout['vax_bav'])
            self.help_draw_generic_info(image, draw, "Bayern KH Fälle:", self.databook.get_bavaria_hospital(), layout['hosp_bav'])
            self.help_draw_trended_number(image, draw, "Bayern ICU:", self.databook.get_bavaria_icu(), layout['icu_bav'])

            # Ampel
            ampel_file = self.databook.evaluate_ampel_status().value[0]
            bmp = Image.open(os.path.join(picdir, ampel_file))
            image.paste(bmp, layout['ampel'])
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

    def ampel(self, image):
        ampel_files = ['ampel-red.bmp', 'ampel-yellow.bmp', 'ampel-green.bmp']

        bmp = Image.open(os.path.join(picdir, ampel_files[random.randint(0, 2)]))
        image.paste(bmp, layout['ampel'])
        return image

    def clear(self):
        self.epd.init(0)
        self.epd.Clear(0xFF, 0)
