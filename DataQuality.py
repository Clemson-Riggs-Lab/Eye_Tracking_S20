import pandas as pd
from os import path
#Sam Smith
#04/09/2020

"""
Use the "time" column to count up 6 ms intervals (delta), time zero is system time
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
def findFirstInstance(time):
    first = 0
    for each in raw["SystemTime"]: 
        if (each[3:10] == time[3:10]):
            break
        first +=1
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
    return time


#Counting number of total rows
totalRows=0
for each in raw["BestPogX"]:
    totalRows+=1

raw["MissionTime"] = 0.0
def setMissionTime(Raw_csv, start_index, outFile):
    for i in range(totalRows):
        if i > start_index:
            x = (Raw_csv.at[i, "Time"]) - (Raw_csv.at[i-1, "Time"])
            Raw_csv.at[i, "MissionTime"] = float(Raw_csv.at[i-1, "MissionTime"]) + x
    Raw_csv.to_csv(outFile, index=False)

time = findFirstTime(performance)
start = findFirstInstance(time)
#You can change output file with third parameter here 
setMissionTime(raw, start, "output1.csv")



"""
Create dictionary of the mission times (from the button clicks), assign 
coordinates as values to the mission times key 
"""
missionDict = {}
raw["DataQuality"] = False
count=0
for each in performance["TDTargetPresent"]:
    if each == 1.0:
        raw_counter=0
        clickTime = performance.iloc[count, 27]
        for mt in raw["MissionTime"]:
            #Finding where button click time and MissionTime align
            if -.01 < mt -  clickTime < .01 :
                
                uavNum = int(performance.at[count, "UAVNumber"])
                uav = UAVs[uavNum-1]

                x = raw.at[raw_counter, "BestPogX"]
                y = raw.at[raw_counter, "BestPogY"]

                xacc= (x >= uav[0] and x <= uav[1])
                yacc = (y >= uav[2] and y <= uav[3])
                """
                Value will be True if both x and y coordinates are accurate 
                according to the current UAV and False if not. 
                """
                missionDict[clickTime] = xacc and yacc
                raw.at[raw_counter, "DataQuality"] = xacc and yacc
                #stuff to help with testing 
                # print ("Coordinates at mission time " + str(mt) + " : " + str(x) + ", " + str(y))

                # if (xacc and not yacc):
                #     print("Only x is accurate")
                # if (yacc and not xacc):
                #     print("Only y is accurate")
                # if (yacc and xacc):
                #     print("Both x and y are accurate")
                # else:
                #  print("Neither are accurate")
            raw_counter+=1
    count+=1

print(missionDict)

raw.to_csv('output1.csv', index=False)

