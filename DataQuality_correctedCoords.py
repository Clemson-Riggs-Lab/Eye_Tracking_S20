import pandas as pd
from os import path
import math
from datetime import time, datetime, timedelta, date
from tkinter import *
from os import path
import os
import numpy as np

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
UAV1 = [930, 1330, 0, 195]
UAV2 = [1340, 1740, 0, 195]
UAV3 = [1750, 2150, 0, 195]
UAV4 = [2160, 2560, 0, 195]
UAV5 = [930, 1330, 205, 400]
UAV6 = [1340, 1740, 205, 400]
UAV7 = [1750, 2150, 205, 400]
UAV8 = [2160, 2560, 205, 400]
UAV9 = [930, 1330, 410, 607]
UAV10 = [1340, 1740, 410,  607]
UAV11 = [1750, 2150, 410, 607]
UAV12 = [2160, 2560, 410, 607]
UAV13 = [930, 1330,  617, 813]
UAV14 = [1340, 1740, 617, 813]
UAV15 = [1750, 2150, 617, 813]
UAV16 = [2160, 2560, 617, 813]

#This is the list of all of our UAVs
UAVs = [UAV1, UAV2, UAV3, UAV4, UAV5, UAV6, UAV7, 
        UAV8, UAV9, UAV10, UAV11, UAV12, UAV13, 
        UAV14, UAV15, UAV16]


#Global variables to help with later calculations 
system_time = ""
count = 0
coordinates = []

#testing files @Sam you can ignore this - i just toggled these lines on and off when messign with SystemTime issues 
# file="C:/Users/WHISL/Documents/NAMIEyetracking/PreprocessedEyetrackingFiles/P114T2WS_D20200305T0812Output_EyeTracker1.csv"
# df = pd.read_csv(file)
# # #REMOVING BLANK LINE FROM GAZEPOINT
# df = df[1:df.index.stop]
# df.reset_index(drop=True, inplace=True)
# inputP = "C:/Users/WHISL/Documents/NAMIEyetracking/PreprocessedEyetrackingFiles/P114T2WS_D20200305T0812Output_NewFormat_Fixed.csv"
# performance = pd.read_csv(inputP)


# def find_neighbours(value, datf, colname):
#     exactmatch = datf[datf[colname] == time]
#     if not exactmatch.empty:
#         return exactmatch.index
#     else:
#         lowerneighbour_ind = datf[datf[colname] < value][colname].index[-1]
#         upperneighbour_ind = datf[datf[colname] > value][colname].index[0]
#         return lowerneighbour_ind, upperneighbour_ind

#@Sam: I added this loop to easily change which SystemTime we wanted to make our anchor (i.e. MissionTime == 0 vs 0.02)
def find_mission_start(performance,df):
    for m in range(0,(len(performance)-1)):
        if performance.loc[m,"MissionTime"]==0 #0.02:
            index_first_perf_time = m
            first_perf_time = performance["SystemTime"][m]
            mt_first_perf_time = performance.loc[m,"MissionTime"]
            print("row",m, "is where mission time = 0.0")
            break
            
    if (len(first_perf_time)==7):
        fulldate = datetime(100, 1, 1, 1, int(first_perf_time[0:2]), int(first_perf_time[3:5]), int(first_perf_time[6]) * 100000)
    elif (len(first_perf_time) == 11):
        fulldate = datetime(100, 1, 1, int(first_perf_time[0:2]), int(first_perf_time[3:5]), int(first_perf_time[6:8]), int(first_perf_time[9:11])*10000)
    fulltime = fulldate.time()
    exactmatch = df[df["NST"] == fulltime] #@Sam: this was an attempt to be more precise with which SystemTime we say is when MissionTime == 0 (or 0.02) so looking for exact match and if not find closest (regardless if it is before or after)
    if not exactmatch.empty:
        startIndex = exactmatch.index[0]
    else:
        startIndex1 = df[df["NST"] > fulltime]["NST"].index[0] #choose the next closest NST that is greater than the true start NST
        startIndex1_time = df.loc[startIndex1,"NST"]
        difference1 = startIndex1_time.microsecond - fulltime.microsecond
        startIndex2 = df[df["NST"] < fulltime]["NST"].index[-1] #choose the next closest NST that is less than the true start NST
        startIndex2_time = df.loc[startIndex2,"NST"]
        difference2 = fulltime.microsecond - startIndex2_time.microsecond
        if difference1 <= difference2:
            startIndex = startIndex1
            mt_first_perf_time = mt_first_perf_time + (difference1/1000000)
        else:
            startIndex = startIndex2
            mt_first_perf_time = mt_first_perf_time - (difference2/1000000)
            
        
        
        # upper_ind_time_delta = datetime.timedeltas(hours=upper_ind_time.hour, minutes=upper_ind_time.minute, seconds=upper_ind_time.second, microseconds = upper_ind_time.microsecond)
        # time_delta = datetime.timedeltas(hours=time.hour, minutes=time.minute, seconds=time.second, microseconds = time.microsecond)
        # difference_delta = upper_ind_time_delta - time_delta
    
    
    # count = 0
    # startIndex=-100    
    # for each in (df["NST"]): 
    #     #Finding the first time within 1 ms
    #     if subSecs(time, 1000) <= each <= addSecs(time, 1000):
    #         startIndex=count
    #         break
    #     else:
    #         count+=1
    
    # if startIndex == -100:      
    #     time = fulldate.time()
    #     count = 0
    #     for each in (df["NST"]): 
    #         #Finding the first time within 5 ms
    #         if subSecs(time, 5000) <= each <= addSecs(time, 5000):
    #             startIndex = count
    #             break
    #         else:
    #             count+=1              
             
    #if we didn't find the start of the mission , just return the -100 
    return startIndex,mt_first_perf_time 




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

def subSecs(tm, msecs):
    #arbitrary date, its the time that matters.
    #For some reason python doesnt allow you to deal strictly with times
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second, tm.microsecond)
    fulldate = fulldate - timedelta(microseconds=msecs)
    return fulldate.time()




"""
This function uses the time column in the eyetracking data to create a MissionTime 
column that matches up with the mission time in the performance csv. This allows us to more
easily pinpoint where the participant was looking throughout the mission. We are using 
MissionTime as opposed to system time because mission time is more accurate and controllable.
MissionTime is a column we created whereas SystemTime is created by the eyetracking gazepoint 
software I believe. 
"""

def setMissionTime(df, start_index, mt_first_perf_time):
    df["MissionTime"] = mt_first_perf_time
    if not ((df.loc[2, "Time"]) - (df.loc[1, "Time"])) * 1000000 == 0:
        for i in reversed(range(0, (start_index))):
            if i < start_index:
                x = (df.loc[i+1, "Time"]) - (df.loc[i, "Time"])
                df.loc[i, "MissionTime"] = float(df.loc[i+1, "MissionTime"]) - x     
        for i in range(start_index+1, df.index.stop):
            if i > start_index:
                x = (df.loc[i, "Time"]) - (df.loc[i-1, "Time"])
                df.loc[i, "MissionTime"] = float(df.loc[i-1, "MissionTime"]) + x   
    else: #@Sam: added this loop to see if the method that we were incrementing the eye tracking file's MissionTime was causing the lag. Really no evidence that is was across the files I tested. BUT realized it was nice to have if the Time column in the eye trackign file did not have time data to the hundreths place
        print("Had to use Counter column for MissionTime incrementation")
        for i in reversed(range(0, (start_index))):
            if i < start_index:
                x = ((df.loc[i+1, "Counter"]) - (df.loc[i, "Counter"])) * .0065
                df.loc[i, "MissionTime"] = float(df.loc[i+1, "MissionTime"]) - x
        for i in range(start_index+1, df.index.stop):
            if i > start_index:
                x = ((df.loc[i, "Counter"]) - (df.loc[i-1, "Counter"])) * .0065
                df.loc[i, "MissionTime"] = float(df.loc[i-1, "MissionTime"]) + x    
    return df

def create_ST_lst(df):
    base = (df.loc[0, "SystemTime"])
    if (len(base) == 7):
        fulldate = datetime(100, 1, 1, 1, int(base[0:2]), int(base[3:5]), 0)
    elif (len(base) == 11):
        fulldate = datetime(100, 1, 1, int(base[0:2]), int(base[3:5]), int(base[6:8]), int(base[9:11])*10000)

    fulltime = fulldate.time()
    arr = [fulltime]
    # ser = pd.Series(arr)
    return arr

def deltas(df):
    dlst = []
    tm = df["Time"].tolist()
    if not float((tm[1]) - (tm[0])) * 1000000 == 0:
        for i in range(0,len(tm)):
            delta = float((tm[i]) - (tm[i-1])) * 1000000
            dlst.append(delta)
    else:
        print("Had to use Counter column for NST incrementation")
        cm = df["Counter"].tolist()
        for j in range(0,len(cm)):
            delta = (float(cm[j]-cm[j-1])) * .0065 * 1000000
            dlst.append(delta)
    return dlst

def set_NST(arr, df, delta_lst):
    for i in range(1, df.index.stop):        
        x = addSecs(arr[i-1], delta_lst[i]) 
        arr.append(x)

def add_NST_to_df(arr, df):
    df["NST"] = pd.Series(arr)


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

#@Sam: This is actually an unrelated change, but this allows MissionTime to get created for the entire dataset and not just cutoff at the 15 minutes flat (there may be a whole second of data left)

# def find_end(start, df):
#     counter = 0
#     for each in df["NST"]:
#         if(each.minute - df["NST"][start].minute == 15):
#             if(each.second == df["NST"][start].second):
#                 return counter
#         counter +=1
#     return counter


def preProcess(df):
        # Default width is 2560 and default height is 1440 for Gazepoint
        column_names_X = []
        column_names_Y = []
        column_names_bool = []
        column_names_Pupil_Diameter = []
       
        # Default width is 2560 and default height is 1440 for Gazepoint
        # Tracker used is that of experiment 1
        # all the names of the columns we want to convert proportions to pixels for
        width_of_screen = int(2560)
        height_of_screen = int(1440)
        column_names_X = ['CursorX', 'LeftEyeX', 'RightEyeX', 'FixedPogX', 'LeftPogX', 'RightPogX', 'BestPogX',
                            'LeftPupilX', 'RightPupilX']
        column_names_Y = ['CursorY', 'LeftEyeY', 'RightEyeY', 'FixedPogY', 'LeftPogY', 'RightPogY', 'BestPogY',
                            'LeftPupilY', 'RightPupilY']
        column_names_bool = ['LeftEyePupilValid', 'RightEyePupilValid', 'FixedPogValid', 'LeftPogValid',
                                'RightPogValid', 'BestPogValid', 'LeftPupilValid', 'RightPupilValid', 'MarkerValid']
        column_names_Pupil_Diameter = ['LeftEyePupilDiamet', 'RightEyePupilDiame']

        # turn TRUES and FALSES to 1s and 0s
        for each in column_names_bool:
            df[each].replace(True, 1, inplace=True)
            df[each].replace(False, 0, inplace=True)
        # CHANGE RESOLUTION OF X HERE
        for each in column_names_X:
            df[each] = df[each].multiply(width_of_screen)

        # CHANGE RESOLUTION OF Y HERE
        for each in column_names_Y:
            df[each] = df[each].multiply(height_of_screen)
            
def dq(df, inputP, xError, yError):
            #REMOVING BLANK LINE FROM GAZEPOINT
            df = df[1:df.index.stop]
            df.reset_index(drop=True, inplace=True)
            
            #if there is a blank line in performance, you can repeat the above two lines
            #with performance in place of df
            performance = pd.read_csv(inputP)

           
            
            arr = create_ST_lst(df)
            ds = deltas(df)
            set_NST(arr, df, ds)
            add_NST_to_df(arr, df)
            start, mt_start = find_mission_start(performance, df)
            #end = find_end(start, df)
            setMissionTime(df, start, mt_start) #, end)
            Time0Index=df[((df["MissionTime"])>=0)].index[0] #& ((df["MissionTime"]<0.007))
                      
                        
            """
            Data Quality section, tester data immediately below
            """
            #testing files for data quality with event detection data @Sam you can ignore this block
            # file="C:/Users/WHISL/Documents/NAMIEyetracking/EventDetectionEyetrackingFiles/P115_T2_M_Out2.csv"
            # df = pd.read_csv(file)
            # df.rename(columns = {'Event Type':'Event_Type', 'Start time (s)':'MissionTime', 'X':'BestPogX', 'Y':'BestPogY'}, inplace = True) 
            # df = df[df.Event_Type != "Saccade"]
            # df.reset_index(drop=True, inplace=True)
            
            # inputP = "C:/Users/WHISL/Documents/NAMIEyetracking/PreprocessedEyetrackingFiles/P115T1WG_D20200305T0806Output_NewFormat_Fixed.csv"
            # performance = pd.read_csv(inputP)
            
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
                        if -.01 <= (mt - clickTime) <= .01: #only checking eye tracking data 0.01 seconds before and after click time of target task
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
            RRPanel = [0, 910, 0, 1440] #@Sam: I changed this to include Map panel because participants could have been looking at map and using peripheral vision to check alternate routes
            FLPanel = [930, 2560, 830, 1158]
            CMPanel = [930, 2560, 1180, 1440]
            task_dict = {"RRTimeofRR" :RRPanel, "FLStopTime":FLPanel, "MessageTime":CMPanel}
            for task in task_dict:
                perf_counter=0
                for each in performance[task]:
                   
                    if not pd.isnull(each):
                        if task == "MessageTime":
                            if (performance.at[perf_counter,"MessageFrom"] != 'user'):
                                perf_counter+=1
                               #print(each)
                                continue #@Sam: ignore this code - i thought DQ was running for incorrect chat message responses, but it was not
                            # if (performance.at[perf_counter,"MessageAnswerAccuracy"] != 1):
                            #     perf_counter+=1
                            #     #print(each)
                            #     continue
                            
                            
                        raw_counter=0
                        for mt in df["MissionTime"]:
                            if (-.5 <= mt - each <= .5): #only checking eye tracking data 0.5 seconds before and after click time of target task
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
            # percent_accurate = number_true/number_analyzed
            # summary_stats = open("quality_summary.txt", 'w')
            # summary_stats.write("The data was "+ str(100 * percent_accurate) + " percent accurate.\n")
            # summary_stats.write("Of the "+ str(number_analyzed)+  " data points analyzed, " + str(number_true)+" data points were accurate while " + str(number_false) + " were inaccurate." )
            # summary_stats.close()
            #returning from mission time start to the 900th point after that
            """
            Important to note that this function no longer puts the dataframe 
            into an output file. It just returns a dataframe. 
            """
            """
            TODO: Change the return df to return 900 seconds after starting point
            """
            return df[Time0Index:df.index.stop]

#@Sam: Trash/trial code, just ignore
#df.to_csv("P115_G_DQwithED.csv", index=False)

# performance2 = performance[performance.TaskType != "TargetDetection"]
# performance2.reset_index(drop=True, inplace=True)
# arr2 = create_ST_lst(performance2)
# dlst = []
# tm = performance2["MissionTime"].tolist()
# for i in range(0,len(tm)):
#     delta = float((tm[i]) - (tm[i-1])) * 1000000
#     dlst.append(delta)

# set_NST(arr2, performance2, dlst)
# add_NST_to_df(arr2, performance2)
# perforamnce2 = performance2[["SystemTime","MissionTime","NST"]]


# convert_dict = {'SystemTime': datetime64[ns], 
#                 'NST': datetime64[ns]
#                } 
  
# df = df.astype(convert_dict) 
# print(df.dtypes) 

# df['NST'] = df['NST'].astype('datetime64[ns]')

# df.to_csv("P100_S_compare16.csv", index=False, date_format='%HH:%MM:%SS:%MS')

# df["NST"] = pd.to_datetime(df["NST"])
