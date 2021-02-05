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


import subprocess
import time

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import RPi.GPIO as GPIO 

#### config ####
gpio_led = 8
gpio_sw_1 = 21
gpio_sw_10 = 20
gpio_sw_60 = 16
gpio_sw_res = 12
gpio_sw_st = 7

interval = 0.3
########

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

proc = subprocess.run("ls /media/stada", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
dir_usb = "/media/stada/" + proc.stdout.decode("utf8")

def cleanup():
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

def sw_cleanup():
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

def text1(text):
    #textを1行表示
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text, fill="white")


def text2(text1, text2):
    #text1とtext2を改行して表示
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text1, fill="white")
        draw.text((10, 30), text2, fill="white")


##1=Reset 2=Start

def y_n():
    #Reset(n)とStart(y)の入力を受け取る
    status = 0
    pressed_time = time.time()
    while True:
        #n = int(input())
        if (GPIO.input(gpio_sw_res) == 0) & (status == 0) & (time.time() - pressed_time > interval):
        #if (n == 1) & (status == 0) & (time.time() - pressed_time > interval):
            status = 1
            pressed_time = time.time()
            ans = "y"
            break
        elif (GPIO.input(gpio_sw_st) == 0) & (status == 0) & (time.time() - pressed_time > interval):
        #elif (n == 2) & (status == 0) & (time.time() - pressed_time > interval):
            status = 1
            pressed_time = time.time()
            ans = "n"
            break
        else:
            status = 0
    return ans


#10=shutdown
def shutdown():
    #1mとstartの同時押しでシャットダウン
    status = 0
    pressed_time = time.time()
    while True:
        #n = int(input())
        if (GPIO.input(gpio_sw_1) == 0) & (GPIO.input(gpio_sw_st) == 0) & (status == 0) & (time.time() - pressed_time > interval):
        #if (n == 10) & (status == 0) & (time.time() - pressed_time > interval):
            status = 1
            text1("shutdown...")
            print("shutdown...")
            time.sleep(3)
            print("See you!")
            #subprocess.run("sudo shutdown -h now", shell=True)
            break
        else:
            status = 0


def rec_loop():
    #録画を連続して行うか、シャットダウンするか
    while True: 
        subprocess.run("sudo python3 /home/stada/DLC/record.py", shell=True)
        #subprocess.run("python3 record.py", shell=True)
        cleanup()
        text2("Record again?", "Yes or No")
        print("Record again? Yes or No")
        again = y_n()
        if again == "n":
            text1("Please shutdown")
            print("Please shutdown")
            shutdown()
            break
            

while True:
    text2("Mode Select", "Record or Inference")
    print("Mode Select  Record or Inference:")
    rep = y_n()
    if rep == "y":
        text2("Record?", "Yes or No") 
        print("Record? Yes or No")
        rep = y_n()
        if rep == "y":
            rec_loop()
            break
    elif rep == "n":
        text2("Inference?", "Yes or No") 
        print("Inference? Yes or No")
        rep = y_n()
        if rep == "y":
            text2("detected USB:", dir_usb)
            subprocess.run("sudo /usr/bin/python3 /home/stada/DLC/inference.py", shell=True)
            #subprocess.run("python3 inference.py", shell=True)
            cleanup()
            print("Please shutdown")
            text1("Please shutdown")
            shutdown()
            break
    else:
       status = 0

GPIO.cleanup(gpio_led)
GPIO.cleanup(gpio_sw_1)
GPIO.cleanup(gpio_sw_10)
GPIO.cleanup(gpio_sw_60)
GPIO.cleanup(gpio_sw_res)
GPIO.cleanup(gpio_sw_st)
