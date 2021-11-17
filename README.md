# pi-info-paper

This is a python project running on a raspberry pi zero w of mine. The pi has a 3.7 Inch Waveshare e paper (and display controller) attached to it.

The code is intended to run as a cronjob every 10 minutes.
It will download Germanys current information regarding covid-19 infections and vaccinations and display them on the screen. 
I put it up on the fridge in my kitchen which makes for a convenient way to get a sense for the numbers.

## What is does
It displays information on the current covid-19 situation in Bavaria and Munich.

![paper-showcase-ampel](https://user-images.githubusercontent.com/33176142/142193751-604a572e-98f0-4e7e-89c7-a93ce78e3332.jpg)


- Percentage of fully vaccinated people in bavaria
- Number of hospitalized people in bavaria
- Number of patients in intensiv care in bavaria
- The 7 days Incidence* of Munich, Bavaria 
- The 7 days Incidence* of Miesbach, Bavaria 
- The 7 days Incidence* of Bavaria 

&ast; 7 days Incidence is the number of new infections in the last 7 days per 100k people

### Previous version with constantly updating screen (gif)

![paper-vax-update-showcase](https://user-images.githubusercontent.com/33176142/142194954-c7d4dd77-aa9f-4d4d-9a38-d57d85000496.gif)

This is an older software version that estimated how many vaccine doses would be given out on a day and would update the number as fast as the screen allows it (~every 5 seconds).

It also shows a nice 3D printed case for the screen, adapter and pizero I designed myself :)

## Technologies and setup


### Hardware 

The hardware probably costs less than 50€ 

- **[Raspberry Pi zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)** with pins

- **[Waveshare 3.7inch e-Paper e-Ink Display HAT For Raspberry Pi, 480*280, Black / White, 4 Grey Scales](https://www.aliexpress.com/item/1005001408167714.html?spm=a2g0s.9042311.0.0.1e2b4c4dAKdgvw)** The HAT is the easy solution with the e-paper and controller combined into one element.
*Alternatively* get the e-paper and the controller separately. This allows the e-paper being flat against a surface. The combined element with the Raspi is 2cm thick. The combined element is easier to set up since it fits together snuggly :)

- *Alternative:* **[Waveshare 3.7inch e-Paper e-Ink Raw Display with 480×280 Resolution Black/White 4 Grey Scales ](https://www.aliexpress.com/item/1005001587973205.html?spm=a2g0s.9042311.0.0.1e2b4c4dAKdgvw)**
 and separate **[Universal e-Paper Raw Panel Driver HAT SPI for Waveshare Various E-ink Module](https://www.aliexpress.com/item/32834283583.html?spm=a2g0s.9042311.0.0.1e2b4c4dAKdgvw)**

- **A micro SD card with 4GB in size or larger**

- **A micro USB cable and somewhere to plug it into**

### Software

The code for driving the e-paper is oriented around the official documentation from
[github.com/waveshare/e-Paper](https://github.com/waveshare/e-Paper) and the [waveshare e-paper wiki page](https://www.waveshare.com/wiki/3.7inch_e-Paper_HAT)



My code may be a bit messy in some parts, since I wrote this after a long break of coding with python. But it's good enough for a hobby project I guess?


### Setup

Setup the raspi for the waveshare hardware, by following the instructions on the [waveshare e-paper wiki page](https://www.waveshare.com/wiki/3.7inch_e-Paper_HAT) which is always up to date or follow the same instructions here with minor changes and comments. Maybe follow along both? ;)

<details><summary>Configure the raspi for the waveshare hardware and code</summary>
<p>

 Use a clean ubuntu installation and setup headless wifi for easy access over ssh.

 Upgrading sounds like a good first thing to do!

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

Also set the **timezone** of the raspberry py to Germanys timezone. While in ```sudo raspi-config``` set it to Europe/Berlin

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
if gpio shows a version number it's installed correctly :)

```sh
sudo apt update
sudo apt install -y python-pip python-pil python-numpy
sudo pip install RPi.GPIO spidev

sudo apt update
sudo apt install -y python3-pip python3-pil python3-numpy
sudo pip3 install RPi.GPIO spidev
```

How about some apt maintenance now?

```sh
sudo apt clean && sudo apt autoclean && sudo apt autoremove
```


Lastly install git to clone this or the official repo.
```sh
sudo apt install -y git
```

You can try the waveshare example code if you want. It has some nice demo code. Instructions and code are on their [github page](https://github.com/waveshare/e-Paper) .

</p>
</details>

<details><summary>Setting up my code</summary>
<p>

The following commaned clones this repo and installs dependencies. I recommend installing pandas like shown below with *apt*. Other ways (pip or conda) will probably lead to issues.

```sh
cd ~
git clone https://github.com/lor-enz/pi-info-epaper
pip3 install pytz
sudo apt install -y python3-pandas
```

figure out where your python3 is install with ```which python3``` and where you cloned the repo. 
Then adapt the script.sh in the root folder of this repo if necessary. 
Run it to see if it's working. You might need to cancel the Partial Update with Ctrl+C since it run for about 9 minutes.

Create a logfile by runnning ```touch ~/info-screen.log```

then configure a cronjob by by running ```crontab -e```
and add the following line:

```*/10 * * * * ~/pi-info-epaper/script.sh >> ~/info-screen.log 2>&1```

which runs the script every 10 minutes

</p>
</details>

<details><summary>Running Tests</summary>
<p>

In repo folder run a all tests from a TestClass like this:

```python3 code/test_storage.py TestStorage```

In repo folder run a single specific test like this:

```python3 code/test_paper.py TestPaper.test_paper_demo```

</p>
</details>


## Common issues

Any time/clock issues: counting starts too late, or ends too soon.

-> The timezone of the raspberry pi is not set correctly. Run  ```sudo raspi-config``` and set it to Europe/Berlin

## Future uses

The information I want to have displayed is likely to change in the future. Other ideas I have are:

- stock prices
- weather information
- wikipedia article of the day


