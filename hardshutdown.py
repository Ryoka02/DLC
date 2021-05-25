#!/usr/bin/env python

##########################################
###                                      
### 2021/01/28
### auto-runner of DeepLabCut
###
### Masatoshi Abe, Ryoko Kitabatake, 
### Yuhei Ohtsuka, Yoshiaki Yasumizu
### Osaka University, Faculty of Medicine
### Python-kai
###
##########################################


######## utils ########
import subprocess
import time
import datetime
import sys

######## hard ########
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import RPi.GPIO as GPIO 

######## config ########
gpio_led = 8
gpio_sw_1 = 21
gpio_sw_10 = 20
gpio_sw_60 = 16
gpio_sw_res = 12
gpio_sw_st = 7
interval = 0.3

######## devices set up ########
serial = i2c(port=8, address=0x3C)
device = sh1106(serial)
GPIO.cleanup(gpio_led)
GPIO.cleanup(gpio_sw_1)
GPIO.cleanup(gpio_sw_10)
GPIO.cleanup(gpio_sw_60)
GPIO.cleanup(gpio_sw_res)
GPIO.cleanup(gpio_sw_st)
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_led, GPIO.OUT)
GPIO.setup(gpio_sw_1, GPIO.IN)
GPIO.setup(gpio_sw_10, GPIO.IN)
GPIO.setup(gpio_sw_60, GPIO.IN)
GPIO.setup(gpio_sw_res, GPIO.IN)
GPIO.setup(gpio_sw_st, GPIO.IN)
GPIO.output(gpio_led, 0) 



######## mode select ########
status = 0
while True:
    if (GPIO.input(gpio_sw_1) == 0) & (GPIO.input(gpio_sw_10) == 0) & (GPIO.input(gpio_sw_60) == 0) & (GPIO.input(gpio_sw_res) == 0) & (GPIO.input(gpio_sw_st) == 0) & (status == 0):
        status = 1
        subprocess.run("sudo systemctl stop DLC.service", shell=True)
        text1("shutdown...")
        subprocess.run("journalctl -u DLC.service > log.txt", shell=True)
        now = datetime.datetime.now()
        log_time = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + str(now.hour) + "-" + str(now.minute) + "-" + str(now.second)
        subprocess.run("sudo mkdir /home/stada/log/{}".format(log_time), shell=True)
        subprocess.run("sudo mv /log.txt /home/stada/log/{}".format(log_time), shell=True)
        subprocess.run("sudo shutdown -h now", shell=True)
        break
    else:
        status = 0
