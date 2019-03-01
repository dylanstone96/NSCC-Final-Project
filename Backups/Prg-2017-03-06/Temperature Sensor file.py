#sensor 2 appears to be 0.063 degrees too low

import os
import glob
import time
import RPi.GPIO as GPIO

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

device_file1 = glob.glob(base_dir + '28-011592209dff')[0] + '/w1_slave'
device_file2 = glob.glob(base_dir + '28-0115922482ff')[0] + '/w1_slave'

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
    if t1 == t2:
        GPIO.output(pin, 1)
    else:
        GPIO.output(pin, 0)

def results():
    date = (str((time.localtime()).tm_hour) + ":" + str((time.localtime()).tm_min) + ":" + str((time.localtime()).tm_sec) + "," + str((time.localtime()).tm_mday) + "/" + str((time.localtime()).tm_mon) + "/" + str((time.localtime()).tm_year))
    print (date)
    print ("Sersor 1 temperature:           " + str(round(temp1, 3)) + "C")
    print ("Sersor 2 temperature:           " + str(round(temp2, 3)) + "C")
    print ("Sensor temperature difference:  " + (str(round(abs(temp1 - temp2), 3))) + "C\n\n")
    return date

while 1:
    #set up GPIO using BCM numbering
    GPIO.setmode(GPIO.BCM)
    #setup GPIO using Board numbering
    #GPIO.setmode(GPIO.BOARD)
    GPIO.setup(27, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(27, 1)
    temp1 = read_temp(device_file1)
    flash(27, 0, 0.1)
    temp2 = read_temp(device_file2)
    GPIO.output(27, 0)
    lighttemp(22, temp1, temp2)
    date = results()
    with open('/home/pi/Desktop/Programs/Data1.csv', 'a') as f:
        tempdata = date + ',' + str(round(temp1, 3)) + ',' + str(round(temp2, 3)) + ',' + str(round(abs(temp1 - temp2), 3)) + '\n'
        f.write(tempdata)
    time.sleep(10)
    GPIO.cleanup()




    


