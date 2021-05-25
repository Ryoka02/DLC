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
fps = int(sys.argv[1])

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


def shutdown():
    #1mとstartの同時押しでシャットダウン
    status = 0
    pressed_time = time.time()
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


def rec_loop():
    #録画を連続して行うか、シャットダウンするか
    while True: 
        subprocess.run("sudo /usr/bin/python3 /home/stada/DLC/record.py {}".format(fps), shell=True)
        cleanup()
        text3("Record finish!", "Record again?", "Yes or No")
        again = y_n()
        if again == "n":
            text1("Please shutdown")
            shutdown()
            break
            

def date_count():
    proc = subprocess.run("ls /home/stada/tmp", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.stdout.decode("utf8")
    videolist = output.split("\n")
    rec_count = len(videolist) - 1
    return rec_count            



######## mode select ########
while True:
    text2("Mode Select", "Record or Inference")
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
            text3(str(rec_count) + " date remain", "Inference?", "Yes or No") 
            rep = y_n()
            if rep == "y":
                subprocess.run("sudo /usr/bin/python3 /home/stada/DLC/inference.py {}".format(fps), shell=True)
                cleanup()
                text1("Please shutdown")
                shutdown()
                break
        else:
            text2("No date remain", "shutdown?", "Yes or No")
            rep = y_n()
            if rep == "y":
                text1("Please shutdown")
                shutdown()
                
    else:
       status = 0



######## cleanup ########
GPIO.cleanup(gpio_led)
GPIO.cleanup(gpio_sw_1)
GPIO.cleanup(gpio_sw_10)
GPIO.cleanup(gpio_sw_60)
GPIO.cleanup(gpio_sw_res)
GPIO.cleanup(gpio_sw_st)
