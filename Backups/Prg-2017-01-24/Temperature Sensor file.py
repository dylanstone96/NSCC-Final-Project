import os
import glob
import time
import RPi.GPIO as GPIO

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
    date = (str((time.localtime()).tm_hour) + ":" + str((time.localtime()).tm_min) + ":" + str((time.localtime()).tm_sec) + "," + str((time.localtime()).tm_mday) + "/" + str((time.localtime()).tm_mon) + "/" + str((time.localtime()).tm_year))
    print (date)
    print ("Sersor 1 temperature:           " + str(round(temp1, 3)) + "C")
    print ("Sersor 2 temperature:           " + str(round(temp2, 3)) + "C")
    print ("Sensor temperature difference:  " + (str(round(abs(temp1 - temp2), 3))) + "C\n\n")
    return date

while 1:
    GPIO.setmode(GPIO.BCM)              #set up GPIO using BCM numbering
    GPIO.setup(27, GPIO.OUT)
    GPIO.setup(5, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(27, 1)
    GPIO.output(5, 1)
    temp1 = read_temp(device_file1)
    flash(27, 0, 0.1)
    temp2 = read_temp(device_file2)
    GPIO.output(27, 0)
    lighttemp(22, temp1, temp2)
    date = results()                    #prints results and saves to file
    date2 = '/home/pi/Desktop/Programs/Data-' + str((time.localtime()).tm_mday) + "-" + str((time.localtime()).tm_mon) + "-" + str((time.localtime()).tm_year) + '.csv'
    with open(date2, 'a') as f:
        tempdata = date + ',' + str(round(temp1, 3)) + ',' + str(round(temp2, 3)) + ',' + str(round(abs(temp1 - temp2), 3)) + '\n'
        f.write(tempdata)
    GPIO.output(5, 0)
    GPIO.cleanup()
    time.sleep(1)                      #delay to next read
    




    


