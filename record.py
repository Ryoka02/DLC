#!/usr/bin/python3


####### utils
import time
import sys
import datetime
import os

####### hard
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import RPi.GPIO as GPIO 

######## dlc
import cv2
import numpy as np
from tqdm import tqdm
WINDOW_NAME = 'Camera Test'
import pandas as pd

#### config ####
gpio_led = 8
gpio_sw_1 = 21
gpio_sw_10 = 20
gpio_sw_60 = 16
gpio_sw_res = 12
gpio_sw_st = 7

interval = 0.3
################

#### devices set up ####
serial = i2c(port=1, address=0x3C)
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
########

min = 0
status = 0
pressed_time = time.time()


def show_min(min):
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), "Exposure time...", fill="white")
        draw.text((10, 40), str(min) + " min", fill="white")


def text1(text):
    #textを1行表示
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text, fill="white")


def text2(text1, text2):
    #text1とtext2を改行して表示
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text1, fill="white")
        draw.text((10, 30), text2, fill="white")


def record(settime,rec_name):
    os.makedirs("/home/stada/tmp/{}".format(rec_name), exist_ok=True)
    ## record ====
    GST_STR = 'nvarguscamerasrc \
        ! video/x-raw(memory:NVMM), width=3280, height=2464, format=(string)NV12, framerate=(fraction)30/1 \
        ! nvvidconv ! video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx \
        ! videoconvert \
        ! appsink'
    cap = cv2.VideoCapture(GST_STR, cv2.CAP_GSTREAMER)
    out = cv2.VideoWriter("/home/stada/tmp/{}/movie.avi".format(rec_name), cv2.VideoWriter_fourcc("X","V","I","D"),21, (640, 480))
    start = time.time()
    pbar = tqdm(total=settime*21)
    while time.time()-start<=settime:
        ret, frame = cap.read()
        out.write(frame)
        pbar.update(1)
    pbar.close()
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    text1("Record finish!")

show_min(min)

while True:
    if (GPIO.input(gpio_sw_1) == 0) & (status == 0) & (time.time() - pressed_time > interval):
        min += 1
        status = 1
        # print(min)
        show_min(min)
        pressed_time = time.time()
    
    elif (GPIO.input(gpio_sw_10) == 0) & (status == 0) & (time.time() - pressed_time > interval):
        min += 10
        status = 1
        # print(min)
        show_min(min)
        pressed_time = time.time()
    
    elif (GPIO.input(gpio_sw_60) == 0) & (status == 0) & (time.time() - pressed_time > interval):
        min += 60
        status = 1
        # print(min)
        show_min(min)
        pressed_time = time.time()

    elif (GPIO.input(gpio_sw_res) == 0) & (status == 0) & (time.time() - pressed_time > interval):
        min = 0
        status = 1
        # print(min)
        show_min(min)
        pressed_time = time.time()

    elif (GPIO.input(gpio_sw_st) == 0):
        GPIO.output(gpio_led, 1) 
        text2("Now recording...", str(min) + " min")

        ##################
        ### deeplabcut ###
        ##################
        now = datetime.datetime.now()
        rec_name = str(now.year)+"-"+str(now.month)+"-"+str(now.day)+"-"+str(now.hour)+"-"+str(now.minute)+"-"+str(now.second)
        #rectime = min*60
        rectime = min*1
        record(rectime, rec_name)

        break

    else:
        status = 0
