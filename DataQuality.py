import pandas as pd
from os import path
import math
from datetime import time, datetime, timedelta
from tkinter import *
from os import path
import os
#Sam Smith
#04/09/2020

"""
Overall, I'd say this file is somewhat difficult to understand because there are many things
going on at once. The gist is that we are looking through a participant's performance file and 
finding when they clicked on the different tasks (target detection, reroute, chat message, fuel leak)
and checking to see that at the time of clicking those tasks, was the user actually looking where 
they clicked. This is basically a sanity check to ensure that the preprocessed data we are using to analyze is 
accurate. The goal of this file is to identify what is accurate and what isn't so we know what data
to rely on and analyze in the future. 
"""
#Column numbers in the eye tracking and performance files so accessing data is easier.
"""Pandas does allow us to access a data column directly with its name as well,
but sometimes I used these numbers to access specific cells."""
UAVNumber = 7
TaskType = 6
SysTimeP = 4
SysTimeET = 47
leftx = 24
lefty = 25


"""
These coordinates are based on the layout of the screen that the participants 
are looking at during the test. 
"""
#Coordinate fields for each UAV in the 2560 x 1440 resolution
#       x1    x2   y1   y2
UAV1 = [930, 1326, 194, 0]
UAV2 = [1326, 1738, 194, 0]
UAV3 = [1738, 2150, 194, 0]
UAV4 = [2150, 2560, 194, 0]
UAV5= [930, 1326, 194, 400]
UAV6 = [1326, 1738, 194, 400]
UAV7 = [1738, 2150, 194, 400]
UAV8 = [2150, 2560, 194, 400]
UAV9 = [930, 1326, 400, 606]
UAV10 = [1326, 1738, 400, 606]
UAV11 = [1738, 2150, 400, 606]
UAV12 = [2150, 2560, 400, 606]
UAV13 = [930, 1326, 606, 812]
UAV14 = [1326, 1738, 606, 812]
UAV15 = [1738, 2150, 606, 812]
UAV16 = [2150, 2560, 606, 812]

#This is the list of all of our UAVs
UAVs = [UAV1, UAV2, UAV3, UAV4, UAV5, UAV6, UAV7, 
        UAV8, UAV9, UAV10, UAV11, UAV12, UAV13, 
        UAV14, UAV15, UAV16]


#Global variables to help with later calculations 
system_time = ""
count = 0
coordinates = []

#returns first index found of given time in raw data
"""
This function finds the first instance of a given time in the preprocessed eye
tracking folder so that we know when the test actually started. THis is critical to
calculating the mission time, which we then use to check the participants eye data when 
they clicked certain things on the screen.
"""
def findFirstInstance(time, Raw_csv):
    first = 0
    for each in Raw_csv["NewSystemTime"]: 
        if (each[0:8] == time[0:8]):
            e_ms = int(each[9:11])
            p_ms = int(time[9:11])
            if p_ms -10 < e_ms < p_ms + 10:
                break
        first +=1
    return first

#finds first system time at which target is present in the performance file 
#This will be where mission time equals 0, because this was the time when the mission actually began
def findFirstTime(Perf_csv):
    count=0
    time = ""
    for each in Perf_csv["TDTargetPresent"]:
        if each==1:
            #system time is 4th col of performance
            time = Perf_csv.iloc[count, 4]
            break
        count+=1
    return time


#Counting number of total rows within eye tracking file 

"""
Converting the system time string into a datetime object
which allows us to more easily add time using timedeltas.
See the python datetime documentation (https://docs.python.org/3/library/datetime.html)
for more information. Depending on the boolean value, convert either a SystemTime 
or a NewSystemTime. 
"""
def convert_to_datetime(Raw_csv, row, boolean=False):
    if boolean:
        real_st = Raw_csv.at[row, "SystemTime"]
    else:
        real_st = Raw_csv.at[row, "NewSystemTime"]
    #If statement is basically checking if hours is a single digit
    if ":" in real_st[0:2]:
        hours = int(real_st[0])
        minutes = int(real_st[2:4])
        seconds = int(real_st[5:7])
        if len(real_st) ==7:
            micro=0
        else:
            micro = int(real_st[8:])

    else:
        hours = int(real_st[0:2])
        minutes = int(real_st[3:5])
        seconds = int(real_st[6:8])
        if len(real_st)==8:
            micro=0
        else:
            micro = int(real_st[9:])
    fulldate = datetime(100, 1, 1, hours, minutes, seconds, micro)
    return fulldate.time()

"""
This function allows us to add time, because this is strangely difficult 
with the provided datetime functions. The same goes for the subSecs function. 
"""
def addSecs(tm, msecs):
    #arbitrary date, its the time that matters.
    #For some reason python doesnt allow you to deal strictly with times
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second, tm.microsecond)
    fulldate = fulldate + timedelta(microseconds=msecs)
    return fulldate.time()



"""
Takes the previous value in the NewSystemTime column,
whch was initialized with a starting value as the first time in
the original system time column, and adds the difference between
the previous time and the the current time to the new system time. The 
Datetime library is strange and I ran into errors when trying to update the
NewSystemTime with time objects, so I converted them back into strings instead. 
"""
def setSystemTime(Raw_csv, total_rows):
    for i in range(1,total_rows):

        #Previous milisecond value (in microseconds)
        previous = convert_to_datetime(Raw_csv, i-1)
        #Difference between current time and previous time
        delta = float((Raw_csv.at[i, "Time"]) - (Raw_csv.at[i-1, "Time"]))
        #Converting delta into microseconds 
        #Im finding that the micro_delta multiple strongly affects the accuracy
        micro_delta = delta* 1000000
        current = addSecs(previous, micro_delta)
        prev_x = convert_to_datetime(Raw_csv, i-1, True)
        x = convert_to_datetime(Raw_csv,i, True)

        #If system time incremented by 1 second, change the    
        #New System time second to equal the system time second. 
        if prev_x.second != x.second:
            new_current = current.replace(hour=x.hour, minute=x.minute, second=x.second,microsecond=0)
           
            str_time = new_current.strftime("%H:%M:%S.%f")
            Raw_csv.at[i, "NewSystemTime"] = str_time
        else:
            str_time = current.strftime("%H:%M:%S.%f")
            Raw_csv.at[i, "NewSystemTime"] = str_time
        
            






"""
This function uses the time column in the eyetracking data to create a MissionTime 
column that matches up with the mission time in the performance csv. This allows us to more
easily pinpoint where the participant was looking throughout the mission. We are using 
MissionTime as opposed to system time because mission time is more accurate and controllable.
MissionTime is a column we created whereas SystemTime is created by the eyetracking gazepoint 
software I believe. 
"""

def setMissionTime(Raw_csv, start_index, out_file, total_rows):
    for i in range(total_rows):
        if i > start_index:
            x = (Raw_csv.at[i, "Time"]) - (Raw_csv.at[i-1, "Time"])
            Raw_csv.at[i, "MissionTime"] = float(Raw_csv.at[i-1, "MissionTime"]) + x





"""
Given x and y coordinates, this function determines which UAV the corrdinates would
fall into. Future edit may be to combine this function with the secondary task function. 
"""
def which_uav(x, y):
    counter=0
    for uav in UAVs:
        xacc= (x >= uav[0] and x <= uav[1])
        yacc = (y >= uav[2] and y <= uav[3])
        if xacc and yacc:
            return counter+1
        counter+=1
    return "Inconclusive"

#Determines if participant is looking at one of the secondary tasks
def which_secondary_task(x, y, tasks):
    counter=0
    for task in tasks:
        xacc= (x >= tasks[task][0] and x <= tasks[task][1])
        yacc = (y >= tasks[task][2] and y <= tasks[task][3])
        if xacc and yacc:
            return task
        counter+=1
    return "Inconclusive"

#Helper function that essentially uses the distance formula to find distance between two points
def calculateDistance(x1,y1,x2,y2):  
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
     return dist  



