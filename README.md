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


### Setup
<details><summary>Setup</summary>
<p>

 Use a clean ubuntu installation

 How about upgrading first?

```sh
sudo apt update && sudo apt upgrade
```


```sh
sudo raspi-config
```
-> 3 Interface Options
-> P4 SPI
-> Yes
-> Ok	
-> Finish


```sh
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
tar zxvf bcm2835-1.60.tar.gz 
cd bcm2835-1.60/
sudo ./configure
sudo make
sudo make check
sudo make install
```

```sh
cd ~
sudo apt install wiringpi
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
```

```sh
sudo apt update
sudo apt install -y python-pip python-pil python-numpy
sudo pip install RPi.GPIO spidev

sudo apt update
sudo apt install -y python3-pip python3-pil python3-numpy
sudo pip3 install RPi.GPIO spidev
```

```sh
sudo apt install -y git
```

How about some apt maintenance now?

```sh
sudo apt clean && sudo apt autoclean && sudo apt autoremove
```

If you want to try the waveshare example code first:

```sh
cd ~
git clone https://github.com/waveshare/e-Paper

```
Grab the code from this repo and install dependencies. Install pandas like shown below, it's the easiest solution.

```sh
cd ~
git clone https://github.com/lor-enz/pi-info-epaper
pip3 install pytz
sudo apt install -y python3-pandas
```

Run it with python3

</p>
</details>




## Future uses

The information I want to have displayed is likely to change in the future. Other ideas I have are:

- stock prices
- weather information
- wikipedia article of the day


