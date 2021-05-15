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
import subprocess

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
#import deeplabcutcore as deeplabcut(立ち上げ時に時間がかかるため後でインポート)

######## config ########
gpio_led = 8
gpio_sw_st = 7
interval = 0.3

######## devices set up ########
serial = i2c(port=8, address=0x3C)
device = sh1106(serial)
GPIO.cleanup(gpio_led)
GPIO.cleanup(gpio_sw_st)
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_led, GPIO.OUT)
GPIO.setup(gpio_sw_st, GPIO.IN)
GPIO.output(gpio_led, 0) 



######## display def ########
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


##### 起動待ち #####
text1("Now Setting...")
import deeplabcutcore as deeplabcut
####################


######## inference def ########
def inference(rec_name):
    text1("Now Analyzing...")
    videofile_path="/home/stada/tmp/{}/movie.avi".format(rec_name)
    path_config_file="/home/stada/mouse_tracking-stada-2020-12-23/config.yaml"
    deeplabcut.analyze_videos(path_config_file, videofile_path, save_as_csv=True)
    text2("Analyze finish!", "Now labeling...")
    deeplabcut.create_labeled_video(path_config_file, videofile_path, draw_skeleton=True)


def change_fps(name):
    text2("Label finish!", "Now converting...")
    file_path = "/home/stada/tmp/{}/movieDLC_resnet50_mouse_trackingDec23shuffle1_5500_labeled.mp4".format(name)
    path_out = "/home/stada/tmp/{}/movieDLC_resnet50_mouse_trackingDec23shuffle1_5500_labeled_final.mp4".format(name)
    cap = cv2.VideoCapture(file_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = cv2.VideoWriter(path_out, fourcc, 21, (w, h), True)
    while True:
      ret, frame = cap.read()
      video.write(frame) 
      if not ret:break
    cap.release()


def wait_input_st():
    status = 0
    while True:
        if (GPIO.input(gpio_sw_st) == 0) & (status == 0):
            status = 1
            break
        else:
            status = 0


    
######## detect usb ########
try:
    subprocess.run("sudo mkdir /media/stada/dlc_stada")
except:
    pass

try:
    subprocess.run("sudo mount /dev/sda1 /media/stada/dlc_stada", shell=True)
except:
    text2("No detected USB", "Press Start button")
    wait_input_st()
    sys.exit()

  
######## get rec_name ########    
proc = subprocess.run("ls /home/stada/tmp", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
output = proc.stdout.decode("utf8")
videolist = output.split("\n")
rec_name = videolist[0]


######## inference ########
inference(rec_name)
change_fps(rec_name)
subprocess.run("sudo mv /home/stada/tmp/{} /media/stada/dlc_stada".format(rec_name), shell=True)


######## unmount ########
subprocess.run("sudo umount -l /media/stada/dlc_stada", shell=True)

try:
    subprocess.run("sudo rm -r /media/stada/dlc_stada", shell=True)
except:
    pass

GPIO.output(gpio_led, 1)
text2("Inference finish!", "Press Start button")
wait_input_st()
