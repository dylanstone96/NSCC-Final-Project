import os
import glob
import time

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

device_file1 = glob.glob(base_dir + '28-011592209dff')[0] + '/w1_slave'
device_file2 = glob.glob(base_dir + '28-0115922482ff')[0] + '/w1_slave'

import RPi.GPIO as GPIO
#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
#setup GPIO using Board numbering
#GPIO.setmode(GPIO.BOARD)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

def flash(pin, state, wait):
    boo = not state
    GPIO.output(pin, state)
    time.sleep(wait)
    GPIO.output(pin, boo)
    
def read_temp_raw(d_file):
    f = open(d_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(d_file):
    lines = read_temp_raw(d_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw1()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def lighttemp(pin, t1, t2):
    if t1 > t2:
        GPIO.output(pin, 1)
    else:
        GPIO.output(pin, 0)

def results(display):
    q = 1
    if (display == "all" or display == "1" or display == "2" or display == "temp" or display == "diff"):
        if (display == "all" or display == "1" or display == "temp"):
            print("Sersor 1 temperature:           ", round(temp1, 3), "C")
        if (display == "all" or display == "2" or display == "temp"):
            print("Sersor 2 temperature:           ", round(temp2, 3), "C")
        if (display == "all" or display == "diff"):
            print("Sensor temperature difference:  ", round(abs(temp1 - temp2), 3), "C")
        if (display == "all"):
            print("LED illuminated while sensor 1 is hotter than sensor 2")
        print("\n\n")
    elif(display == "quit"):
        print("The program will now terminate...")
        time.sleep(1)
        q = 0
        print("\n")
    elif(display == "loop"):
         q = int(input("Please enter number of loops\n-"))
    else:
        print("No valid input was detected\n")
    return q
    

display = "all"
q = 1
loopnum = 0

while (q or (loopnum >=1)):
    GPIO.output(27, 1)
    temp1 = read_temp(device_file1)
    flash(27, 0, 0.1)
    temp2 = read_temp(device_file2)
    GPIO.output(27, 0)
    lighttemp(22, temp1, temp2)
    q = results(display)
    if (q > 1):
        loopnum = q
        q = 1
    if ((q == 1) and (loopnum < 1)):
        display = input("Enter \"all\" \"1\" \"2\" \"temp\" \"diff\" \"loop\" or \"quit\" to continue\n-")
    if (loopnum >= 1):
        loopnum = loopnum - 1
        display = "all"

GPIO.cleanup()


    


    


