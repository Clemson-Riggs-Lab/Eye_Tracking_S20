import pandas as pd
from os import path
#Sam Smith
#04/09/2020

#Reading in eye tracking and performance csv files
input_raw = input("Enter the name of a PreProcessed csv file: ") or "sET.csv"
raw = pd.read_csv(input_raw)

input_performance = input("Enter the name of a matching Performance csv: ") or "sP.csv"
performance = pd.read_csv(input_performance)


#Column numbers so accessing data is easier
UAVNumber = 7
TaskType = 6
SysTimeP = 4
SysTimeET = 47


#iloc works like this : row, col

#Coordinate fields for each UAV
#       x1    x2   y1   y2
UAV1 = [930, 1326, 194, 0]
UAV2 = [1326, 1738, 194, 0]
UAV3 = [1738, 2150, 194, 0]
UAV4 = [2150, 2560, 194, 0]

UAVs = [UAV1, UAV2, UAV3, UAV4]
system_time = 0
count = 0
coordinates = []


#returns first index found of given time in raw data 
def findFirstInstance(time):
    first = 0
    for each in raw["SystemTime"]: 
        if (each[3:10]==time):
            break
        first +=1
    return first

# Main loop for checking target data
for each in performance["TDTargetPresent"]:
    if each==1:
        print("")
        num = int(performance.iloc[count, UAVNumber])
        # Establishing coordinates of the current video feed
        #coordinates = UAVs[num]
        # finding the system time at which the target was present
        system_time = performance.iloc[count, SysTimeP]
        x=raw["SystemTime"].str.find(system_time)
        #substring of the time that we are concerned with 
        time = system_time[3:10]
        first = findFirstInstance(time)

        #using LeftPogY as an example column here, showing first 20 coordinates from 
        #the system time at which target was present
        """
        Now, just have to check coordinates of eye data with UAV coordinates in the below
        for loop.
        """
        for i in range(20):
            print(raw.iloc[first + i, 25])
    count +=1



# print(raw.iloc[0, 47])
# print(count)