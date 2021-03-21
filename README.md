# pi-info-paper

This is a python project running on raspberry pi zero w of mine. The pi has a 3.7 Inch Waveshare e paper (and display controller) attached to it.

The code is intended to run as a cronjob every 10 minutes.
It will download Germanys current information regarding covid-19 infections and vaccinations and display them on the screen. Updating some of it continuously.

It displays:

- Vaccination doses given out in Bavaria. Extrapolated to the current moment according to some assumptions.
- The Inzidenzwert of Bavaria
- The Inzidenzwert of Munich, Bavaria

The information I want to have displayed is likely to change in the future. Other ideas I have are:

- stock prices
- weather information
- wikipedia article of the day

