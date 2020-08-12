# import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from tkinter import *
from scipy.signal import savgol_filter


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

def event_detection(tracker_type):
    file_name = inputET_name.get()
    df = pd.read_csv(file_name)
    if tracker_type == 1:
        # counter=0
        # for i in df["MissionTime"]:
        #     if i > 0.0:
        #         break
        #     counter +=1
        # time = df["MissionTime"][counter-1:len(df["MissionTime"])]
        # velocities = df["Angular Velocity (in degrees/second)"][counter-1:len(df["Angular Velocity (in degrees/second)"])]
        # #Pandas series are not sliceable
        # time = list(time)
        # velocities = list(velocities)
        time = df["Time"]
        velocities = df["Angular Velocity (in degrees/second)"]
        time = list(time)
        velocities = list(velocities)

    else:
        time = df["Time"]
        velocities = df["Angular Velocity (in degrees/second)"]
        time = list(time)
        velocities = list(velocities)

    PT = int(peak_thresh.get())
    onset_threshold = int(on_thresh.get())
    offset_threshold = int(off_thresh.get())
    #I chose any numbers until we determine the velocity threshold, onset and offset thresholds
    #arbitrary values, PT will be determined before (each participant has a different PT for a different load)

    #those will be changed at the end to add in the excel file or in a text file
    onsets_times = []
    onsets_velocities = []
    offsets_times = []
    offsets_velocities = [] 
    offsets=[]
    peak_times = []
    peaks = [] 
    sac_amps= []
    # indices = find_peaks(velocities, height = PT)[0]

      #smooth the velocities with and SG filter. Used the parameters suggested by Nystrom & Holmqvist
    velocities_filt = savgol_filter(velocities, window_length = 5, polyorder = 3) #NOTE: window length will depend on eye tracker as Nystrom & Holmqvist suggest a filter length of 20 ms so that is a window length = 2 for FOVIO and window length = 3 or 4 for Gazepoint
    indices_filt = find_peaks(velocities_filt, height = PT)[0]


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

    print (len(indices_filt),'peaks were detected')
    for i in range(len(indices_filt)): 
        r=indices_filt[i]
        peak_times.append(time[r])
        peaks.append(i+1)
        #we need to add ouput.write at the end as we create a seperate column/text file
        # print('Peak',i+1,'has a velocity of',velocities[r],'degrees/s at time',time[r],'ms')
        

        
    # fig.show()

    #velocities VS time plot
    # plt.title('Velocities (degrees/s) VS Time (ms)')
    # plt.xlabel('Time (ms)')
    # plt.ylabel('Velocities (degrees/s)')
    # plt.plot(time,velocities)
    # plt.show()


    left_most=0
    vel=[]

    for each in range(len(indices_filt)):
        i=indices_filt[each]
        flag=False
        for v in range(i,left_most,-1):
            #this flag will tell us if we've found an onset
            if velocities_filt[v]<onset_threshold and velocities_filt[v]-velocities_filt[v-1]<0 and velocities_filt[v]-velocities_filt[v+1]<0:
                    onsets_velocities.append(velocities_filt[v])
                    onsets_times.append(time[v])
                    #when we write in excel or text, we say peak #1 had onset velcoties[j]
                    #When flag is True, we correctly found onset
                    flag=True
                    break
        if flag==False:
            #999 for both velocities and times?
            onsets_times.append(999)
            onsets_velocities.append(999)
        left_most=i

    df["OnsetsTimes"] = pd.Series(onsets_times)
    df["OnsetsVelocities"] = pd.Series(onsets_velocities)

    #######################################################

    for each in range(len(indices_filt)):
        i=indices_filt[each]
        if each==len(indices_filt)-1:
            for index in range(len(velocities_filt)):
                if index==len(velocities_filt)-1:
                    right_most=index
        else:
            right_most=indices_filt[each+1]
        flag=False   
        for v in range(i,right_most,1):
           
            if velocities_filt[v]<offset_threshold and velocities_filt[v]-velocities_filt[v-1]<0 and velocities_filt[v]-velocities_filt[v+1]<0:
                offsets_velocities.append(velocities_filt[v])
                offsets_times.append(time[v])
                #when we write in excel or text, we say peak #1 had offset velcoties[v]
                flag=True
                break
        if flag==False:
            offsets_times.append(0)
            offsets_velocities.append(0)

    df["OffsetsTimes"] = pd.Series(offsets_times)
    df["OffsetsVelocities"] = pd.Series(offsets_velocities)

    print(len(onsets_times))
    print(len(offsets_times))
    saccade_duration=[]
    #Using len(indices) was causing problems here because it was much larger than the 
    #other lists (like onsets times and velocities etc)
    for each in range(len(onsets_times)):
        s=offsets_times[each]-onsets_times[each]
        saccade_duration.append(s)

    df["SaccadeDurations"] = pd.Series(saccade_duration)

    for i in range(len(indices_filt)):
        peak_v = df.at[indices_filt[i], "Angular Velocity (in degrees/second)"]
        onset_v = onsets_velocities[i]
        offset_v = offsets_velocities[i]
        avg = (peak_v + onset_v + offset_v)/3
        time_diff = offsets_times[i] - onsets_times[i]
        sac_amp = avg * time_diff
        sac_amps.append(sac_amp)
    
    df["SaccadeAmplitudes"] = pd.Series(sac_amps)

    """
    updating the csv with the new information
    """
    out_file = output_name.get()
    df.to_csv(out_file, index=False)


# UI things. This is very similar to preprocessing UI 
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

window.title("Event Detection GUI")

text0 = Label(frame0, text='Enter Eyetracking file name: ')
text0.pack(side=LEFT)
inputET_name = Entry(frame0)
inputET_name.pack(side=LEFT)

text1 = Label(frame1, text='Enter Output file name: ')
text1.pack(side=LEFT)
output_name = Entry(frame1)
output_name.pack(side=LEFT)

text2 = Label(frame2, text='Enter Peak Threshold: ')
text2.pack(side=LEFT)
peak_thresh = (Entry(frame2))
peak_thresh.pack(side=LEFT)

text3 = Label(frame3, text='Enter Onset Threshold: ')
text3.pack(side=LEFT)
on_thresh = Entry(frame3)
on_thresh.pack(side=LEFT)

text4 = Label(frame4, text='Enter Offset Threshold: ')
text4.pack(side=LEFT)
off_thresh = Entry(frame4)
off_thresh.pack(side=LEFT)

one = Button(window, text="Gazepoint", width="10", height="3",command=lambda : event_detection(1))
one.pack(side="top")

two = Button(window, text="FOVIO", width="10", height="3", command=lambda : event_detection(2))
two.pack(side="top")

text6 = Label(frame7, text='Status: N/A')
text6.pack()

window.mainloop()

