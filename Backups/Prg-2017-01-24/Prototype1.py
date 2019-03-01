import os
import glob
import time
import RPi.GPIO as GPIO
import sys
import shutil
GPIO.setwarnings(False)

os.system('modprobe w1-gpio')           #sets up IO and temp readings
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
                                        #assigns variable to each temperature sensor address
device_file1 = glob.glob(base_dir + '28-0000074b7f2d')[0] + '/w1_slave'
device_file2 = glob.glob(base_dir + '28-0000074b8662')[0] + '/w1_slave'
                                        #flashes led on call                                            
def flash(pin, state, wait):
    boo = not state
    GPIO.output(pin, state)
    time.sleep(wait)
    GPIO.output(pin, boo)
                                        #opens temperature sensor when passed address
def read_temp_raw(d_file):
    f = open(d_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
                                        #reads and returns the temperature
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
                                        #function that lights an LED when temperature 1 is higher than temperature 2
def lighttemp(pin, t1, t2):
    if t1 > t2:                         
        GPIO.output(pin, 1)
    else:
        GPIO.output(pin, 0)

def results():                          #prints the results to the console
    print (time.ctime())
    print ("Vent temperature:           " + str(round(temp1, 3)) + "C")
    print ("Ambient temperature:        " + str(round(temp2, 3)) + "C")
    print ("Vent temperature increase:   " + (str(round(temp1 - temp2, 3))) + "C\n\n")

def IRup():
    if GPIO.input(24):
        GPIO.output(17, 0)
    else:
        GPIO.output(17, 1)

def wait(itime, oldtime):
    while((time.time() - oldtime) < itime) and GPIO.input(24):
        time.sleep(.1)
        usave()
        GPIO.output(17, 0)
    if (GPIO.input(24) == 0):
        GPIO.output(17, 1)

def usave():
    folders = os.listdir("/media/pi")
    i = 0
    flow = 0
    while (i < len(folders)):
        if (not(folders[i] == "SETTINGS") and not(folders[i] == "SETTINGS1")):
            print (folders[i] + " device has been inserted.\n")
            GPIO.output(6, 1)
            time.sleep(2)
            usbfolders = os.listdir("/media/pi/" + folders[i])
            j = 0
            while (j < len(usbfolders)):
                if(usbfolders[j] == 'Data'):
                    k = 0
                    dirfiles = os.listdir("/media/pi/" + folders[i] + '/' + usbfolders[j])
                    while (k < len(dirfiles)):
                        if(dirfiles[k] == '1-AIRSPEED.txt'):
                            shutil.copyfile('/media/pi/' + folders[i] + '/Data/1-AIRSPEED.txt', '/home/pi/Desktop/Programs/Data/1-AIRSPEED.txt')
                        k = k + 1
                    shutil.rmtree('/media/pi/' + folders[i] + '/Data')
                j = j + 1
            shutil.copytree('/home/pi/Desktop/Programs/Data','/media/pi/' + folders[i] + '/Data')
            os.system('sudo udisks --unmount /dev/sda1')
            GPIO.output(6, 0)
            print (folders[i] + " device has been removed.\n")
        i = i + 1
        return flow

oldtime = time.time() - 60
ostate = 0

while 1:
    GPIO.setmode(GPIO.BCM)              #set up GPIO using BCM numbering
    GPIO.setup(27, GPIO.OUT)
    GPIO.setup(5, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(6, GPIO.OUT)
    GPIO.setup(24, GPIO.IN)
    usave()
    if (GPIO.input(24) == 0):
        ostate = 1
        otime = time.time()
        wait(4, oldtime)
    elif ((ostate == 1) and ((time.time() - otime) <= 300)):
        wait(10, oldtime)
    elif ((ostate == 1) and ((time.time() - otime) <= 900)):
        wait(30, oldtime)
    else:
        wait(60, oldtime)
        ostate = 0
    oldtime = time.time()
    GPIO.output(27, 1)
    GPIO.output(5, 1)
    temp1 = read_temp(device_file1)
    IRup()
    flash(27, 0, 0.1)
    IRup()
    temp2 = read_temp(device_file2)
    IRup()
    GPIO.output(27, 0)
    lighttemp(22, temp1, temp2)
    IRup()
    results()                    #prints results and saves to file
    date2 = '/home/pi/Desktop/Programs/Data/' + str((time.localtime()).tm_year) + "-" + str((time.localtime()).tm_mon) + "-" + str((time.localtime()).tm_mday) + '.csv'
    with open(date2, 'a') as f:
        tempdata = time.ctime() + ',' + str(round(temp1, 3)) + ',' + str(round(temp2, 3)) + ',' + str(round(abs(temp1 - temp2), 3)) + ',' + str((GPIO.input(24) == 0)) + '\n'
        f.write(tempdata)
    IRup()
    GPIO.output(5, 0)
   #time.sleep(1)                      #delay to next read
    IRup()
    

GPIO.cleanup()
    




    


