import subprocess
import time

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import RPi.GPIO as GPIO 


#### config ####
gpio_led = 21
gpio_sw_1 = 20
gpio_sw_10 = 16
gpio_sw_60 = 12
gpio_sw_res = 7
gpio_sw_st = 8

interval = 0.3
########

#### devices set up ####
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_led, GPIO.OUT)
GPIO.setup(gpio_sw_1, GPIO.IN)
GPIO.setup(gpio_sw_10, GPIO.IN)
GPIO.setup(gpio_sw_60, GPIO.IN)
GPIO.setup(gpio_sw_res, GPIO.IN)
GPIO.setup(gpio_sw_st, GPIO.IN)

GPIO.output(gpio_led, 0) 
########


def text1(text):　#textを1行表示
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text, fill="white")


def text2(text1, text2):　#text1とtext2を改行して表示
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text1, fill="white")
        draw.text((10, 30), text2, fill="white")


def y_n():　#Reset(n)とStart(y)の入力を受け取る
    status = 0
    pressed_time = time.time()
    while True:
        if (GPIO.input(gpio_sw_res) == 0) & (status == 0) & (time.time() - pressed_time > interval):
            status = 1
            pressed_time = time.time()
            ans = "n"
            break
        elif (GPIO.input(gpio_sw_st) == 0) & (status == 0) & (time.time() - pressed_time > interval):
            status = 1
            pressed_time = time.time()
            ans = "y"
            break
        else:
            status = 0
    return ans


def shutdown():　#1mとstartの同時押しでシャットダウン
    status = 0
    while True:
        if (GPIO.input(gpio_sw_1) == 0) & (GPIO.input(gpio_sw_st) == 0) & (status == 0) & (time.time() - pressed_time > interval):
            status = 1
            text1("shutdown...")
            time.sleep(3)
            subprocess.run("sudo shutdown -h now", shell=True)
            break
        else:
            status = 0


def rec_loop():　#録画を連続して行うか、シャットダウンするか
    while True:
        again = y_n() 
        if again == "y":
            subprocess.run("sudo python3 /home/stada/DLC/record.py", shell=True)
            text2("Record again?", "Yes or No")
        else:
            text1("Please shutdown")
            shutdown()
            break
            

while True:
    text2("Mode Select", "Record or Inference")
    rep = y_n()
    if rep == "n":
        text2("Record?", "Yes or No") 
        rec_loop()
        break
    else:
        text2("Inference?", "Yes or No") 
        rep = y_n()
        if rep == "y":
            subprocess.run("sudo python3 inference.py", shell=True)
            text1("Please shutdown")
            shutdown()
            break
