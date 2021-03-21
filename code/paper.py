#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
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


class Paper:
    vac_partial_refresh_pixels = (26, 77, 433, 149)

    def __str__(self):
        return f"Paper class, what should I print?"

    def __init__(self, databook):
        logging.info(f'Init Paper at {mytime.current_time_hr()}')
        self.databook = databook
        self.epd = epd3in7.EPD()

        self.font_huge = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 90)
        self.font_very_big = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 85)
        self.font_big = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 45)
        self.font_medium = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 28)
        self.font_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        self.font_very_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)

    def write_current_time(self, epd, draw):
        string_to_display = f'{mytime.current_time_hr("%H:%M")}+'
        draw.text((0, 0), string_to_display, font=self.font_very_small, fill=epd.GRAY4)
        logging.info(f"Add to screen {string_to_display}")

    def partial_refresh_vac_for(self, duration_secs):
        if not mytime.is_business_hours():
            logging.info(f'Skipping partial refresh because outside business hours {mytime.current_time_hr()}')
            return

        start_time = mytime.current_time()
        epd = self.epd

        try:
            epd.init(1)  # 1 Gary mode
            epd.Clear(0xFF, 1)
            image = Image.new('1', (epd.height, epd.width), 255)
            draw = ImageDraw.Draw(image)
            # Clear area once, so frame buffer works
            draw.rectangle(self.vac_partial_refresh_pixels, fill=0)
            epd.display_1Gray(epd.getbuffer(image))
            draw.rectangle(self.vac_partial_refresh_pixels, fill=255)
            epd.display_1Gray(epd.getbuffer(image))
            # This surely can be optimised. Do we skip the black box? Or the white Box?

            while (int((mytime.current_time() - start_time)) < duration_secs) and not self.cancel_file_exists():
                # get fresh data
                vaccinated_abs = self.databook.get_extrapolated_abs_doses()
                string_2_line = f"{vaccinated_abs[0]}"
                draw.rectangle(self.vac_partial_refresh_pixels, fill=255)
                self.write_just_vac_number(draw, string_2_line)
                epd.display_1Gray(epd.getbuffer(image))
                logging.info(f"PARTIAL {vaccinated_abs[2]}")
            epd.sleep()
        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd3in7.epdconfig.module_exit()
            exit()

    def cancel_file_exists(self):
        if os.path.isfile("/home/pi/partial.cancel"):
            print(f"Cancel file found")
            return True
        return False

    def write_just_vac_number(self, draw, string_2_line):
        # Vaccinations
        draw.text((20, 60), string_2_line, font=self.font_huge, fill=0)

    def maybe_refresh_all_covid_data(self):
        vaccinated_abs = self.databook.get_extrapolated_abs_doses()
        munich_inz = self.databook.get_inz_munich()
        bavaria_inz = self.databook.get_inz_bavaria()
        logging.info(
            f'Got data from databook vaccinated_abs ({vaccinated_abs[0]}, {vaccinated_abs[1]}, ...) munich_inz {munich_inz} bavaria_inz {bavaria_inz}')
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
            image = Image.new('L', (epd.height, epd.width),
                              0xFF)  # 0xFF: clear the frame
            draw = ImageDraw.Draw(image)
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
            image.save(r'image.png')
            epd.display_4Gray(epd.getbuffer_4Gray(image))
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
