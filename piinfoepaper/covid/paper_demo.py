#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys

from PIL import Image, ImageDraw, ImageFont
import time
from waveshare_epd import epd3in7
import logging

picdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

logging.basicConfig(level=logging.DEBUG)


class Paper:

    def __init__(self):
        logging.info(f'Init Paper (Demo) at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')

        self.epd = epd3in7.EPD()

        self.font_huge = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 90)
        self.font_very_big = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 85)
        self.font_big = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 45)
        self.font_medium = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 28)
        self.font_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        self.font_very_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)

    def clear(self):
        self.epd.init(0)
        self.epd.Clear(0xFF, 0)

    def ampel(self):
        try:
            logging.info("epd3in7 Demo")

            epd = self.epd
            logging.info("init and Clear")
            epd.init(0)
            epd.Clear(0xFF, 0)

            logging.info("ampel-yellow")
            image = Image.new('1', (epd.height, epd.width),
                                255)  # 255: clear the frame

            resize = (85,141)

            bmp_red = Image.open(os.path.join(picdir, 'ampel-red2.bmp'))
            bmp_red = bmp_red.resize(resize, Image.ANTIALIAS)

            bmp_yellow = Image.open(os.path.join(picdir, 'ampel-yellow2.bmp'))
            bmp_yellow = bmp_yellow.resize(resize, Image.ANTIALIAS)

            bmp_green = Image.open(os.path.join(picdir, 'ampel-green2.bmp'))
            bmp_green = bmp_green.resize(resize, Image.ANTIALIAS)

            image.paste(bmp_red, (0, 70))
            image.paste(bmp_yellow, (160, 70))
            image.paste(bmp_green, (390, 70))

            epd.display_4Gray(epd.getbuffer_4Gray(image))
            time.sleep(5)

            logging.info("Goto Sleep...")
            epd.sleep()

        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd3in7.epdconfig.module_exit()
            exit()

    def demo(self):
        try:
            logging.info("epd3in7 Demo")

            epd = self.epd
            logging.info("init and Clear")
            epd.init(0)
            epd.Clear(0xFF, 0)

            font36 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36)
            font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
            font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

            # Drawing on the Horizontal image
            logging.info("1.Drawing on the Horizontal image...")
            image = Image.new('L', (epd.height, epd.width),
                               0xFF)  # 0xFF: clear the frame
            draw = ImageDraw.Draw(image)
            draw.text((10, 0), 'hello world', font=font24, fill=0)
            draw.text((10, 20), '3.7inch e-Paper', font=font24, fill=0)
            draw.rectangle((10, 110, 154, 146), 'black', 'black')
            draw.text((10, 110), u'Penguin', font=font36, fill=epd.GRAY1)
            draw.text((10, 150), u'Penguin', font=font36, fill=epd.GRAY2)
            draw.text((10, 190), u'Penguin', font=font36, fill=epd.GRAY3)
            draw.text((10, 230), u'Penguin', font=font36, fill=epd.GRAY4)
            draw.line((20, 50, 70, 100), fill=0)
            draw.line((70, 50, 20, 100), fill=0)
            draw.rectangle((20, 50, 70, 100), outline=0)
            draw.line((165, 50, 165, 100), fill=0)
            draw.line((140, 75, 190, 75), fill=0)
            draw.arc((140, 50, 190, 100), 0, 360, fill=0)
            draw.rectangle((80, 50, 130, 100), fill=0)
            draw.chord((200, 50, 250, 100), 0, 360, fill=0)
            epd.display_4Gray(epd.getbuffer_4Gray(image))
            time.sleep(5)

            logging.info("2.read 4 Gray bmp file")
            image = Image.open(os.path.join(picdir, '3in7_4gray2.bmp'))
            epd.display_4Gray(epd.getbuffer_4Gray(image))
            time.sleep(5)

            logging.info("3.read bmp file on window")
            image2 = Image.new('1', (epd.height, epd.width),
                                255)  # 255: clear the frame
            bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
            image2.paste(bmp, (200, 50))
            epd.display_4Gray(epd.getbuffer_4Gray(image2))
            time.sleep(5)

            # Drawing on the Vertical image
            logging.info("4.Drawing on the Vertical image...")
            l_image = Image.new('L', (epd.width, epd.height),
                               0xFF)  # 0xFF: clear the frame
            draw = ImageDraw.Draw(l_image)
            draw.text((2, 0), 'hello world', font=font18, fill=0)
            draw.text((2, 20), '3.7inch epd', font=font18, fill=0)
            draw.rectangle((130, 20, 274, 56), 'black', 'black')
            draw.text((130, 20), u'Penguin', font=font36, fill=epd.GRAY1)
            draw.text((130, 60), u'Penguin', font=font36, fill=epd.GRAY2)
            draw.text((130, 100), u'Penguin', font=font36, fill=epd.GRAY3)
            draw.text((130, 140), u'Penguin', font=font36, fill=epd.GRAY4)
            draw.line((10, 90, 60, 140), fill=0)
            draw.line((60, 90, 10, 140), fill=0)
            draw.rectangle((10, 90, 60, 140), outline=0)
            draw.line((95, 90, 95, 140), fill=0)
            draw.line((70, 115, 120, 115), fill=0)
            draw.arc((70, 90, 120, 140), 0, 360, fill=0)
            draw.rectangle((10, 150, 60, 200), fill=0)
            draw.chord((70, 150, 120, 200), 0, 360, fill=0)
            epd.display_4Gray(epd.getbuffer_4Gray(l_image))
            time.sleep(5)

            # partial update, just 1 Gary mode
            logging.info("5.show time, partial update, just 1 Gary mode")
            epd.init(1)  # 1 Gary mode
            epd.Clear(0xFF, 1)
            time_image = Image.new('1', (epd.height, epd.width), 255)
            time_draw = ImageDraw.Draw(time_image)
            num = 0
            while True:
                time_draw.rectangle((10, 10, 120, 50), fill=255)
                time_draw.text((10, 10), time.strftime(
                    '%H:%M:%S'), font=font24, fill=0)
                epd.display_1Gray(epd.getbuffer(time_image))

                num = num + 1
                if num == 20:
                    break

            logging.info("Clear...")
            epd.init(0)
            epd.Clear(0xFF, 0)

            logging.info("Goto Sleep...")
            epd.sleep()

        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd3in7.epdconfig.module_exit()
            exit()