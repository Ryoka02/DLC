import subprocess
import time

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import RPi.GPIO as GPIO 


#### config ####
gpio_led = 21
gpio_sw_1 = 20
gpio_sw_10 = 18
gpio_sw_60 = 12
gpio_sw_res = 8
gpio_sw_st = 7

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


def text1(text):
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text, fill="white")


def text2(text1, text2):
    with canvas(device, dither=True) as draw:
        draw.text((10, 20), text1, fill="white")
        draw.text((10, 30), text2, fill="white")


def y_n():
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


status = 0
pressed_time = time.time()
interval = 0.3
        
text2("Mode Select", "Record or Inference")
rep = y_n()

if rep == "n":
    text2("Record?", "Yes or No") 
    rep = y_n()
    if rep == "" 
    


while True:
    #if (GPIO.input(gpio_sw_res) == 0) & (status == 0) & (time.time() - pressed_time > interval):
    if (n == 1) & (status == 0) & (time.time() - pressed_time > interval):
        status = 1
        pressed_time = time.time()

        while True:
            #text2("Recording?", "Yes or No")
            print("Record?")
            n = input("Yes or No")
            #if (GPIO.input(gpio_sw_res) == 0) & (status == 1) & (time.time() - pressed_time > interval):
            if (n == "Yes") & (status == 1) & (time.time() - pressed_time > interval):
                status = 2
                #subprocess.run("sudo python3 /home/stada/DLC/record.py", shell=True)
                subprocess.run("python3 record.py", shell=True)
                #text2("Record again?", "Yes or No")
                print("Record again? Yes or No")
                n = input("Yes or No")

                while True:
                    #if (GPIO.input(gpio_sw_res) == 0) & (status == 2) & (time.time() - pressed_time > interval):
                    if (n == "Yes") & (status == 2) & (time.time() - pressed_time > interval):
                        status = 3
                        break
                    
                    #elif (GPIO.input(gpio_sw_st) == 0) & (status == 2) & (time.time() - pressed_time > interval):
                    elif (n == "No") & (status == 2) & (time.time() - pressed_time > interval):
                        status = 3
                        #text1("Please shutdown")
                        print("Please shutdown")
                        break
                    
                    else:
                        status = 2
                        

            
            #elif (GPIO.input(gpio_sw_st) == 0) & (status == 1) & (time.time() - pressed_time > interval):
            elif (n == "No") & (status == 1) & (time.time() - pressed_time > interval):
                status = 2
                break

            else:


        break
    
    #elif (GPIO.input(gpio_sw_st) == 0) & (status == 0):
    elif (n == 2) & (status == 0):
        #subprocess.run("sudo python3 /home/stada/DLC/inference.py", shell=True)
        subprocess.run("python3 inference.py", shell=True)
        break
    
    else:
        status = 0


print("finish")


