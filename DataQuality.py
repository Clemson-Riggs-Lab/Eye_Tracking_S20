import pandas as pd
from os import path
import math
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
while True:
    try:  
        input_raw = input("Enter the name of a PreProcessed csv file: ") or "2ndTask_ET.csv"
        raw = pd.read_csv(input_raw)
        break
    except:
        print("Invalid eye tracking file (must be in csv format).")

while True:
    try:
        input_performance = input("Enter the name of a matching Performance csv: ") or "2ndTask_P.csv"
        performance = pd.read_csv(input_performance)
        break
    except:
        print("Invalid performance file (must be in csv format).")


#Gathering user input for error in calculating times and
xError= float(input("Enter the desired level of error for the x direction: ") or "0")
yError = float(input("Enter the desired level of error for the y direction: ") or "0")

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
        if (each[2:7] == time[3:8]):
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

time = findFirstTime(performance)
print(time[0:10])

#Not returning correct start index.
#I think this is because system time in performance file is more accurate

start = findFirstInstance(time)
#You can change output file with third parameter here 

setMissionTime(raw, start, "output1.csv")
raw.to_csv('output1.csv', index=False)


def which_uav(x, y):
    counter=0
    for uav in UAVs:
        xacc= (x >= uav[0] and x <= uav[1])
        yacc = (y >= uav[2] and y <= uav[3])
        if xacc and yacc:
            return counter+1
        counter+=1
    return "Inconclusive"



def calculateDistance(x1,y1,x2,y2):  
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
     return dist  

"""
Create dictionary of the mission times (from the button clicks), assign 
coordinates as values to the mission times key 
"""
missionDict = {}
#Tells us if target detection was accurate
raw["DataQuality"] = False
#Tells which uav the target appeared in
raw["TD_Task"] = ""
#Tells us which uav the participant was looking at
raw["Qualitative"] = "N/A"

"""
Uses distance formula to calculate how far eye coordinates are 
from the center of a video feed
"""
raw["DistanceFromCenter"] = 0

count=0
for each in performance["TDTargetPresent"]:
    if each == 1.0:
        raw_counter=0
        clickTime = performance.iloc[count, 27]
        for mt in raw["MissionTime"]:
            #Finding where button click time and MissionTime align
            if -.01 <= mt -  clickTime <= .01 :
                #print(raw.at[raw_counter, "BestPogY"])
                uavNum = int(performance.at[count, "UAVNumber"])
                uav = UAVs[uavNum-1]

                x = raw.at[raw_counter, "BestPogX"]
                y = raw.at[raw_counter, "BestPogY"]

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
                if -.01 < mt -  clickTime < .01:
                    missionDict[clickTime] = xacc and yacc
                
                cur_uav = which_uav(x, y)

                #Calculating how far away the coordinates are from either 
                #the upper or lower bound of the uav feed

                centerx = (uav[0] + uav[1])/2
                centery = (uav[2] + uav[3])/2


                #Updating the output csv file
                raw.at[raw_counter, "DataQuality"] = xacc and yacc
                raw.at[raw_counter, "TD_Task"] = "Target detection task for UAV " + str(uavNum)
                raw.at[raw_counter, "Qualitative"] = "Participant was looking at UAV " + str(cur_uav)
                raw.at[raw_counter, "DistanceFromCenter"] = calculateDistance(centerx,centery,x,y)

            raw_counter+=1
    count+=1

print(missionDict)

#Coordinates for the reroute menu 
RRPanel = [0, 920, 930, 1440]
for each in performance["RRTimeofRR"]:
    if not pd.isnull(each):
        raw_counter=0
        for mt in raw["MissionTime"]:
            if (-.01 <= mt- each <= .01):
                x = raw.at[raw_counter, "BestPogX"]
                y = raw.at[raw_counter, "BestPogY"]
                xacc= (x >= RRPanel[0] - xError and x <= RRPanel[1] + xError)
                yacc = (y >= RRPanel[2] - yError and y <= RRPanel[3] + yError)
                # print(str(x) + ", " + str(y))

                centerx = (RRPanel[0] + RRPanel[1])/2
                centery = (RRPanel[2] + RRPanel[3])/2
                raw.at[raw_counter, "TD_Task"] = "Secondary detection task for reroute panel"
                raw.at[raw_counter, "DataQuality"] = xacc and yacc
                raw.at[raw_counter, "DistanceFromCenter"] = calculateDistance(centerx,centery,x,y)

            raw_counter+=1

FLPanel = [920, 2560, 812 ,1158]
for each in performance["FLStopTime"]:
    if not pd.isnull(each):
        raw_counter=0
        for mt in raw["MissionTime"]:
            if (-.01 <= mt- each <= .01):
                x = raw.at[raw_counter, "BestPogX"]
                y = raw.at[raw_counter, "BestPogY"]
                xacc= (x >= FLPanel[0] - xError and x <= FLPanel[1] + xError)
                yacc = (y >= FLPanel[2] - yError and y <= FLPanel[3] + yError)
                # print(str(x) + ", " + str(y))
                centerx = (FLPanel[0] + FLPanel[1])/2
                centery = (FLPanel[2] + FLPanel[3])/2
                raw.at[raw_counter, "TD_Task"] = "Secondary detection task for Fuel Leak panel"
                raw.at[raw_counter, "DataQuality"] = xacc and yacc
                raw.at[raw_counter, "DistanceFromCenter"] = calculateDistance(centerx,centery,x,y)

            
            raw_counter+=1

CMPanel = [920, 2560, 1158 ,1440]
perf_counter=0
for each in performance["MessageTime"]:
    if not pd.isnull(each):
        if (performance.at[perf_counter,"MessageFrom"] == 'user'):
            print("user")
            raw_counter=0

            for mt in raw["MissionTime"]:
                if (-.01 <= mt- each <= .01):
                    x = raw.at[raw_counter, "BestPogX"]
                    y = raw.at[raw_counter, "BestPogY"]
                    xacc= (x >= CMPanel[0] - xError and x <= CMPanel[1] + xError)
                    yacc = (y >= CMPanel[2] - yError and y <= CMPanel[3] + yError)
                    # print(str(x) + ", " + str(y))
                    centerx = (CMPanel[0] + CMPanel[1])/2
                    centery = (CMPanel[2] + CMPanel[3])/2
                    raw.at[raw_counter, "TD_Task"] = "Secondary detection task for Chat Message panel"
                    raw.at[raw_counter, "DataQuality"] = xacc and yacc
                    raw.at[raw_counter, "DistanceFromCenter"] = calculateDistance(centerx,centery,x,y)

                raw_counter+=1
    perf_counter+=1
raw.to_csv('output1.csv', index=False)

