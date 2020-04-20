import pandas as pd
from os import path
#Sam Smith
#04/09/2020

"""
Use the "time" column to count up 6 ms intervals, time zero is system time
at which first target appears. Then, look at the TDbuttonclick time on 
performance file to find the row at that same time in that column we created
in raw data. In that row, look at best pog x and y, and compare that to the UAV
video feed coordinates of the UAV whose target they clicked. 
"""

#Reading in eye tracking and performance csv files, just press enter for default values
input_raw = input("Enter the name of a PreProcessed csv file: ") or "FakeEyetrackOutput.csv"
raw = pd.read_csv(input_raw)

input_performance = input("Enter the name of a matching Performance csv: ") or "FakePerform.csv"
performance = pd.read_csv(input_performance)


#Column numbers so accessing data is easier
UAVNumber = 7
TaskType = 6
SysTimeP = 4
SysTimeET = 47
leftx = 24
lefty = 25

#iloc works like this : row, col

#Coordinate fields for each UAV
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

UAVs = [UAV1, UAV2, UAV3, UAV4, UAV5, UAV6, UAV7, 
        UAV8, UAV9, UAV10, UAV11, UAV12, UAV13, 
        UAV14, UAV15, UAV16]
system_time = ""
count = 0
coordinates = []

#returns first index found of given time in raw data 
#METHOD IS NOT WORKING
def findFirstInstance(time):
    first = 0
    for each in raw["SystemTime"]: 
        if (each[3:10] == time[3:10]):
            break
        first +=1
    print(first)
    return first

#finds first system time at which target is present
#This will be where mission time equals 0 
def findFirstTime(Perf_csv):
    count=0
    time = ""
    for each in Perf_csv["TDTargetPresent"]:
        if each==1:
            #system time is 4th col of performance
            time = Perf_csv.iloc[count, 4]
            break
        count+=1
    print(time)
    return time

raw["MissionTime"] = 0.0
#How to update output at each iteration quickly?
def setMissionTime(Raw_csv, start_index):
    #LENGTH OF FAKE DATA IS CURRENTLY HARD CODED
    for i in range(2571):
        if i > start_index:
            # Raw_csv.replace(to_replace = [Raw_csv["MissionTime"][i]],
            # value = (Raw_csv["MissionTime"][i] - Raw_csv["MissionTime"][i-1]))
            x = (Raw_csv.at[i, "Time"]) - (Raw_csv.at[i-1, "Time"])
            Raw_csv.at[i, "MissionTime"] = float(Raw_csv.at[i-1, "MissionTime"]) + x
    Raw_csv.to_csv('output1.csv', index=False)

time = findFirstTime(performance)
start = findFirstInstance(time)
setMissionTime(raw, start)
print(raw["MissionTime"])

# for each in performance["TDTargetPresent"]:
#     if each==1:
#         print("")
#         num = int(performance.iloc[count, UAVNumber])
#         # Establishing coordinates of the current video feed
#         coordinates = UAVs[num-1]
#         # finding the system time at which the target was present
#         system_time = performance.iloc[count, SysTimeP]
#         #substring of the time that we are concerned with 
#         time = system_time
#         first = findFirstInstance(time)

        #using LeftPogY as an example column here, showing first 20 coordinates from 
        #the system time at which target was present
        # """
        # Now, just have to check coordinates of eye data with UAV coordinates in the below
        # for loop. Using left eye data. 
        # """
        # for i in range(100,120):
        #     datax = raw.iloc[first + i, leftx]
        #     datay = raw.iloc[first + i, lefty]

        #     xacc = (datax <= coordinates[1] and datax >= coordinates[0])
        #     yacc = (datay <= coordinates[3] and datay >= coordinates[2])


        #     if (xacc and not yacc):
        #         print("Only x is accurate")
        #     if (yacc and not xacc):
        #         print("Only y is accurate")
        #     if (yacc and xacc):
        #         print("Both x and y are accurate")
        #     else:
        #         print("Neither are accurate")



            # print(datax)

    # count+=1
