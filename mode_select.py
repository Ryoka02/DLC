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
import os

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
fps = int(sys.argv[1])

version = "210610"

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

######## get environments ########
dir_base = os.path.realpath(os.path.dirname(__file__))

######## functions ########
def cleanup():
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

    
def y_n():
    #Reset(n)とStart(y)の入力を受け取る
    status = 0
    pressed_time = time.time()
    while True:
        if (GPIO.input(gpio_sw_res) == 0) & (status == 0) & (time.time() - pressed_time > interval):
            status = 1
            pressed_time = time.time()
            ans = "y"
            break
        elif (GPIO.input(gpio_sw_st) == 0) & (status == 0) & (time.time() - pressed_time > interval):
            status = 1
            pressed_time = time.time()
            ans = "n"
            break
        else:
            status = 0
    return ans


def shutdown_reboot():
    #1mとstartの同時押しでシャットダウンか再起動
    status = 0
    pressed_time = time.time()
    text2("Mode select", "Shutdown or Reboot")
    rep = y_n()
    if rep == "y":
        text1("Please shutdown")        
        while True:
            if (GPIO.input(gpio_sw_1) == 0) & (GPIO.input(gpio_sw_st) == 0) & (status == 0) & (time.time() - pressed_time > interval):
                status = 1
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
    else:
        text1("Please reboot")
        while True:
            if (GPIO.input(gpio_sw_1) == 0) & (GPIO.input(gpio_sw_st) == 0) & (status == 0) & (time.time() - pressed_time > interval):
                status = 1
                text1("reboot...")
                subprocess.run("journalctl -u DLC.service > log.txt", shell=True)
                now = datetime.datetime.now()
                log_time = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + str(now.hour) + "-" + str(now.minute) + "-" + str(now.second)
                subprocess.run("sudo mkdir /home/stada/log/{}".format(log_time), shell=True)
                subprocess.run("sudo mv /log.txt /home/stada/log/{}".format(log_time), shell=True)
                subprocess.run("sudo reboot", shell=True)
                break
            else:
                status = 0

def rec_loop():
    #録画を連続して行うか、シャットダウンするか
    while True: 
        subprocess.run("sudo /usr/bin/python3 {}/record.py {}".format(dir_base, fps), shell=True)
        cleanup()
        text3("Record finish!", "Record again?", "Yes or No")
        again = y_n()
        if again == "n":
            shutdown_reboot()
            break

            
def inf_loop():
    #推論を連続して行うか、シャットダウンするか
    while True: 
        subprocess.run("sudo /usr/bin/python3 {}/inference.py {}".format(dir_base, fps), shell=True)
        cleanup()
        text3("Inference finish!", "Inference again?", "Yes or No")
        again = y_n()
        if again == "n":
            shutdown_reboot()
            break

            
def inf_atonce(rec_count):
    for i in range(rec_count): 
        subprocess.run("sudo /usr/bin/python3 {}/inference.py {}".format(dir_base, fps), shell=True)
        cleanup()
        
    text2("All inferences have done.", "Please press Start")
    status = 0
    pressed_time = time.time()
    while True:
        if (GPIO.input(gpio_sw_st) == 0) & (status == 0) & (time.time() - pressed_time > interval):
            status = 1
            shutdown_reboot()
            break
        else:
            status = 0

            
def date_count():
    proc = subprocess.run("ls /home/stada/tmp", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.stdout.decode("utf8")
    videolist = output.split("\n")
    rec_count = len(videolist) - 1
    return rec_count            



######## mode select ########
while True:
    text3("verion : {}".format(version), "Mode Select", "Record or Inference")
    rep = y_n()
    
    if rep == "y":
        text2("Record?", "Yes or No") 
        rep = y_n()
        if rep == "y":
            rec_loop()
            break
            
    elif rep == "n":
        rec_count = date_count()
        if rec_count >=1:
            text3(str(rec_count) + " movies are remaining", "Inference?", "Yes or No") 
            rep = y_n()
            if rep == "y":
                text2("Inference at once?", "Yes or No") 
                rep = y_n()
                if rep == "y":
                    inf_atonce(rec_count)
                else:
                    inf_loop()
                break
        else:
            text3("No data remains", "Shutdown or Reboot?", "Yes or No")
            rep = y_n()
            if rep == "y":
                shutdown_reboot()
                
    else:
       status = 0



######## clean up ########
GPIO.cleanup(gpio_led)
GPIO.cleanup(gpio_sw_1)
GPIO.cleanup(gpio_sw_10)
GPIO.cleanup(gpio_sw_60)
GPIO.cleanup(gpio_sw_res)
GPIO.cleanup(gpio_sw_st)
