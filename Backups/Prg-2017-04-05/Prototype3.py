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

def results():                          #prints the results to the console
    print (time.ctime())
    print ("Vent temperature:           " + str(round(temp1, 3)) + "C")
    print ("Ambient temperature:        " + str(round(temp2, 3)) + "C")
    print ("Vent temperature increase:   " + (str(round(temp1 - temp2, 3))) + "C")
    print (str(power) + "W")
    print (str(round(totalen, 3)) + "kWh\n\n")

def IRup():
    if GPIO.input(24):
        GPIO.output(17, 0)
        state = False
    else:
        GPIO.output(17, 1)
        state = True
    return state

def wait(itime, oldtime):
    while(((time.time() - oldtime) < itime) and (IRup() == False) and (GPIO.input(23) == True)):
        time.sleep(.1)
        usave()

def usave():
    folders = (os.popen("ls -l /media/pi/").readlines())
    i = 0
    flow = 0
    while (i < len(folders)):
        stringf = folders[i].split(" ")
        if (len(folders[i]) > 15):
            if (stringf[2] == "pi"):
                stringf = folders[i].split(":")
                if (len(stringf) == 1):
                    stringf = stringf[0].split("196")
                stringf = stringf[1].split(" ")
                #print stringf
                #print stringf[1]
                h = len(stringf)
                g = 1
                folders[i] = stringf[g]
                g = g + 1
                while (g < h):
                    folders[i] = folders[i] + " " + stringf[g]
                    g = g + 1
                folders[i] = folders[i].rstrip()
                print (folders[i] + " device has been inserted.\n")
                GPIO.output(6, 1)
                #time.sleep(4)
                usbfolders = os.listdir("/media/pi/" + folders[i])
                j = 0
                while (j < len(usbfolders)):
                    if(usbfolders[j] == 'Data'):
                        k = 0
                        dirfiles = os.listdir("/media/pi/" + folders[i] + '/' + usbfolders[j])
                        while (k < len(dirfiles)):
                            if(dirfiles[k] == '1-AIRSPEED.txt' and lps('/media/pi/' + folders[i] + '/Data/1-AIRSPEED.txt')):
                                shutil.copyfile('/media/pi/' + folders[i] + '/Data/1-AIRSPEED.txt', '/home/pi/Desktop/Programs/Data/1-AIRSPEED.txt')
                            k = k + 1
                        shutil.rmtree('/media/pi/' + folders[i] + '/Data')
                    j = j + 1
                shutil.copytree('/home/pi/Desktop/Programs/Data','/media/pi/' + folders[i] + '/Data')
                os.system('sudo udisks --unmount /dev/sda1')
                GPIO.output(6, 0)
                time.sleep(0.4)
                flash(6,1,0.1)
                flash(6,0,0.1)
                flash(6,1,0.1)
                print (folders[i] + " device has been removed.\n")
        i = i + 1
    GPIO.output(6, 0)

oldtime = time.time() - 60
oldtime2 = time.time()
oldday = time.localtime()
ostate = 0
startup = 1
flow = 47
energy = 0
totalen = 0
power = 0
dayen = 0

def lps(directory):
    with open(directory, "r") as ff:
        fstring = ff.read()
        if(len(fstring) > 3):
            if (fstring[1] == 'l'):
                start = 1;
            elif (fstring[2] == 'l'):
                start = 2
            elif (fstring[3] == 'l'):
                start = 3
            elif (fstring[4] == 'l'):
                start = 4
            if ((fstring[start] == 'l') and (fstring[start + 1] == 'p') and (fstring[start + 2] == 's')):
                print (fstring)
                k = 0
                lstring = ''
                while (k < start):
                    lstring = lstring + fstring[k]
                    k = k + 1
                flow = int(lstring)
                return True
        return False

lps("/home/pi/Desktop/Programs/Data/1-AIRSPEED.txt")

while 1:
    GPIO.setmode(GPIO.BCM)              #set up GPIO using BCM numbering
    GPIO.setup(5, GPIO.OUT)
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(6, GPIO.OUT)
    GPIO.setup(24, GPIO.IN)
    GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    usave()
    if IRup():
        ostate = 1
        otime = time.time()
        wait(1, oldtime)
    elif ((ostate == 1) and ((time.time() - otime) <= 300)):
        wait(10, oldtime)
    elif ((ostate == 1) and ((time.time() - otime) <= 900)):
        wait(30, oldtime)
    else:
        wait(60, oldtime)
        ostate = 0
    oldtime = time.time()
    GPIO.output(5, 1)
    temp1 = read_temp(device_file1)
    IRup()
    flash(5, 0, 0.1)
    IRup()
    temp2 = read_temp(device_file2)
    IRup()
    flash(5, 0, 0.1)
    IRup()
    #results()                    #prints results and saves to file
    date2 = '/home/pi/Desktop/Programs/Data/' + str((time.localtime()).tm_year) + "-" + str((time.localtime()).tm_mon) + "-" + str((time.localtime()).tm_mday) + '.csv'
    with open(date2, 'a') as f:
        if (f.tell() == 0):
            f.write("Day of month,Date,Vent Temperature,Ambient Temperature,Difference in Temperature,Vent Open/Closed,Power(W),Energy(kWh),Total Energy(kWh)\n")
        timedata = str(time.ctime()).split(" ")
        if (timedata[2] == ''):
            timedata[2] = timedata[3]
            timedata[3] = timedata[4]
            timedata[4] = timedata[5]
        savetime = "\"" + timedata[1] + " " + timedata[2] + ", " + timedata[4] + " " + timedata[3] + "\""
        tempdata = str((time.localtime()).tm_mday) + "," + savetime + ',' + str(round(temp1, 3)) + ',' + str(round(temp2, 3)) + ',' + str(round(abs(temp1 - temp2), 3)) + ',' + str(IRup())
        if IRup():
            if(totalen == 0):
                oldtime2 = time.time() - 2.7
            power = 1.125 * flow * (temp1 - temp2)
            energy = (power * (time.time() - oldtime2)) / 3600 / 1000
            totalen = totalen + energy
            tempdata = tempdata + ',' + str(round(power, 3)) + ',' + str(round(totalen, 3)) + ",0"
        else:
            energy = 0
            power = 0
            if (not(totalen == 0)):
              tempdata = tempdata + ",0,0," + str(round(totalen, 3))
              dayen = dayen + totalen
              totalen = 0
            else:
                tempdata = tempdata + ",0,0,0"
        print (str(round(time.time() - oldtime2, 2)) + " seconds")
        oldtime2 = time.time()
        if (startup):
            tempdata = tempdata + ",Program has started\n"
        else:
            tempdata = tempdata + '\n'
        f.write(tempdata)
    if ((time.localtime()).tm_mday != oldday.tm_mday):
        with open('/home/pi/Desktop/Programs/Data/2-DAILYDATA.csv', 'a') as f:
            f.write(str(oldday.tm_year) + '/' + str(oldday.tm_mon) + '/' + str(oldday.tm_mday) + ',' + str(round(dayen,6)) + '\n')
        oldday = time.localtime()
        dayen = 0
    print(tempdata)
            
            
    IRup()
    GPIO.output(5, 0)
    flash(5, 1, 0.1)
    flash(5, 0, 0.1)
    flash(5, 1, 0.1)
    time.sleep(0.5)                      #delay to next read
    IRup()
    startup = 0
    

GPIO.cleanup()
    




    


