import pandas as pd
from os import path
import math
from datetime import time, datetime, timedelta
from tkinter import *
from os import path
import os
#Sam Smith
#04/09/2020


#Column numbers in the eye tracking and performance files so accessing data is easier.
"""Pandas does allow us to access a data column directly with its name as well,
but sometimes I used these numbers to access specific cells."""
UAVNumber = 7
TaskType = 6
SysTimeP = 4
SysTimeET = 47
leftx = 24
lefty = 25


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
This function is still being changed around given that the system time column 
in the eye tracking data seems to be causing problems. 
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
for more information. 
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
    # time = fulldate.strftime("%H:%M:%S.%f")
    return fulldate.time()

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
the previous time and the the current time to the new system time.
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
easily pinpoint where the participant was looking throughout the mission. 
"""

def setMissionTime(Raw_csv, start_index, out_file, total_rows):
    for i in range(total_rows):
        if i > start_index:
            x = (Raw_csv.at[i, "Time"]) - (Raw_csv.at[i-1, "Time"])
            Raw_csv.at[i, "MissionTime"] = float(Raw_csv.at[i-1, "MissionTime"]) + x





"""
Given x and y coordinates, this function determines which UAV the corrdinates would
fall into. 
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



"""
The function that is called in the GUI. This is the back end 
of the program that contains most of the logic. 
"""
def dq():
            if inputET_name.get() == '' or not os.path.isfile(inputET_name.get()):
                raw = pd.read_csv("2ndTask_ET.csv")
            else:
                raw = pd.read_csv(inputET_name.get())
            
            if inputP_name.get() == '' or not os.path.isfile(inputP_name.get()):
                performance = pd.read_csv("2ndTask_P.csv")
            else:
                performance = pd.read_csv(inputP_name.get())

            # if output_name.get() == '' or not os.path.isfile(output_name.get()):
            #     output_file_name = "output1.csv"
            # else:
            #     output_file_name = output_name.get()
            output_file_name = output_name.get()
            #Gathering user input for error calculating the valid field of view for participants eyes.
            """
            Essentially, the error that the user inputs is used to extend the bounds that we would
            consider to be acceptably accurate. For example, if a video feed's x coordinates were 
            200 to 1000, an xError of 50 would mean that any eye data in the x direction
            within the window of 150 to 1050 pixels would considered as accurate. This applies
            to the y direction as well.  
            """
            try: 
                int(xError.get())
                input_xError = int(xError.get())
            except:
                input_xError = 0

            try: 
                int(yError.get())
                input_yError = int(yError.get())
            except:
                input_yError = 0
          
            totalRows=0
            for each in raw["BestPogX"]:
                totalRows+=1

            raw["NewSystemTime"] = ""
            raw.at[0, "NewSystemTime"]= raw.at[0, "SystemTime"]+ ".0"
            setSystemTime(raw, totalRows)
            # 7:47:35.0
            #Calling the setMissionTime function below 
            time = findFirstTime(performance)
            start = (findFirstInstance(time, raw))
            print("starting mission time at: "+ str(start)) 
            #You can change output file with third parameter here 
            raw["MissionTime"] = 0.0

            setMissionTime(raw, start, output_file_name, totalRows)
            raw.to_csv(output_file_name, index=False)
            """
            Create dictionary of the mission times (from the button clicks), assign 
            coordinates as values to the mission times key 
            """
            missionDict = {}
            #Tells us if target detection was accurate
            raw["DataAccurate"] = ""
            #Tells which uav the target appeared in
            raw["Task"] = ""
            #Tells us which uav the participant was looking at
            raw["Qualitative"] = "N/A"

            """
            Uses distance formula to calculate how far eye coordinates are 
            from the center of a video feed
            """
            raw["DistanceFromCenter"] = 0



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
                    for mt in raw["MissionTime"]:
                        #Finding where button click time and MissionTime align
                        if -.01 <= mt -  clickTime <= .01 :
                            #print(raw.at[raw_counter, "BestPogY"])
                            number_analyzed+=1
                            uavNum = int(performance.at[count, "UAVNumber"])
                            uav = UAVs[uavNum-1]
                            x = raw.at[raw_counter, "BestPogX"]
                            y = raw.at[raw_counter, "BestPogY"]

                            #Now accuracy takes the errors into account 
                            xacc= (x >= uav[0] - input_xError and x <= uav[1] + input_xError)
                            yacc = (y >= uav[2] - input_yError and y <= uav[3] + input_yError)
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
                            raw.at[raw_counter, "DataAccurate"] = xacc and yacc
                            raw.at[raw_counter, "Task"] = "Target detection task for UAV " + str(uavNum)
                            raw.at[raw_counter, "Qualitative"] = "Participant was looking at UAV " + str(cur_uav)
                            raw.at[raw_counter, "DistanceFromCenter"] = calculateDistance(centerx,centery,x,y)

                        raw_counter+=1
                count+=1

            print(missionDict)

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
                        for mt in raw["MissionTime"]:
                            if (-.01 <= mt- each <= .01):
                                number_analyzed+=1
                                x = raw.at[raw_counter, "BestPogX"]
                                y = raw.at[raw_counter, "BestPogY"]
                                xacc= (x >= task_dict[task][0] - input_xError and x <= task_dict[task][1] + input_xError)
                                yacc = (y >= task_dict[task][2] - input_yError and y <= task_dict[task][3] + input_yError)

                                centerx = (task_dict[task][0] + task_dict[task][1])/2
                                centery = (task_dict[task][2] + task_dict[task][3])/2
                                raw.at[raw_counter, "Task"] = "Secondary detection task for "+ task
                                raw.at[raw_counter, "DataAccurate"] = xacc and yacc
                                raw.at[raw_counter, "DistanceFromCenter"] = calculateDistance(centerx,centery,x,y)
                                
                                if xacc and yacc:
                                    number_true+=1
                                    raw.at[raw_counter, "Qualitative"] = "Participant was correctly looking at the " + task
                                else: 
                                    cur_uav = which_uav(x, y)
                                    number_false+=1
                                    if cur_uav == "Inconclusive":
                                        cur_task = which_secondary_task(x, y, task_dict)
                                        if cur_task=="Inconclusive":
                                            raw.at[raw_counter, "Qualitative"] = "Unable to pinpoint participant's gaze location."
                                        else:
                                            raw.at[raw_counter, "Qualitative"] = "Participant was looking at "+ cur_task
                                    else:
                                        raw.at[raw_counter, "Qualitative"] = "Participant was looking at "+ str(cur_uav)
                            raw_counter+=1
                    perf_counter+=1
           
            raw.to_csv(output_file_name, index=False)
            text6.configure(text='Status: Success! The output file now shows data quality information.')
            #Creating summary statistics file
            percent_accurate = number_true/number_analyzed
            summary_stats = open("quality_summary.txt", 'w')
            summary_stats.write("The data was "+ str(100 * percent_accurate) + " percent accurate.\n")
            summary_stats.write("Of the "+ str(number_analyzed)+  " data points analyzed, " + str(number_true)+" data points were accurate while " + str(number_false) + " were inaccurate." )
            summary_stats.close()

# UI things
window = Tk()
frame0 = Frame(window)
frame1 = Frame(window)
frame2 = Frame(window)
frame3 = Frame(window)
frame4 = Frame(window)
frame5 = Frame(window)
frame6 = Frame(window)
frame7 = Frame(window)

frame0.pack()
frame1.pack()
frame2.pack()
frame3.pack()
frame4.pack()
frame5.pack()
frame6.pack()
frame7.pack()

window.title("Data Quality GUI")

text0 = Label(frame0, text='Enter Eyetracking file name: ')
text0.pack(side=LEFT)
inputET_name = Entry(frame0)
inputET_name.pack(side=LEFT)

text1 = Label(frame1, text='Enter Performance file name: ')
text1.pack(side=LEFT)
inputP_name = Entry(frame1)
inputP_name.pack(side=LEFT)

text2 = Label(frame2, text='Enter Output file name: ')
text2.pack(side=LEFT)
output_name = Entry(frame2)
output_name.pack(side=LEFT)

text3 = Label(frame3, text='Enter horizontal (x) margin of error value [pixels]: ')
text3.pack(side=LEFT)
xError=Entry(frame3)
xError.pack(side=LEFT)

text4 = Label(frame4, text='Enter vertical (y) margin of error value [pixels]: ')
text4.pack(side=LEFT)
yError=Entry(frame4)
yError.pack(side=LEFT)

note = Label(frame5, text='Note: Margin of error refers to how far a gaze point can be from the boundary and still be classified as an accurate gaze point')
note.pack()
button1 = Button(frame6, text='Submit',command=dq)
button1.pack(side=RIGHT)

text6 = Label(frame7, text='Status: N/A')
text6.pack()

window.mainloop()

