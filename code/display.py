#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
picdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from PIL import Image, ImageDraw, ImageFont
from covid import Databook
import traceback
import time
from waveshare_epd import epd3in7
import logging

logging.basicConfig(level=logging.DEBUG)

class InfoScreen():

    vacc_partial_refresh_pixels = (26, 77, 433, 149)

    def __str__(self):
        return f"Infoscreen class, what should I print?"

    def __init__(self):
        logging.info(f'Init InfoScreen at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
        self.databook = Databook()

        self.epd = epd3in7.EPD()       

        self.font_huge = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 90)
        self.font_very_big = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'),85)
        self.font_big = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 45)
        self.font_medium = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 28)
        self.font_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        self.font_very_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)

    def write_current_time(self, epd, draw):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        string_to_display = f"Last change at: {current_time}"
        draw.text((0, 0), string_to_display, font=self.font_very_small, fill=epd.GRAY4)
        logging.info(f"Add to screen {string_to_display}")

    def partial_refresh_vacc_for_minutes(self, minutes):
        if not self.databook.is_business_hours():
            logging.info(f"Skipping partial refresh because outside business hours")
            return

        start_time = time.time()
        epd = self.epd
        
        try:
            epd.init(1)         # 1 Gary mode
            epd.Clear(0xFF, 1)
            image = Image.new('1', (epd.height, epd.width), 255)
            draw = ImageDraw.Draw(image)
            num = 0
            # Clear area once, so framebuffer works?
            draw.rectangle(self.vacc_partial_refresh_pixels, fill=0)
            epd.display_1Gray(epd.getbuffer(image))
            draw.rectangle(self.vacc_partial_refresh_pixels, fill=255)
            epd.display_1Gray(epd.getbuffer(image))
            
            while (True):
                # get fresh data
                vaccinated_abs = self.databook.get_extrapolated_abs_doses()
                string_2_line = f"{vaccinated_abs[0]}"
                
                #draw.rectangle(self.vacc_partial_refresh_pixels, fill=0)
                #epd.display_1Gray(epd.getbuffer(image))
                draw.rectangle(self.vacc_partial_refresh_pixels, fill=255)
                self.write_just_vac_number(draw, string_2_line)
                epd.display_1Gray(epd.getbuffer(image))
                logging.info(f"PARTIAL {vaccinated_abs[0]}")
                current_time = time.time()
                if(int((current_time - start_time) / 60) >= minutes) or self.cancel_file_exists():
                    break
            epd.sleep()
        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd3in7.epdconfig.module_exit()
            exit()

    def cancel_file_exists(self):
        x= os.path.isfile("/home/pi/partial.cancel")
        if (x):
            print(f"Cancel file found")
        return x

    def write_just_vac_number(self, draw, string_2_line):
        # Vaccinations
        draw.text((20, 60), string_2_line,font=self.font_huge, fill=0)

    def maybe_refresh_all_covid_data(self):

        vaccinated_abs = self.databook.get_extrapolated_abs_doses()
        munich_inz = self.databook.get_inz_munich()
        bavaria_inz = self.databook.get_inz_bavaria()
        logging.info(f'Got data from databook vaccinated_abs {vaccinated_abs} munich_inz {munich_inz} bavaria_inz {bavaria_inz}')
        if not (vaccinated_abs[1] or munich_inz[1] or bavaria_inz[1]):
            # No changes
            logging.info(f"Data is the same. Skipping Display change")
            return
        logging.info(f"Will refresh screen...")
        self.epd.init(0)
        self.epd.Clear(0xFF, 0)
        
        string_1_line = f"Verteilte Impfdosen in Bayern"
        string_2_line = f"{vaccinated_abs[0]}"

        string_bottom_left_1 = f"Bayern Inz:"
        string_bottom_left_2 = f"{bavaria_inz[0]}"
        string_bottom_right_1 = f"München Inz:"
        string_bottom_right_2 = f"{munich_inz[0]}"
        

        epd = self.epd
        try:
            Himage = Image.new('L', (epd.height, epd.width),
                               0xFF)  # 0xFF: clear the frame
            draw = ImageDraw.Draw(Himage)
            self.write_current_time(epd, draw)
            
            # Vaccinations
            draw.text((20, 40), string_1_line,
                      font=self.font_medium, fill=epd.GRAY4)
            self.write_just_vac_number(draw, string_2_line)
            # Inz BY
            draw.text((20, 170), string_bottom_left_1,
                      font=self.font_medium, fill=epd.GRAY4)
            draw.text((20, 190), string_bottom_left_2,
                      font=self.font_very_big, fill=epd.GRAY4)

            # Inz MUC
            draw.text((293, 170), string_bottom_right_1,
                      font=self.font_medium, fill=epd.GRAY4)
            draw.text((293, 190), string_bottom_right_2,
                      font=self.font_very_big, fill=epd.GRAY4)

            # push to display
            Himage.save(r'image.png')
            epd.display_4Gray(epd.getbuffer_4Gray(Himage))
            epd.sleep()
        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd3in7.epdconfig.module_exit()
            exit()

    def clear(self):
        self.epd.init(0)
        self.epd.Clear(0xFF, 0)

    def demo(self):
        try:
            logging.info("epd3in7 Demo")

            epd = epd3in7.EPD()
            logging.info("init and Clear")
            epd.init(0)
            epd.Clear(0xFF, 0)

            font36 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36)
            font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
            font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

            # Drawing on the Horizontal image
            logging.info("1.Drawing on the Horizontal image...")
            Himage = Image.new('L', (epd.height, epd.width),
                               0xFF)  # 0xFF: clear the frame
            draw = ImageDraw.Draw(Himage)
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
            epd.display_4Gray(epd.getbuffer_4Gray(Himage))
            time.sleep(5)

            logging.info("2.read 4 Gray bmp file")
            Himage = Image.open(os.path.join(picdir, '3in7_4gray2.bmp'))
            epd.display_4Gray(epd.getbuffer_4Gray(Himage))
            time.sleep(5)

            logging.info("3.read bmp file on window")
            Himage2 = Image.new('1', (epd.height, epd.width),
                                255)  # 255: clear the frame
            bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
            Himage2.paste(bmp, (200, 50))
            epd.display_4Gray(epd.getbuffer_4Gray(Himage2))
            time.sleep(5)

            # Drawing on the Vertical image
            logging.info("4.Drawing on the Vertical image...")
            Limage = Image.new('L', (epd.width, epd.height),
                               0xFF)  # 0xFF: clear the frame
            draw = ImageDraw.Draw(Limage)
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
            epd.display_4Gray(epd.getbuffer_4Gray(Limage))
            time.sleep(5)

            # partial update, just 1 Gary mode
            logging.info("5.show time, partial update, just 1 Gary mode")
            epd.init(1)         # 1 Gary mode
            epd.Clear(0xFF, 1)
            time_image = Image.new('1', (epd.height, epd.width), 255)
            time_draw = ImageDraw.Draw(time_image)
            num = 0
            while (True):
                time_draw.rectangle((10, 10, 120, 50), fill=255)
                time_draw.text((10, 10), time.strftime(
                    '%H:%M:%S'), font=font24, fill=0)
                epd.display_1Gray(epd.getbuffer(time_image))

                num = num + 1
                if(num == 20):
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

screen = InfoScreen()
screen.maybe_refresh_all_covid_data()
#screen.clear()
screen.partial_refresh_vacc_for_minutes(9)
