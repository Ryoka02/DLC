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
import time
import sys
import datetime
import os
import threading

######## hard ########
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import RPi.GPIO as GPIO 

######## dlc ########
import cv2
import numpy as np
from tqdm import tqdm
WINDOW_NAME = 'Camera Test'
import pandas as pd

######## config ########
gpio_led = 8
gpio_sw_1 = 21
gpio_sw_10 = 20
gpio_sw_60 = 16
gpio_sw_res = 12
gpio_sw_st = 7
interval = 0.3
fps = int(sys.argv[0])

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



######## def ########
def show_min(min):
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), "Exposure time...", fill="white")
        draw.text((10, 40), str(min) + " min", fill="white")
    print("Exposure time...  " + str(min) + " min")
        

def text1(text):
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text, fill="white")
    print(text)


def text2(text1, text2):
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text1, fill="white")
        draw.text((10, 30), text2, fill="white")
    print(text1 + "  " + text2)


def text3(text1, text2, text3):
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text1, fill="white")
        draw.text((10, 30), text2, fill="white")
        draw.text((10, 40), text3, fill="white")
    print(text1 + "  " + text2 + "  " + text3)


def record(settime, rec_name, fps):
    os.makedirs("/home/stada/tmp/{}".format(rec_name), exist_ok=True)
    ## record ====
    GST_STR = 'nvarguscamerasrc \
        ! video/x-raw(memory:NVMM), width=640, height=480, format=(string)NV12, framerate=(fraction){}/1 \
        ! nvvidconv ! video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx \
        ! videoconvert \
        ! appsink'.format(fps)
    cap = cv2.VideoCapture(GST_STR, cv2.CAP_GSTREAMER)
    out = cv2.VideoWriter("/home/stada/tmp/{}/movie.avi".format(rec_name), cv2.VideoWriter_fourcc("X","V","I","D"), fps, (640, 480))
    start = time.time()
    pbar = tqdm(total=settime*fps)
    while time.time()-start<=settime:
        _, frame = cap.read()
        out.write(frame)
        pbar.update(1)
    pbar.close()
    cap.release()
    out.release()
    cv2.destroyAllWindows()


def rec_main(min):
    now = datetime.datetime.now()
    rec_name = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + str(now.hour) + "-" + str(now.minute) + "-" + str(now.second) + "-" + str(min) + "min"
    rectime = min * 60
    # rectime = min * 1
    time.sleep(1)
    record(rectime, rec_name, fps)

    
def time_display(min):
    GPIO.output(gpio_led, 1)
    elapsed_time = 0
    for i in range(min):
        text2("Now recording...", str(elapsed_time) + " min" + " / " + str(min) + " min")
        time.sleep(60)
        # time.sleep(1)
        elapsed_time += 1
        if elapsed_time == min:
            break
       
    
    
######## record ########
min = 0
status = 0
pressed_time = time.time()

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
        if min != 0:
            thread1 = threading.Thread(target=rec_main, args=[min])
            thread2 = threading.Thread(target=time_display, args=[min])
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()
            sys.exit()

    else:
        status = 0
