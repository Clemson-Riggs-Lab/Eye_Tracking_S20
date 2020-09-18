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

def setMissionTime(Raw_csv, start_index, total_rows):
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



def dq(df, inputP, xError, yError):
          
            
            performance = pd.read_csv(inputP)

           
            
            #Gathering user input for error calculating the valid field of view for participants eyes.
            """
            Essentially, the error that the user inputs is used to extend the bounds that we would
            consider to be acceptably accurate. For example, if a video feed's x coordinates were 
            200 to 1000, an xError of 50 would mean that any eye data in the x direction
            within the window of 150 to 1050 pixels would considered as accurate. This applies
            to the y direction as well.  
            """
           
          
            totalRows=0
            for each in df["BestPogX"]:
                totalRows+=1

            df["NewSystemTime"] = ""
            df.at[0, "NewSystemTime"]= df.at[0, "SystemTime"]+ ".0"
            setSystemTime(df, totalRows)
            #Calling the setMissionTime function below 
            time = findFirstTime(performance)
            start = (findFirstInstance(time, df))
            print("starting mission time at: "+ str(start)) 
            #You can change output file with third parameter here 
            df["MissionTime"] = 0.0

            setMissionTime(df, start, totalRows)
            # raw.to_csv(output, index=False)
            """
            Create dictionary of the mission times (from the button clicks), assign 
            coordinates as values to the mission times key 
            """
            missionDict = {}
            #Tells us if target detection was accurate
            df["DataAccurate"] = ""
            #Tells which uav the target appeared in
            df["Task"] = ""
            #Tells us which uav the participant was looking at
            df["Qualitative"] = "N/A"

            """
            Uses distance formula to calculate how far eye coordinates are 
            from the center of a video feed or secondary task.
            """
            df["DistanceFromCenter"] = 0



            """
            When there is a target present, this loop looks at the mission time, finds a matching time in the 
            eye tracking file's mission time file (or a time that is very close to the same) and checks that the 
            participants eyes are looking in the correct area. This logic is repeated for the secondary tasks below. 
            """
            number_true = 0
            number_false = 0
            number_analyzed=0
            count=0
            for each in performance["TDTargetPresent"]:
                if each == 1.0:
                    raw_counter=0
                    clickTime = performance.iloc[count, 27]
                    for mt in df["MissionTime"]:
                        #Finding where button click time and MissionTime align
                        if -.01 <= mt -  clickTime <= .01 :
                            #print(raw.at[raw_counter, "BestPogY"])
                            number_analyzed+=1
                            uavNum = int(performance.at[count, "UAVNumber"])
                            uav = UAVs[uavNum-1]
                            x = df.at[raw_counter, "BestPogX"]
                            y = df.at[raw_counter, "BestPogY"]

                            #Now accuracy takes the errors into account 
                            xacc= (x >= uav[0] - xError and x <= uav[1] + xError)
                            yacc = (y >= uav[2] - yError and y <= uav[3] + yError)
                            """
                            Value will be True if both x and y coordinates are accurate 
                            according to the current UAV and False if not. 
                            """

                            """
                            Below if statement ensures that only a time that is close
                            to clickTime will be used for the dictionary so we can pinpoint 
                            accuracy at exact clicktime.
                            """
                            if xacc and yacc:
                                number_true +=1
                            else:
                                number_false+=1
                            if -.01 < mt -  clickTime < .01:
                                missionDict[clickTime] = xacc and yacc
                            
                            cur_uav = which_uav(x, y)

                            #Calculating how far away the coordinates are from either 
                            #the upper or lower bound of the uav feed

                            centerx = (uav[0] + uav[1])/2
                            centery = (uav[2] + uav[3])/2


                            #Updating the output csv file
                            df.at[raw_counter, "DataAccurate"] = xacc and yacc
                            df.at[raw_counter, "Task"] = "Target detection task for UAV " + str(uavNum)
                            df.at[raw_counter, "Qualitative"] = "Participant was looking at UAV " + str(cur_uav)
                            df.at[raw_counter, "DistanceFromCenter"] = calculateDistance(centerx,centery,x,y)

                        raw_counter+=1
                count+=1

            # print(missionDict)

            """
            Here, we repeat the logic used for target detection but in the context of 
            the secondary tasks. 
            """
            RRPanel = [0, 920, 930, 1440]
            FLPanel = [920, 2560, 812 ,1158]
            CMPanel = [920, 2560, 1158 ,1440]
            task_dict = {"RRTimeofRR" :RRPanel, "FLStopTime":FLPanel, "MessageTime":CMPanel}
            for task in task_dict:
                perf_counter=0
                for each in performance[task]:
                   
                    if not pd.isnull(each):
                        if task == "MessageTime":
                            if (performance.at[perf_counter,"MessageFrom"] != 'user'):
                                perf_counter+=1
                                continue
                            
                            
                        raw_counter=0
                        for mt in df["MissionTime"]:
                            if (-.01 <= mt- each <= .01):
                                number_analyzed+=1
                                x = df.at[raw_counter, "BestPogX"]
                                y = df.at[raw_counter, "BestPogY"]
                                xacc= (x >= task_dict[task][0] - xError and x <= task_dict[task][1] + xError)
                                yacc = (y >= task_dict[task][2] - yError and y <= task_dict[task][3] + yError)

                                centerx = (task_dict[task][0] + task_dict[task][1])/2
                                centery = (task_dict[task][2] + task_dict[task][3])/2
                                df.at[raw_counter, "Task"] = "Secondary detection task for "+ task
                                df.at[raw_counter, "DataAccurate"] = xacc and yacc
                                df.at[raw_counter, "DistanceFromCenter"] = calculateDistance(centerx,centery,x,y)
                                
                                if xacc and yacc:
                                    number_true+=1
                                    df.at[raw_counter, "Qualitative"] = "Participant was correctly looking at the " + task
                                else: 
                                    cur_uav = which_uav(x, y)
                                    number_false+=1
                                    if cur_uav == "Inconclusive":
                                        cur_task = which_secondary_task(x, y, task_dict)
                                        if cur_task=="Inconclusive":
                                            df.at[raw_counter, "Qualitative"] = "Unable to pinpoint participant's gaze location."
                                        else:
                                            df.at[raw_counter, "Qualitative"] = "Participant was looking at "+ cur_task
                                    else:
                                        df.at[raw_counter, "Qualitative"] = "Participant was looking at "+ str(cur_uav)
                            raw_counter+=1
                    perf_counter+=1
           
            # raw.to_csv(output, index=False)
            #Creating summary statistics file (STILL IN PROGRESS)
            percent_accurate = number_true/number_analyzed
            summary_stats = open("quality_summary.txt", 'w')
            summary_stats.write("The data was "+ str(100 * percent_accurate) + " percent accurate.\n")
            summary_stats.write("Of the "+ str(number_analyzed)+  " data points analyzed, " + str(number_true)+" data points were accurate while " + str(number_false) + " were inaccurate." )
            summary_stats.close()
            #returning from mission time start to the 900th point after that
            """
            Important to note that this function no longer puts the dataframe 
            into an output file. It just returns a dataframe. 
            """
            return df[start:start+900]

