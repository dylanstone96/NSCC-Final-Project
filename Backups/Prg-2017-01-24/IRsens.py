import os
import glob
import time
import RPi.GPIO as GPIO

while 1:
    GPIO.setmode(GPIO.BCM)              #set up GPIO using BCM numbering
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(24, GPIO.IN)
    if GPIO.input(24):
        GPIO.output(17, 0)
    else:
        GPIO.output(17, 1)
