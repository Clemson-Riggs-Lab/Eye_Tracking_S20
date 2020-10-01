# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 16:17:42 2020

@author: Shannon P Devlin
"""
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from tkinter import *
from scipy.signal import savgol_filter
import math
#fake data for testing
# all_indices=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
# onset_indices=[4,10,17]
# offset_indices=[6,12,19]

#file_name = inputET_name.get()
file_name="C:/Users/Shannon P Devlin/Dropbox/Riggs Lab - Shannon D/Summer2020Eyetracking/GitHubOverflow/FOVIO_P2_Sudden_preProcessed.csv"
df = pd.read_csv(file_name)
#NOTE: THIS NEEDS TO BE STORED VALUES PROVIDED BY THE USER. E.g. FOVIO has a sample rate of 16.6667 and Gazepoint has a sample rate of 6.66667 so need the user to either enter this value or add FOVIO and Gazepoint buttons to the GUI like we have for every other script
samp_rate=16.6667
duration_threshold=80
spatial_threshold=100

#Identify key columns
time = df["Time"]
velocities = df["Angular Velocity (in degrees/second)"]
time = list(time) 
velocities = list(velocities)

#NOTE: JUST HARD CODING THE THRESHOLD VALUES FOR TESTING
PT = 408 #int(peak_thresh.get())
onset_threshold = 228 #int(on_thresh.get())
offset_threshold = 254 #int(off_thresh.get()) 

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
saccade_indices = []
onset_indices=[]
offset_indices=[]
# indices = find_peaks(velocities, height = PT)[0]

#smooth the velocities with and SG filter. Used the parameters suggested by Nystrom & Holmqvist
velocities_filt = savgol_filter(velocities, window_length = 3, polyorder = 2) #NOTE: window length is usually based on eye tracker as Nystrom & Holmqvist suggest a filter length of 20 ms so that is a window length = 1 or 2 for FOVIO and window length = 3 or 4 for Gazepoint. However, it says window length can't be even so just making 3 for both 
indices_filt = find_peaks(velocities_filt, height = PT)[0]

"""
 for each in range(len(velocities_filt)):
     if velocities_filt[each]<0:
         velocities_filt.remove(velocities_filt[each])
 """        
print (len(indices_filt),'peaks were detected')
for i in range(len(indices_filt)): 
     r=indices_filt[i]
     peak_times.append(time[r])
     peaks.append(i+1)
     #we need to add ouput.write at the end as we create a seperate column/text file
     # print('Peak',i+1,'has a velocity of',velocities[r],'degrees/s at time',time[r],'ms')
peak_velocities=[]
for each in range(len(indices_filt)):
     i=indices_filt[each]
     peak_velocities.append(velocities_filt[i])
df["Filtered Velocities"] = pd.Series(velocities_filt)

average_peak_velocity=sum(peak_velocities)/len(peak_velocities)
max_peak_velocity=max(peak_velocities)
print (average_peak_velocity,'is the average peak velocity')
print (max_peak_velocity,'is the max peak velocity')
 
left_most=0
vel=[]

for each in range(len(indices_filt)):
     i=indices_filt[each]
     flag=False
     saccade_indices.append(i)
     for v in range(i,left_most,-1):
         saccade_indices.append(v)
         #this flag will tell us if we've found an onset
         if velocities_filt[v]<onset_threshold and velocities_filt[v]-velocities_filt[v-1]<0 and velocities_filt[v]-velocities_filt[v+1]<0:
                 onset_indices.append(v)
                 onsets_velocities.append(velocities_filt[v])
                 onsets_times.append(time[v])
                 #when we write in excel or text, we say peak #1 had onset velcoties[j]
                 #When flag is True, we correctly found onset
                 flag=True
                 break
     if flag==False:
         #999 for both velocities and times?
         onset_indices.append(i-1)
         onsets_times.append(999999)
         onsets_velocities.append(999999)
     left_most=i

df["OnsetsTimes"] = pd.Series(onsets_times)
df["OnsetsVelocities"] = pd.Series(onsets_velocities)

#######################################################
##################################FINDING ALL OFFSET INDICES#################################

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
         saccade_indices.append(v)
         if velocities_filt[v]<offset_threshold:
             offset_indices.append(v)
             offsets_velocities.append(velocities_filt[v])
             offsets_times.append(time[v])
             #when we write in excel or text, we say peak #1 had offset velcoties[v]
             flag=True
             break
     if flag==False:
         offset_indices.append(i+1)
         offsets_times.append(0)
         offsets_velocities.append(0)

df["OffsetsTimes"] = pd.Series(offsets_times)
df["OffsetsVelocities"] = pd.Series(offsets_velocities)


##################################FINDING ALL FIXATIONS INDICES#################################
#initialize list variables
fixation_indices=[]
mini_lst = []

#Need 3 while loops to find all the fixation indices in a file. 
#The first searches for fixation indices before the first onset,
#the second searches for fixation indices between the first saccade's offset to the last saccade's onset, 
#and the third searches for fixation indices after the last saccade's offset

#initialize list variables for searching for fixation indices
fixation_indices=[]
mini_lst = []
j=0
while j < onset_indices[0]:
    mini_lst.append(j)
    j+=1
fixation_indices.append(mini_lst)

for i in range(len(offset_indices)-1):
    j=offset_indices[i] + 1
    mini_lst = []
    while j < onset_indices[i+1]:
        mini_lst.append(j)
        j+=1
    fixation_indices.append(mini_lst)
    
j=(offset_indices[len(offset_indices)-1])+1 #go to the index where the last offset was detected as the starting point to find the last collection of fixation indices
mini_lst = []
while j < len(velocities_filt):#want to search across all velocities past the last saccade's offset so use the filtered velocity list as the structure to base this off of
    mini_lst.append(j)
    j+=1
fixation_indices.append(mini_lst)
   
######################################FIXATION DETECTION CODE######################################### 
    
#distance formula
def calculateDistance(x1,y1,x2,y2):  
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
    return dist  

#initialize list variables for storing fixation indices after the spatial and duration constraitns are applied
fixations_after_constraints = []
center_points = []
for fixation in fixation_indices: #loop thur the list of lists to apply thresholds
    #initialize variables   
    g=""
    fix_lst=[]
    if len(fixation) < 2: #if a given mini fixation list only has two or less points, just skip this list entirely. NOTE: we should probs adjust this value based on eye tracker (i.e. 5 for FOVIO and 12 for Gazepoint) to speed up code
        continue
    else:
        index=1 #initialize the search in this particular mini list (i.e. what is called fixation)
        while index < len(fixation): #using a while loop since sometimes we have to move back a few gazepoints to find a new g and a for loop would not allow us to do that
            if index == 1: #if this is the first time we are searching in this particular mini list (i.e. what is called fixation), then g is simply the first index in the list 
                z=0
                g = fixation[z]
                fix_lst = [g]
                #if distance between index and g > constraint px, break
                #else, add index to fix_lst
                dist = calculateDistance(df.at[g, "BestPogX"], df.at[g, "BestPogY"] ,
                    df.at[index, "BestPogX"], df.at[index, "BestPogY"]) #the euclidean distance calculation as detatiled in the calculateDistance function, units in pixels and does not need to be calculated in visual angle as the threshold is set accounting for visual angle
                if dist <= spatial_threshold: #made up threshold for testing code purposes, but for our work, we do not want to hardcode any values and would want to ask the user for this value in the GUI and store it 
                    fix_lst.append(fixation[index])#add the index to the list that is storing "close" fixation indices
                    index+=1 #increase the counter to search for the next index and test its distance
                    if index >= len(fixation): #This might seem like a random/unnecessary check here but if we increase the counter and then are at the end of this fixation index list, if we immediately go to the while loop this code is all housed in (line 66) we will lose any collection of fixation indices we just previously collected. So we need to proactively check the duration value to see what we have collected thus far is a potential fixation before going to the next mini list (i.e. what is called fixation)
                        if (len(fix_lst)-1) * samp_rate > duration_threshold: #made up threshold for testing code purposes, but for our work, we do not want to hardcode any values and would want to ask the user for this value in the GUI and store it 
                            #store this collection of indices since it meets spatial and duration constriants and store its center point separate so we can pull its x,y coordinates for the output file
                            fixations_after_constraints.append(fix_lst)
                            center_points.append(fix_lst[0])
                            #exit the while to go back to the over arching for loop since we are at the last index of the mini list
                            break
                        else: #if the last points in the list do not meet the duraiton threshold, then go to the next fixation incdice list
                            break       
                else: #if the current index is outside the spatial threshold, check to see if the previous collected indices fits the duration threshold
                    if (len(fix_lst)-1) * samp_rate > duration_threshold:
                        #store the fixation since it meets spatial and duration constriants
                        fixations_after_constraints.append(fix_lst)
                        center_points.append(fix_lst[0])
                        #reset all indices/counters for next loop within the same mini list (i.e. what is called fixation)
                        g=""
                        g=fixation[index]
                        fix_lst=[]
                        fix_lst=[g]
                        z=index
                        index+=1 #the reason we do not need to check if incrementing index by 1 is outside the mini list immeidatley is because the loop will automatcally immediately go back to the while statement (line 66) and it will be checked there and we don't have to worry about losing potential fixaiton data as we just stored the mini ist that fit within the thresholds
                    else:
                        #prep indices/counters to check the next datapoint (but not necessarily the next index) to see if its the 
                        #center of a fixation. However, have it check this with the previously written code 
                        g=""
                        z+=1
                        g=fixation[z] #the new g is determined by z and not index because we had collection of points that were closer togetehr but did not meet the duration threshold so we need to go to the point that is after g, not the next index point as it might be a few point from g
                        fix_lst=[]
                        fix_lst=[g]
                        index=z+1 #need to make index right after g, regardless of where it reached prior
            else: #this section of code is if this is not our first search in the mini list (i.e. what is called fixation), complete the same process with the updated g value                                  
                dist = calculateDistance(df.at[g, "BestPogX"], df.at[g, "BestPogY"] ,
                    df.at[index, "BestPogX"], df.at[index, "BestPogY"]) #the euclidean distance calculation as detatiled in the calculateDistance function, units in pixels and does not need to be calculated in visual angle as the threshold is set accounting for visual angle
                if dist <= spatial_threshold:
                    fix_lst.append(fixation[index])
                    index+=1
                    if index >= len(fixation):
                        if (len(fix_lst)-1) * samp_rate > duration_threshold:
                            fixations_after_constraints.append(fix_lst)
                            center_points.append(fix_lst[0])
                            break
                        else: 
                            break                           
                else:                                   
                    if (len(fix_lst)-1) * samp_rate > duration_threshold:
                        fixations_after_constraints.append(fix_lst)
                        center_points.append(fix_lst[0])
                        #reset all indice/counters for next loop with a new g
                        g=""
                        g=fixation[index]
                        fix_lst=[]
                        fix_lst=[g]
                        z=index
                        index+=1
                    else:
                        #prep indices/counters to check the next indices to see if its the 
                        #center of a fixation. However, have it make the dist and dur thresholds
                        #with previous code 
                        g=""
                        z+=1
                        g=fixation[z]
                        fix_lst=[]
                        fix_lst=[g]
                        index=z+1


###############################SACCADE
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
    time_diff = (offsets_times[i] - onsets_times[i])/1000
    sac_amp = avg * time_diff
    sac_amps.append(sac_amp)

df["SaccadeAmplitudes"] = pd.Series(sac_amps)
    

"""
updating the csv with the new information
"""
out_file = output_name.get()
# out_file = "output_ED.csv"
df.to_csv(out_file, index=False)
text6.configure(text='Status: Success! Fixations and Saccades have been detected successfully')

#For testing 
"""
This nested for loop checks if there is overlap between saccade indices
and fixation indices. There was no overlap on my end which is a good sign. 
Also BEWARE, this testing loop requires a lot of computing power so make sure
you don't have a lot of other things open when running it!
"""
for i in fixations_after_constraints:
    for j in i:
        for s in saccade_indices:
            if s == j:
                print("Overlap")
          

#This is our total number of fixations
print (len(fixations_after_constraints),'fixations were detected')
  
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

text5 = Label(frame5, text='Enter Fixation Radius (px): ')
text5.pack(side=LEFT)
fix_radius = Entry(frame5)
fix_radius.pack(side=LEFT)

one = Button(window, text="Gazepoint", width="10", height="3",command=lambda : event_detection(1))
one.pack(side="top")

two = Button(window, text="FOVIO", width="10", height="3", command=lambda : event_detection(2))
two.pack(side="top")

text6 = Label(frame7, text='Status: N/A')
text6.pack()

window.mainloop()
