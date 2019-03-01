import os
import glob
import time
import RPi.GPIO as GPIO
import sys
import shutil
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN, pull_up_down = GPIO.PUD_UP)
while(GPIO.input(25)):
    time.sleep(0.05)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.output(17, 0)
GPIO.output(6, 0)
time.sleep(0.15)
GPIO.output(17, 1)
GPIO.output(6, 1)
time.sleep(0.25)
GPIO.output(17, 0)
GPIO.output(6, 0)
time.sleep(0.15)
GPIO.output(17, 1)
GPIO.output(6, 1)
time.sleep(0.25)
GPIO.output(17, 0)
GPIO.output(6, 0)
GPIO.output(5, 1)
os.system("sudo reboot")
