"""
Created on Wed Aug 26 11:24:49 2020

@author: Jad Atweh
"""
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from tkinter import *
from scipy.signal import savgol_filter, savgol_coeffs, convolve
from scipy.ndimage import convolve1d
import math
import numpy as np
import scipy.signal as signal
import random


# Delta = [] #in pixels
# Angular_Velocity = []
# Delta_mm = []
# Delta_rad = [] 
# inch_to_mm=25.4
# rad_to_degrees = 57.29577951
# distance_from_screen = 29.5
# pixel_to_mm=0.269279688

# Delta.append(math.sqrt(pow(x1,2)+pow(y1,2)))
# Delta_mm.append(Delta[i]*pixel_to_mm)
# Delta_rad.append(math.atan(Delta_mm[i]/(distance_from_screen*inch_to_mm)))
# velocity = Delta_rad[i]*rad_to_degrees*1000/time_diff #convert to degrees and divide by time difference
# Angular_Velocity.append(velocity)



file_name="C:/Users/Shannon P Devlin/Documents/GitHub/Eye_Tracking_S20/FOVIO_P10_Sudden.csv"
df = pd.read_csv(file_name)
#tracker_type=2
samp_rate=16.6667
w=2560 #width of screen in pixels
h=1600 #height of screen in pixels
screen=32 #diagonal of screen in inches
D = 29.5 #participants distance from screen in inches
herz=60 #refresh rate of eye tracker
period = float(1.0/float(herz)) #period of the eye tracker (i.e. time between samples)
dfwidth=5 #window length for SG filter
dfdegree=2 #order of the polynomial for SG filter
dfo=1 #level of derivative for SG filter


XCoord=df["BestPogX"]
YCoord=df["BestPogY"]
FiltXCoord=savgol_filter(XCoord, window_length = dfwidth, polyorder = dfdegree, deriv = dfo)
FiltYCoord=savgol_filter(YCoord, window_length = dfwidth, polyorder = dfdegree, deriv = dfo)

dt = period * float(dfwidth) #change of time between filtered samples
r = math.sqrt(float(w)*float(w) + float(h)*float(h)) #pythagorean theorem to get hypotenuse in units of pixels
ppi = r/float(screen) #pixels per inch

degx=[0]*len(FiltXCoord)
degy=[0]*len(FiltYCoord)
for point in range(len(FiltXCoord)):
    degx[point]=math.degrees(math.atan2((FiltXCoord[point]/ppi),(2*D)))
    degy[point]=math.degrees(math.atan2((FiltYCoord[point]/ppi),(2*D)))

# def vel_f(a,b)
#     return a/b
degx=np.array(degx)
degy=np.array(degy)

velx= degx/dt 
vely= degy/dt

vel=[0]*len(velx)
for a in range(len(velx)):
    vel[a] = math.sqrt(velx[a]*velx[a] + vely[a]*vely[a])

df["Velocity (degrees of visual angle/second)"]=vel

#sanity check of savgol_function...only works with convolve1d and not convolve as we need the len of the output to = len of input
Coeffs=savgol_coeffs(window_length=dfwidth, polyorder=dfdegree, deriv=dfo, use="conv")
res = convolve1d(np.array(XCoord[0:10]), Coeffs) 








def event_detection(tracker_type):
    #file_name = inputET_name.get()
    file_name="C:/Users/Shannon P Devlin/Documents/GitHub/Eye_Tracking_S20/FOVIO_P10_Sudden.csv"
    df = pd.read_csv(file_name)
    tracker_type=2
    #The sampling rate of each eye tracker is known so no need to be a user input
    if tracker_type == 1:
        samp_rate=6.66667
    else:
        samp_rate=16.6667
        

    time = df["Time"]
    velocities = df["Angular Velocity (in degrees/second)"]
    time = list(time) 
    velocities = list(velocities)
  
    
    duration_threshold=int(dur_thresh.get())
    spatial_threshold=int(fix_radius.get())
    
    #Identify key columns
    PT = int(peak_thresh.get())
    onset_threshold = int(on_thresh.get())
    offset_threshold = int(off_thresh.get())

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

    #smooth the velocities with and SG filter. Used the parameters suggested by Nystrom & Holmqvist
    velocities_filt = savgol_filter(velocities, window_length = 3, polyorder = 2)
    indices_filt = find_peaks(velocities_filt, height = PT)[0]
        
    print (len(indices_filt),'peaks were detected')
    """
    for i in range(len(indices_filt)): 
        r=indices_filt[i]
        peak_times.append(time[r])
        peaks.append(i+1)
        #we need to add ouput.write at the end as we create a seperate column/text file
        # print('Peak',i+1,'has a velocity of',velocities[r],'degrees/s at time',time[r],'ms')
    """
    peak_velocities=[]
    for each in range(len(indices_filt)):
        i=indices_filt[each]
        peak_velocities.append(velocities_filt[i])
    
    #All filtered velocities are reported in a seperate column in output file 1
    df["Filtered Velocities"] = pd.Series(velocities_filt)
    
    average_peak_velocity=sum(peak_velocities)/len(peak_velocities)
    max_peak_velocity=max(peak_velocities)
    print (average_peak_velocity,'is the average peak velocity')
    print (max_peak_velocity,'is the max peak velocity')
    
        
    #following the adaptive algorithm to detect onsets
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
            onset_indices.append(i-1)
            onsets_times.append(999999)
            onsets_velocities.append(999999)
        left_most=i

    df["OnsetsTimes"] = pd.Series(onsets_times)
    df["OnsetsVelocities"] = pd.Series(onsets_velocities)

    #######################################################

    #Following the adaptive algorithm to detect an offset
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
                flag=True
                break
        if flag==False:
            offset_indices.append(i+1)
            offsets_times.append(0)
            offsets_velocities.append(0)

    df["OffsetsTimes"] = pd.Series(offsets_times)
    df["OffsetsVelocities"] = pd.Series(offsets_velocities)
##################################FINDING ALL FIXATIONS INDICES#################################
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
                        df.at[fixation[index], "BestPogX"], df.at[fixation[index], "BestPogY"]) #the euclidean distance calculation as detatiled in the calculateDistance function, units in pixels and does not need to be calculated in visual angle as the threshold is set accounting for visual angle
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
                            g=fixation[z]
                            fix_lst=[]
                            fix_lst=[g]
                            index=z+1
                else: #this section of code is if this is not our first search in the mini list (i.e. what is called fixation), complete the same process with the updated g value                                  
                    dist = calculateDistance(df.at[g, "BestPogX"], df.at[g, "BestPogY"] ,
                        df.at[fixation[index], "BestPogX"], df.at[fixation[index], "BestPogY"]) #the euclidean distance calculation as detatiled in the calculateDistance function, units in pixels and does not need to be calculated in visual angle as the threshold is set accounting for visual angle
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
        
    for each in range(len(onsets_times)):
        s=offsets_times[each]-onsets_times[each]
        saccade_duration.append(s)
    
    
               
    # Saccade amplitude calculation
    for i in range(len(onsets_times)):
        df1=df[(df.Time>=onsets_times[i])&(df.Time<=offsets_times[i])] #create a mini dataframe consisting of the data of 1 saccade
        vel = df1['Angular Velocity (in degrees/second)'].sum() #sum the velocity values
        count=df1.Time.count() #get number of elements to use in average calculation
        if (float(count!=0)):
            avg= float(vel)/float(count)
            time_diff = (offsets_times[i] - onsets_times[i])/1000
            sac_amp = avg * time_diff
            sac_amps.append(sac_amp)
        else:
             sac_amps.append(0) #This value will be discarded, it is only to keep the list value in check with all other lists to prevent out of range errors


              
    
    AOI=[]
    for each in range(len(center_points)):
        if 0<=df.at[center_points[each], "BestPogX"]<=1010 and 0<=df.at[center_points[each], "BestPogY"]<=927:
            AOI.append('AOI 1: Reroute Map')
        elif 0<=df.at[center_points[each], "BestPogX"]<=1010 and 951<=df.at[center_points[each], "BestPogY"]<=1600:
            AOI.append('AOI 2: Reroute Menu')
        elif 1036<=df.at[center_points[each], "BestPogX"]<=2560 and 0<=df.at[center_points[each], "BestPogY"]<811:
            AOI.append('AOI 3: Video Feeds')
        elif 1036<=df.at[center_points[each], "BestPogX"]<=2560 and 811<=df.at[center_points[each], "BestPogY"]<=1157:
            AOI.append('AOI 4: Fuel Leak Bars')
        elif 1036<=df.at[center_points[each], "BestPogX"]<=2560 and 1179<=df.at[center_points[each], "BestPogY"]<=1600:
            AOI.append('AOI 5: Chat Message Panel')
        else:
            #a special case if the centroid landed on any of the grey or black distances seperating each AOI
            AOI.append('Fixation is not in any of the designated AOIs')
        
    
    
    ########################################## CREATING OUTPUT FILE 2 ###########################################

    # output file 1 is simply the input of this code added to it: Filtered velocities, onset times and velocities, and offset times and velocities
    out_file1 = output1_name.get()
    # output file 2 reports all events detected
    out_file2 = output2_name.get()
    
    out_data = []
    out_event=[]
    out_start_time = []
    out_amp =[]
    out_X=[]
    out_Y=[]
    out_duration = []
    out_AOI = []
    fix_start_time = []
    for i in range(len(center_points)):
       fix_start_time.append(df.at[center_points[i],"Time"]) #Find start times of fixation from time of center point

    out =pd.DataFrame(out_data,columns=['Participant Number','Workload','Eyetracker','Event Type','Start time(ms)','Duration','Amplitude (degrees)','X','Y','AOI'])
    i=0 #counter for saccades
    j=0 #counter for fixations
    while (i != len(onsets_times)-1 and j != len(fix_start_time)-1): 
        
        if (onsets_times[i]<fix_start_time[j]): #if saccade comes before fixation
            if(offsets_times[i] == 0):
                print('Invalid saccade detected (missed offset) and its onset time is '+str(onsets_times[i])+' ms')
                i=i+1
            else:
                out_event.append("Saccade")
                out_amp.append(sac_amps[i]) 
                out_start_time.append(onsets_times[i])
                out_duration.append(saccade_duration[i])
                out_X.append("N/A")
                out_Y.append("N/A")
                out_AOI.append("N/A")
                i=i+1

        else: #Fixation comes before saccade
            if (onsets_times[i]==999999):
                print('Invalid saccade detected (missed onset) and its offset is '+str(offsets_times[i])+' ms')
                i=i+1
            else:
                out_event.append("Fixation")
                out_amp.append("N/A")
                out_start_time.append(fix_start_time[j]) #Find time of the center of the fixation
                out_duration.append((len(fixations_after_constraints[j])-1)*samp_rate) 
                out_X.append(df.at[center_points[j],"BestPogX"]) #Find X of the center of the fixation
                out_Y.append(df.at[center_points[j],"BestPogY"]) #Find Y of the center of the fixation
                out_AOI.append(AOI[j])
                j=j+1

    out["Event Type"] = out_event
    out["Start time(ms)"] = out_start_time
    out["Duration"] = out_duration
    out["Amplitude (degrees)"] = out_amp
    out["X"] = out_X
    out["Y"] = out_Y
    out["AOI"] = out_AOI
    if tracker_type ==1:
        out['Eyetracker']='Gazepoint'
    else:
        out['Eyetracker']='FOVIO'
    p = participant.get()
    w = workload.get()
    out["Workload"] = w
    out["Participant Number"] = p
    df.to_csv(out_file1, index=False)
    out.to_csv(out_file2,index=False)
    text11.configure(text='Status: Success! Fixations and Saccades have been detected successfully')
    print (len(fixations_after_constraints),'fixations were detected')
  
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
frame8 = Frame(window)
frame9 = Frame(window)
frame10 = Frame(window)
frame11 = Frame(window)

frame0.pack()
frame1.pack()
frame2.pack()
frame3.pack()
frame4.pack()
frame5.pack()
frame6.pack()
frame7.pack()
frame8.pack()
frame9.pack()
frame10.pack()
frame11.pack()

window.title("Event Detection GUI")


text0 = Label(frame0, text='This code outputs two seperate files: Output file 1 and Output file 2                            ')
text0.pack(side=LEFT)

text1 = Label(frame1, text='Enter Eyetracking file name:                          ')
text1.pack(side=LEFT)
inputET_name = Entry(frame1)
inputET_name.pack(side=LEFT)


text2 = Label(frame2, text='Enter Output 1 file name:                               ')
text2.pack(side=LEFT)
output1_name = Entry(frame2)
output1_name.pack(side=LEFT)

text3 = Label(frame3, text='Enter Output 2 file name:                               ')
text3.pack(side=LEFT)
output2_name = Entry(frame3)
output2_name.pack(side=LEFT)

text4 = Label(frame4, text='Enter Peak Threshold:                                     ')
text4.pack(side=LEFT)
peak_thresh = (Entry(frame4))
peak_thresh.pack(side=LEFT)

text5 = Label(frame5, text='Enter Onset Threshold:                                   ')
text5.pack(side=LEFT)
on_thresh = Entry(frame5)
on_thresh.pack(side=LEFT)

text6 = Label(frame6, text='Enter Offset Threshold:                                   ')
text6.pack(side=LEFT)
off_thresh = Entry(frame6)
off_thresh.pack(side=LEFT)
 
text7 = Label(frame7, text='Enter Fixation Radius (px):                             ')
text7.pack(side=LEFT)
fix_radius = Entry(frame7)
fix_radius.pack(side=LEFT)

text8 = Label(frame8, text='Enter Fixation Duration Threshold (ms):      ')
text8.pack(side=LEFT)
dur_thresh = Entry(frame8)
dur_thresh.pack(side=LEFT)

text9 = Label(frame9, text='Enter Participant Number:                             ')
text9.pack(side=LEFT)
participant = Entry(frame9)
participant.pack(side=LEFT)

text10 = Label(frame10, text='Enter Workload type:                                      ')
text10.pack(side=LEFT)
workload = Entry(frame10)
workload.pack(side=LEFT)
one = Button(window, text="Gazepoint", width="10", height="3",command=lambda : event_detection(1))
one.pack(side="top")

two = Button(window, text="FOVIO", width="10", height="3", command=lambda : event_detection(2))
two.pack(side="top")

text11 = Label(frame11, text='Status: N/A')
text11.pack()

window.mainloop()