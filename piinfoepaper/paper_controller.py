#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import random
import sys
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
import time
import mytime as mytime
from paper_elements import PaperTextElement, PaperImageElement
from paper_layout import PaperLayout
from paper_enums import Alignment, Fill

from waveshare_epd import epd3in7
import logging


class PaperController:

    def __init__(self, paper_layout: PaperLayout):
        logging.debug(f'Init Paper at {mytime.current_time_hr()}')
        self.paper_layout = paper_layout
        self.font_path = paper_layout.font_path
        self.epd = epd3in7.EPD()
        self.debug = False
        self.paper_image = Image.new('L', (self.epd.height, self.epd.width), 0xFF)
        self.draw = ImageDraw.Draw(self.paper_image)
        self.draw_data()

    def cancel_file_exists(self):
        if os.path.isfile("/home/pi/partial.cancel") or os.path.isfile("~/partial.cancel"):
            logging.info(f"Cancel file found")
            return True
        return False

    def debug_rectangle(self, x, y, width, height):
        if self.debug:
            self.draw.rectangle((x, y, x + width, y + height), outline=0)

    def draw_image(self, el: PaperImageElement):
        icon = Image.open(el.image_path)
        width, height = icon.size
        x, y = self.calc_pos_from_alignment(el.xy, el.alignment, width, height)
        logging.info(f"draw_image: \'{el.image_path}\' at ({x}, {y})")
        self.paper_image.paste(icon, (x, y))
        self.debug_rectangle(x, y, width, height)

    def draw_text(self, el: PaperTextElement):
        font = ImageFont.truetype(self.font_path, el.font_size)
        (width, height) = font.getsize(el.text)
        x, y = self.calc_pos_from_alignment(el.xy, el.alignment, width, height)
        logging.info(f"draw_text: size {el.font_size} \'{el.text}\' at ({x}, {y})")
        self.draw.text((x, y), f'{el.text}', font=font, fill=self.fill2grey(el.fill))
        self.debug_rectangle(x, y, width, height)

    def calc_pos_from_alignment(self, xy, alignment, width, height):
        if alignment.value == Alignment.TOP_LEFT.value:
            x = int(xy[0])
            y = int(xy[1])
        elif alignment.value == Alignment.TOP_RIGHT.value:
            x = int(xy[0] - width)
            y = int(xy[1])
        elif alignment.value == Alignment.BOTTOM_LEFT.value:
            x = int(xy[0])
            y = int(xy[1] - height)
        elif alignment.value == Alignment.BOTTOM_RIGHT.value:
            x = int(xy[0] - width)
            y = int(xy[1] - height)
        elif alignment.value == Alignment.CENTERED.value:
            x = int(xy[0] - width / 2)
            y = int(xy[1] - height / 2)
        elif alignment.value == Alignment.BOTTOM_CENTER.value:
            x = int(xy[0] - width / 2)
            y = int(xy[1] - height)
        elif alignment.value == Alignment.TOP_CENTER.value:
            x = int(xy[0] - width / 2)
            y = int(xy[1])
        else:
            logging.error(f"Failed to match alignment:{alignment} w:{width} h:{height} ")
        return x, y

    def draw_data(self):
        try:
            self.clear()

            self.paper_image = Image.new('L', (self.epd.height, self.epd.width), 0xFF)
            self.draw = ImageDraw.Draw(self.paper_image)
            logging.info(f"Drawing {len(self.paper_layout.text_elements)} text elements"
                         f" and {len(self.paper_layout.image_elements)} image elements...")
            for el in self.paper_layout.text_elements:
                try:
                    self.draw_text(el)
                except IOError as e:
                    logging.info(f"Error drawing text")
                    logging.error(e)

            for el in self.paper_layout.image_elements:
                try:
                    self.draw_image(el)
                except IOError as e:
                    logging.info(f"Error drawing image: {el}")
                    logging.error(e)

            # # # # # # # # # # # # #
            # save as file, maybe flip, then push to display
            self.paper_image.save(r'/home/pi/image.png')
            # TODO switch case Orientation and so on...
            # self.paper_image = self.paper_image.transpose(Image.ROTATE_180)

            self.epd.display_4Gray(self.epd.getbuffer_4Gray(self.paper_image))
            self.epd.sleep()


        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd3in7.epdconfig.module_exit()
            exit()

    def fill2grey(self, fill: Fill):
        if fill.value == Fill.GRAY4.value:
            return self.epd.GRAY4
        elif fill.value == Fill.GRAY3.value:
            return self.epd.GRAY3
        elif fill.value == Fill.GRAY2.value:
            return self.epd.GRAY2
        elif fill.value == Fill.GRAY1.value:
            return self.epd.GRAY1
        else:
            logging.error(f"Failed to match Fill to Grey Fill:{fill}")
            return self.epd.GRAY4

    def clear(self):
        self.epd.init(0)
        self.epd.Clear(0xFF, 0)
