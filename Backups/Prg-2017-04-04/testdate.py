import time

def IRup():
    return 1

temp1 = 20
temp2 = 22
flow = 47
oldtime = time.time() - 60
oldtime2 = time.time()
ostate = 0
startup = 1
flow = 47
energy = 0
totalen = 0
power = 0
while 1:
    date2 = '/home/pi/Desktop/Programs/Data/' + str((time.localtime()).tm_year) + "-" + str((time.localtime()).tm_mon) + "-" + str((time.localtime()).tm_mday) + '.csv'
    with open(date2, 'a') as f:
            if (f.tell() == 0):
                print "New file"
                f.write("Day of month,Date,Vent Temperature,Ambient Temperature,Difference in Temperature,Vent Open/Closed,Power(W),Energy(kWh),Total Energy(kWh)\n")
            timedata = str(time.ctime()).split(" ")
            savetime = "\"" + timedata[1] + " " + timedata[2] + ", " + timedata[4] + " " + timedata[3] + "\""
            tempdata = str((time.localtime()).tm_mday) + "," + savetime + ',' + str(round(temp1, 3)) + ',' + str(round(temp2, 3)) + ',' + str(round(abs(temp1 - temp2), 3)) + ',' + str(IRup())
            if IRup():
                power = 1.125 * flow * (temp1 - temp2)
                energy = (power * (time.time() - oldtime2)) / 3600
                totalen = totalen + energy
                tempdata = tempdata + ',' + str(round(power, 3)) + ',' + str(round(totalen, 3)) + ",0"
            else:
                energy = 0
                power = 0
                if (not(totalen == 0)):
                  tempdata = tempdata + ",0,0," + str(round(totalen, 3))
                  totalen = 0
                else:
                    tempdata = tempdata + ",0,0,0"
            if (startup):
                tempdata = tempdata + ",Program has started\n"
            else:
                tempdata = tempdata + '\n'
            f.write(tempdata)
            print("DONE")
            time.sleep(1)
            startup = 0
