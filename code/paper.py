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


layout = {
    'time': (430, 0),

    'text_vac': (45, 15),
    'num_vac': (20, 35),
    'partial_rect': (13, 52, 423, 124),

    'text_bav_inz': (25 - 18, 170 - 15),
    'arrow_bav_inz': (3, 204),
    'num_bav_inz': (51, 185),

    'text_muc_inz': (278, 170 - 15),
    'arrow_muc_inz': (247, 204),
    'num_muc_inz': (295, 185),

    'line_hor': (0, 150, 480, 150),
    'line_ver': (241, 150, 241, 280),

    'ampel': (100, 100),
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
        self.font_medium = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 52)
        self.font_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        self.font_very_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)

    def cancel_file_exists(self):
        if os.path.isfile("/home/pi/partial.cancel") or os.path.isfile("~/partial.cancel"):
            logging.info(f"Cancel file found")
            return True
        return False

    def write_current_time(self, epd, draw):
        string_to_display = f'{mytime.current_time_hr("%H:%M")}+'
        draw.text(layout['time'], string_to_display, font=self.font_very_small, fill=epd.GRAY4)
        logging.info(f"Add to screen {string_to_display}")


    def help_draw_trended_number(self, image, draw, label, trended_object, x, y):
        # Label
        draw.text((x, y), f'{label}',
                  font=self.font_small, fill=self.epd.GRAY4)
        # Number
        draw.text((x + 55, y + 17), f'{trended_object[0]}',
                  font=self.font_medium, fill=self.epd.GRAY4)

        arrow_file = f'{trended_object[1]}.bmp'
        bmp = Image.open(os.path.join(picdir, arrow_file))
        image.paste(bmp, (x, y + 25))

    def help_draw_generic_info(self, image, draw, label, number, x, y):
        # Label
        draw.text((x, y), f'{label}',
                  font=self.font_small, fill=self.epd.GRAY4)
        # Number
        draw.text((x, y + 17), f'{number}',
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
            self.help_draw_trended_number(image, draw, "München Inz:", self.databook.get_munich_inc(), 300, 15)
            self.help_draw_trended_number(image, draw, "Miesbach Inz:", self.databook.get_miesbach_inc(), 300, 15 + 80)
            self.help_draw_trended_number(image, draw, "Bayern Inz:", self.databook.get_bavaria_inc(), 300, 15 + 2 * 80)

            self.help_draw_generic_info(image, draw, "Bayern Impfquote:", self.databook.get_bavaria_vax(), 15, 15)
            self.help_draw_generic_info(image, draw, "Bayern KH Fälle:", self.databook.get_bavaria_hospital(), 15,
                                        15 + 80)
            self.help_draw_trended_number(image, draw, "Bayern ICU:", self.databook.get_bavaria_icu(), 15,
                                        15 + 2*80)

            # Ampel
            ampel_file = self.databook.evaluate_ampel_status().value[0]
            bmp = Image.open(os.path.join(picdir, ampel_file))
            image.paste(bmp, (194, 20))
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

    def partial_refresh_vac_for(self, duration_secs, clear_vac=True):
        start_time = mytime.current_time()
        epd = self.epd

        try:
            epd.init(1)  # 1 Gary mode
            epd.Clear(0xFF, 1)

            # image = Image.new('1', (epd.height, epd.width), 255)
            #
            # draw = ImageDraw.Draw(image)
            if clear_vac:
                image = Image.new('1', (epd.height, epd.width), 255)
                draw = ImageDraw.Draw(image)
                draw.rectangle(self.partial_rect, fill=0)
                epd.display_1Gray(epd.getbuffer(image))
                draw.rectangle(self.partial_rect, fill=255)
                epd.display_1Gray(epd.getbuffer(image))
            logging.info(f"Doing partial refresh from now on...")
            while (int((mytime.current_time() - start_time)) < duration_secs) and not self.cancel_file_exists():
                image = Image.new('1', (epd.height, epd.width), 255)
                draw = ImageDraw.Draw(image)

                vaccinated_abs = self.databook.get_extrapolated_abs_doses()
                string_2_line = f"{vaccinated_abs[0]}"
                draw.rectangle(self.partial_rect, fill=255)
                draw.text(layout['num_vac'], string_2_line, font=self.font_huge, fill=0)
                if self.flip:
                    image = image.rotate(180, expand=1)
                epd.display_1Gray(epd.getbuffer(image))
                logging.debug(f"PARTIAL {vaccinated_abs[2]}")
            logging.info(f"Stopping partial refresh.")
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

    def maybe_refresh_all_covid_data(self, write_vac=True):
        vaccinated_abs = self.databook.get_extrapolated_abs_doses()
        munich_inz = self.databook.get_inz_munich()
        bavaria_inz = self.databook.get_inz_bavaria()
        logging.info(
            f'Got data from databook vaccinated_abs ({vaccinated_abs[0]}, {vaccinated_abs[1]}, ...) munich_inz {munich_inz} bavaria_inz {bavaria_inz}')
        if (vaccinated_abs[1] or munich_inz[1] or bavaria_inz[1]):
            logging.info(f"Will refresh screen...")
            self.refresh_all_covid_data(self, write_vac)
        else:
            logging.info(f"Data is the same. Skipping Display change")

    def refresh_all_covid_data(self, write_vac=True):
        vaccinated_abs = self.databook.get_extrapolated_abs_doses()
        munich_inz = self.databook.get_inz_munich()
        bavaria_inz = self.databook.get_inz_bavaria()

        self.epd.init(0)
        self.epd.Clear(0xFF, 0)

        string_1_line = f"Verteilte Impfdosen in Bayern"
        string_2_line = f"{vaccinated_abs[0]}"

        string_bottom_left_1 = f"Bayern Inz:"
        arrow_file_bav = f'{bavaria_inz[2]}.bmp'
        string_bottom_left_2 = f"{bavaria_inz[0]}"
        string_bottom_right_1 = f"München Inz:"
        arrow_file_muc = f'{munich_inz[2]}.bmp'
        string_bottom_right_2 = f"{munich_inz[0]}"

        epd = self.epd
        try:
            image = Image.new('L', (epd.height, epd.width),
                              0xFF)  # 0xFF: clear the frame
            draw = ImageDraw.Draw(image)

            self.write_current_time(epd, draw)
            image = self.ampel(image)
            # Vaccinations
            draw.text(layout['text_vac'], string_1_line,
                      font=self.font_medium, fill=epd.GRAY4)
            if write_vac:
                draw.text(layout['num_vac'], string_2_line, font=self.font_huge, fill=0)
            # Inz BY
            draw.text(layout['text_bav_inz'], string_bottom_left_1,
                      font=self.font_medium, fill=epd.GRAY4)
            draw.text(layout['num_bav_inz'], string_bottom_left_2,
                      font=self.font_very_big, fill=epd.GRAY4)
            # arrow
            bmp = Image.open(os.path.join(picdir, arrow_file_bav))
            image.paste(bmp, layout['arrow_bav_inz'])

            # Inz MUC
            draw.text(layout['text_muc_inz'], string_bottom_right_1,
                      font=self.font_medium, fill=epd.GRAY4)
            draw.text(layout['num_muc_inz'], string_bottom_right_2,
                      font=self.font_very_big, fill=epd.GRAY4)
            # arrow
            bmp = Image.open(os.path.join(picdir, arrow_file_muc))
            image.paste(bmp, layout['arrow_muc_inz'])

            # LINES
            # draw.line(layout['line_hor'], fill=0)
            # draw.line(layout['line_ver'], fill=0)

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

    def clear(self):
        self.epd.init(0)
        self.epd.Clear(0xFF, 0)
