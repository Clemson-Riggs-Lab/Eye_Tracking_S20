# import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

"""
Created on Thu Jul 23 18:50:45 2020

23/07/2020: Jad peaks + onsets
24/07/2020: refined + comments + graphs
25/07/2020: offsets + saccade detection (onsets,offsets, and duration)

@author: Jad Atweh
"""
#Open in Jupyter

"""
Those values are placed just to come up with the logic and proceed.
We import them from the excel files after calculating the velocites 
"""



"""
I tried to imitate the actual graph (I focused on saccades and glissade peaks for now not on fixations). 
That's why fixations are short as not my purpose now
"""

# time = [0,17,33,49,65,81,98,114,130,146,162,179,195,211,227,244,260,278,294,310,326,342,358,375,391,407,423,439,456,472,488,504,520,536,569,585,601,617,633,650,666,682,699,715,731,747,763,779,796,812,828,844,860,876,893,909,926,942,959,974,990,1007,1023,1039,1055,1071,1088,1104,1121,1137,1153,1169,1185,1201,1218,1234,1250,1266,1282,1299,1315,1331,1349,1363,1380]
# velocities = [60,54,50,37,30,45,80,100,114,137,150,142,133,128,117,90,75,60,45,55,33,36,37,36,45,60,75,80,105,140,165,140,127,120,95,90,75,65,50,75,35,36,37,36,37,45,60,80,96,110,140,160,145,140,125,100,88,70,55,43,30,41,55,60,39,36,38,35,60,77,90,110,135,145,120,105,90,71,60,50,40,33,37,43,55]

df = pd.read_csv("ED_practice.csv")
velocities = df["Angular Velocity (in degrees/second)"]
time = df["MissionTime"]
#I chose any numbers until we determine the velocity threshold, onset and offset thresholds
#arbitrary values, PT will be determined before (each participant has a different PT for a different load)
PT=100
onset_threshold = 40
offset_threshold = 60

#those will be changed at the end to add in the excel file or in a text file
onsets_times = []
onsets_velocities = []
offsets_times = []
offsets_velocities = [] 
offsets=[]
peak_times = []
peaks = [] 

indices = find_peaks(velocities, height = PT)[0]


#I drew this plot to visually see the peaks and follow each point. The velocities VS time plot is below
# fig = go.Figure()
# fig.add_trace(go.Scatter(
#     y=velocities,
#     mode='lines+markers',
#     name='Original Plot'
# ))

# fig.add_trace(go.Scatter(
#     x=indices,
#     y=[velocities[j] for j in indices],
#     mode='markers',
#     marker=dict(
#         size=8,
#         color='red',
#         symbol='cross'
#     ),
#     name='Detected Peaks'
# ))
#this shows a graph of velocites as a function of indices of the velocities as the the function 
#returns the index of the velocity in the list not the time
#I added below a new list for the peak times

print (len(indices),'peaks were detected')
for i in range(len(indices)): 
    r=indices[i]
    peak_times.append(time[r])
    peaks.append(i+1)
    #we need to add ouput.write at the end as we create a seperate column/text file
    print('Peak',i+1,'has a velocity of',velocities[r],'degrees/s at time',time[r],'ms')
    

    
# fig.show()

#velocities VS time plot
# plt.title('Velocities (degrees/s) VS Time (ms)')
# plt.xlabel('Time (ms)')
# plt.ylabel('Velocities (degrees/s)')
# plt.plot(time,velocities)
# plt.show()


left_most=0
vel=[]

for each in range(len(indices)):
    i=indices[each]
    for v in range(i,left_most,-1):
        if velocities[v]<onset_threshold and velocities[v]-velocities[v-1]<0 and velocities[v]-velocities[v+1]<0:
                onsets_velocities.append(velocities[v])
                onsets_times.append(time[v])
                #when we write in excel or text, we say peak #1 had onset velcoties[j]
                break
    left_most=i

df["OnsetsTimes"] = pd.Series(onsets_times)
df["OnsetsVelocities"] = pd.Series(onsets_velocities)

#######################################################

for each in range(len(indices)):
    i=indices[each]
    if each==len(indices)-1:
        for index in range(len(velocities)):
            if index==len(velocities)-1:
                right_most=index
    else:
        right_most=indices[each+1]
        
    for v in range(i,right_most,1):
        if velocities[v]<offset_threshold and velocities[v]-velocities[v-1]<0 and velocities[v]-velocities[v+1]<0:
            offsets_velocities.append(velocities[v])
            offsets_times.append(time[v])
            #when we write in excel or text, we say peak #1 had offset velcoties[v]
            break

df["OffsetsTimes"] = pd.Series(offsets_times)
df["OffsetsVelocities"] = pd.Series(offsets_velocities)

saccade_duration=[]
#Using len(indices) was causing problems here because it was much larger than the 
#other lists (like onsets times and velocities etc)
for each in range(len(onsets_times)):
    s=offsets_times[each]-onsets_times[each]
    saccade_duration.append(s)

df["SaccadeDurations"] = pd.Series(saccade_duration)


"""
updating the csv with the new information
"""
df.to_csv("output_ED.csv", index=False)