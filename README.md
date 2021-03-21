# pi-info-paper

This is a python project running on raspberry pi zero w of mine. The pi has a 3.7 Inch Waveshare e paper (and display controller) attached to it.

The code is intended to run as a cronjob every 10 minutes.
It will download Germanys current information regarding covid-19 infections and vaccinations and display them on the screen. Updating some of it continuously.
I put it up on the fridge in my kitchen which makes for a convenient way to get a sense for the numbers.

## What it displays

![pi-info-epaper](https://user-images.githubusercontent.com/33176142/111890186-6d5a0980-89e7-11eb-8aa8-7fe316021a20.jpg)

- Vaccination doses given out in Bavaria. Extrapolated to the current moment according to some assumptions.
- The Inzidenzwert of Bavaria
- The Inzidenzwert of Munich, Bavaria

## About the code

### waveshare e-paper

The code for driving the e-paper is oriented around the official documentation from
[github.com/waveshare/e-Paper](https://github.com/waveshare/e-Paper) and the [waveshare e-paper wiki page](https://www.waveshare.com/wiki/3.7inch_e-Paper_HAT)

### My code

The code style isn't the best since I haven't written python code in years. But I'm doing my best to improve it!

## Future uses

The information I want to have displayed is likely to change in the future. Other ideas I have are:

- stock prices
- weather information
- wikipedia article of the day


