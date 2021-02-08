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
import deeplabcut

#### config ####
gpio_led = 8
gpio_sw_st = 7

interval = 0.3

#### devices set up ####
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
GPIO.cleanup(gpio_led)
GPIO.cleanup(gpio_sw_st)
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_led, GPIO.OUT)
GPIO.setup(gpio_sw_st, GPIO.IN)

GPIO.output(gpio_led, 1) 
subprocess.run("sudo mount /dev/sda1 /media/stada/dlc_stada", shell = True)
#tables.path.append("/usr/local/lib/python3.6/dist-packages")


######## def ########
def text1(text):
    #textを1行表示
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text, fill="white")


def text2(text1, text2):
    #text1とtext2を改行して表示
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text1, fill="white")
        draw.text((10, 30), text2, fill="white")


def text3(text1, text2, text3):
    #text1とtext2を改行して表示
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text1, fill="white")
        draw.text((10, 30), text2, fill="white")
        draw.text((10, 40), text2, fill="white")


def inference(rec_name):
    text1("Now Inferencing...")
    #videofile_path=dir_usb + "/{}.avi".format(rec_name)
    videofile_path="/home/stada/tmp/{}/movie.avi".format(rec_name)
    path_config_file="/home/stada/mouse_tracking-stada-2020-12-23/config.yaml"
    deeplabcut.analyze_videos(path_config_file, videofile_path, save_as_csv=True)
    #deeplabcut.analyze_videos(path_config_file, videofile_path, save_as_csv=True, videotype = "avi", shuffle = 1)
    #deeplabcut.analyze_videos_converth5_to_csv("/home/stada/tmp/{}".format(rec_name), '.avi')
    #df = pd.read_csv("/home/stada/tmp/{}/movieDLC_resnet50_mouse_trackingDec23shuffle1_5500.csv".format(rec_name))
    #df.to_pickle("/home/stada/tmp/{}/movieDLC_resnet50_mouse_trackingDec23shuffle1_5500_meta.pickle".format(rec_name))
    #df.to_hdf("/home/stada/tmp/{}/movieDLC_resnet50_mouse_trackingDec23shuffle1_5500.h5".format(rec_name), key="df", format="table", mode="w")
    deeplabcut.create_labeled_video(path_config_file, videofile_path, draw_skeleton=True)
    # deeplabcut.convert_detections2tracklets(path_config_file,videofile_path, videotype="mp4", track_method='skeleton')
    # deeplabcut.convert_raw_tracks_to_h5()
    # deeplabcut.plot_trajectories(path_config_file,videofile_path, videotype="mp4", track_method='skeleton')
    text1("Inference finish!")


def change_fps(name):
    text1("Now converting...")
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
    text1("Convert finish!")

def get_usb_name():
    proc = subprocess.run("ls /media/stada", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    usb_name = proc.stdout.decode("utf8")
    usblist = usb_name.split("\n")
    usb_name = usblist[0]
    dir_usb = "/media/stada/{}".format(usb_name)


def wait_input_st():
    status = 0
    while True:
        #n = int(input())
        if (GPIO.input(gpio_sw_st) == 0) & (status == 0):
        #if (n == 1) & (status == 0) & (time.time() - pressed_time > interval):
            status = 1
            break
        else:
            status = 0


######## inference ########
proc = subprocess.run("ls /home/stada/tmp", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
output = proc.stdout.decode("utf8")
videolist = output.split("\n")
rec_name = videolist[0]


try:
    inference(rec_name)
    change_fps(rec_name)
    get_usb_name()
    #subprocess.run("sudo mv /home/stada/tmp/{} /media/stada/{}".format(rec_name, usb_name), shell = True)
    #subprocess.run("sudo mv /home/stada/tmp/{} /home/stada/temp".format(rec_name), shell = True)
    subprocess.run("sudo mv /home/stada/tmp/{} /media/stada/dlc_stada".format(rec_name), shell = True)
    subprocess.run("sudo umount -l /dev/sda1 /media/stada/dlc_stada", shell = True)
except:
    GPIO.output(gpio_led, 1)
    text3("Error", "Press Start button", "Contact to Y.Yasumizu")
    wait_input_st()
    
    