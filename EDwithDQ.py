
"""
Created on Wed Aug 26 11:24:49 2020

@author: Jad Atweh
"""
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from tkinter import *
from scipy.signal import savgol_filter
import math
import numpy as np


"""
These coordinates are based on the layout of the screen that the participants 
are looking at during the test. 
"""
"""
These coordinates are based on the layout of the screen that the participants 
are looking at during the test. 
"""
#Coordinate fields for each UAV in the 2560 x 1440 resolution. @Sam these were updated based on my most recent readings
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

def which_uav(x, y):
    counter=0
    for uav in UAVs:
        xacc= (x >= uav[0] and x <= uav[1])
        yacc = (y >= uav[2] and y <= uav[3])
        if xacc and yacc:
            return counter+1
        counter+=1
    return "Inconclusive"

def event_detection(tracker_type):
    file_name = inputET_name.get()
    df = pd.read_csv(file_name)
    #The sampling rate of each eye tracker is known so no need to be a user input
    if tracker_type == 1:
        samp_rate=6.66667
    else:
        samp_rate=16.6667
    time = df["MissionTime"]
    velocities = df["Velocity (degrees of visual angle/second)"]
    time = list(time) 
    velocities = list(velocities)
  
    
    duration_threshold=int(dur_thresh.get())
    spatial_threshold=int(fix_radius.get())
    
    #Extract thresholds from files
    PT = df["Peak Threshold"][1] #int(peak_thresh.get())
    onset_threshold = df["Onset Threshold"][1]    #int(on_thresh.get())
    offset_threshold = df["Offset Threshold"][1]  #int(off_thresh.get())

    onsets_times = []
    onsets_velocities = []
    offsets_times = []
    offsets_velocities = [] 
    offsets=[]
    peak_times = []
    peaks = [] 
    sac_amps= []
    max_amps=[] #@Sam: added max saccade amplitdue as a measure we might explore
    saccade_indices = []
    onset_indices=[]
    offset_indices=[]

    #Find peaks in velocity as defined by the adaptive algorithm
    indices = find_peaks(velocities, height = PT)[0]
        
    print (len(indices),'saccade peaks were detected')
    """
    for i in range(len(indices)): 
        r=indices[i]
        peak_times.append(time[r])
        peaks.append(i+1)
        #we need to add ouput.write at the end as we create a seperate column/text file
        # print('Peak',i+1,'has a velocity of',velocities[r],'degrees/s at time',time[r],'ms')
    """
    peak_velocities=[]
    for each in range(len(indices)):
        i=indices[each]
        peak_velocities.append(velocities[i])

    
    average_peak_velocity=sum(peak_velocities)/len(peak_velocities)
    max_peak_velocity=max(peak_velocities)
    print (average_peak_velocity,'is the average peak velocity')
    print (max_peak_velocity,'is the max peak velocity')
    
        
    #following the adaptive algorithm to detect onsets
    left_most=0
    vel=[]

    for each in range(len(indices)):
        i=indices[each]
        flag=False
        saccade_indices.append(i)
        for v in range(i,left_most,-1):
            saccade_indices.append(v)
            #this flag will tell us if we've found an onset
            if velocities[v]<onset_threshold and velocities[v]-velocities[v-1]<0 and velocities[v]-velocities[v+1]<0:
                    onset_indices.append(v)
                    onsets_velocities.append(velocities[v])
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
    for each in range(len(indices)):
        i=indices[each]
        if each==len(indices)-1:
            for index in range(len(velocities)):
                if index==len(velocities)-1:
                    right_most=index
        else:
            right_most=indices[each+1]
        flag=False   
        for v in range(i,right_most,1):
            saccade_indices.append(v)
            if velocities[v]<offset_threshold:
                offset_indices.append(v)
                offsets_velocities.append(velocities[v])
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
    while j < len(velocities):#want to search across all velocities past the last saccade's offset so use the filtered velocity list as the structure to base this off of
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
    ###############################################################SACCADE##############################################################
    saccade_duration=[]
        
    for each in range(len(onsets_times)):
        s=offsets_times[each]-onsets_times[each]
        saccade_duration.append(s)
    
    
               
    # Saccade amplitude calculation
    for i in range(len(onsets_times)):
        df1=df[(df.MissionTime>=onsets_times[i])&(df.MissionTime<=offsets_times[i])] #create a mini dataframe consisting of the data of 1 saccade
        maxAmp=df1['Velocity (degrees of visual angle/second)'].max()#find the peak velocity for this saccade
        max_amps.append(maxAmp) 
        vel = df1['Velocity (degrees of visual angle/second)'].sum() #sum the velocity values
        count=df1.MissionTime.count() #get number of elements to use in average calculation
        if (float(count!=0)):
            avg= float(vel)/float(count)
            time_diff = (offsets_times[i] - onsets_times[i])
            sac_amp = avg * time_diff
            sac_amps.append(sac_amp)           
        else:
             sac_amps.append(0) #This value will be discarded, it is only to keep the list value in check with all other lists to prevent out of range errors
             max_amps.append(0) #This value will be discarded, it is only to keep the list value in check with all other lists to prevent out of range errors


              
    
    AOI=[]
    curr_uav = []
    for each in range(len(center_points)):
        if 0<=df.at[center_points[each], "BestPogX"]<=910 and 0<=df.at[center_points[each], "BestPogY"]<=905:
            AOI.append('AOI 3: Map')
            curr_uav.append("NA")
        elif 0<=df.at[center_points[each], "BestPogX"]<=910 and 930<=df.at[center_points[each], "BestPogY"]<=1440:
            AOI.append('AOI 2: Reroute Menu')
            curr_uav.append("NA")
        elif 930<=df.at[center_points[each], "BestPogX"]<=2560 and 0<=df.at[center_points[each], "BestPogY"]<813:
            AOI.append('AOI 1: Video Feeds')
            x = df.at[center_points[each], "BestPogX"]
            y = df.at[center_points[each], "BestPogY"]
            curr_uav.append(which_uav(x, y))
        elif 930<=df.at[center_points[each], "BestPogX"]<=2560 and 835<=df.at[center_points[each], "BestPogY"]<=1158:
            AOI.append('AOI 4: General Health panel')
            curr_uav.append("NA")
        elif 930<=df.at[center_points[each], "BestPogX"]<=2560 and 1180<=df.at[center_points[each], "BestPogY"]<=1440:
            AOI.append('AOI 5: Chat Message Panel')
            curr_uav.append("NA")
        else:
            #a special case if the centroid landed on any of the grey or black distances seperating each AOI
            AOI.append('Fixation is not in any of the designated AOIs')
            curr_uav.append("NA")

    
    
    ########################################## CREATING OUTPUT FILE 2 ###########################################

    # output file 1 is simply the input of this code added to it: Filtered velocities, onset times and velocities, and offset times and velocities
    out_file1 = output1_name.get()
    # output file 2 reports all events detected
    out_file2 = output2_name.get()
    
    out_data = []
    out_event=[]
    out_start_time = []
    out_end_time = []
    out_amp =[]
    out_mamp=[]
    out_X=[]
    out_Y=[]
    out_duration = []
    out_AOI = []
    out_currUAV = []
    fix_start_time = []
    for i in range(len(center_points)):
       fix_start_time.append(df.at[center_points[i],"MissionTime"]) #Find start times of fixation from time of center point

    out=pd.DataFrame(out_data,columns=['Participant Number','Workload','Eyetracker','Event Type','Start time (s)','Duration (ms)', 'Amplitude (degrees)','X','Y','AOI', 'Video Feed']) #'End time (s)',
    i=0 #counter for saccades
    j=0 #counter for fixations
    while (i != len(onsets_times) and j != len(fix_start_time)): 
        
        if (onsets_times[i]<fix_start_time[j]): #if saccade comes before fixation
            if(offsets_times[i] == 0):
                print('Invalid saccade detected (missed offset) and its onset time is '+str(onsets_times[i])+' s')
                i=i+1
            else:
                out_event.append("Saccade")
                out_amp.append(sac_amps[i]) 
                out_mamp.append(max_amps[i])
                out_start_time.append(onsets_times[i])
                out_duration.append(saccade_duration[i])
                out_X.append("N/A")
                out_Y.append("N/A")
                out_AOI.append("N/A")
                out_currUAV.append("N/A")
                i=i+1

        else: #Fixation comes before saccade
            if (onsets_times[i]==999999):
                print('Invalid saccade detected (missed onset) and its offset is '+str(offsets_times[i])+' s')
                i=i+1
            else:
                out_event.append("Fixation")
                out_amp.append("N/A")
                out_mamp.append("N/A")
                out_start_time.append(fix_start_time[j]) #Find time of the center of the fixation
                out_duration.append((len(fixations_after_constraints[j])-1)*samp_rate) 
                out_X.append(df.at[center_points[j],"BestPogX"]) #Find X of the center of the fixation
                out_Y.append(df.at[center_points[j],"BestPogY"]) #Find Y of the center of the fixation
                out_AOI.append(AOI[j])
                out_currUAV.append(curr_uav[j])            
                j=j+1
  
                
    if (i < len(onsets_times)):
        while (i < len(onsets_times)):
            if(offsets_times[i] == 0):
                print('Invalid saccade detected (missed offset) and its onset time is '+str(onsets_times[i])+' s')
                i=i+1
            elif (onsets_times[i]==999999):
                print('Invalid saccade detected (missed onset) and its offset is '+str(offsets_times[i])+' s')
                i=i+1
            else:
                out_event.append("Saccade")
                out_amp.append([i]) 
                out_mamp.append(max_amps[i])
                out_start_time.append(onsets_times[i])
                out_duration.append(saccade_duration[i])
                out_X.append("N/A")
                out_Y.append("N/A")
                out_AOI.append("N/A")
                out_currUAV.append("N/A")
                i=i+1                        
    elif (j < len(fix_start_time)):
        while (j < len(fix_start_time)):            
            out_event.append("Fixation")
            out_amp.append("N/A")
            out_mamp.append("N/A")
            out_start_time.append(fix_start_time[j]) #Find time of the center of the fixation
            out_duration.append((len(fixations_after_constraints[j])-1)*samp_rate) 
            out_X.append(df.at[center_points[j],"BestPogX"]) #Find X of the center of the fixation
            out_Y.append(df.at[center_points[j],"BestPogY"]) #Find Y of the center of the fixation
            out_AOI.append(AOI[j])
            out_currUAV.append(curr_uav[j])
            j=j+1
            
        
    out["Event Type"] = out_event
    out["Start time (s)"] = out_start_time
    out["Duration (ms)"] = out_duration
   # out['End time (s)'] = out_start_time + (out_duration/1000)
    out["Amplitude (degrees)"] = out_amp
    out["Peak Velocity (degrees/second)"] = out_mamp
    out["X"] = out_X
    out["Y"] = out_Y
    out["AOI"] = out_AOI
    out["Video Feed"] = out_currUAV
    if tracker_type ==1:
        out['Eyetracker']='Gazepoint'
    else:
        out['Eyetracker']='FOVIO'
    p = df["ParticipantNumber"][1] #participant.get()
    w = df["Workload"][1] #workload.get()
    out["Workload"] = w
    out["Participant Number"] = p
    df.to_csv(out_file1, index=False)
    out.to_csv(out_file2,index=False)
    text12.configure(text='Status: Success! Fixations and Saccades have been detected successfully')
    print (len(fixations_after_constraints),'fixations were detected')
    print ("Sanity check that all valid saccades outputted to Output file 2 (should equal # of saccade peaks):", i)
    print ("Sanity check that all valid fixations outputted to Output file 2 (should equal # of fixations detected):",j)
    #Run DQ 
    df = pd.read_csv(out_file2)
    #@Sam: this block of code creates the data frame to pass through the DQ part of the code that was adapted for ED. It is coded so that it works with the users same inputs they made in the GUI
    df.rename(columns = {'Event Type':'Event_Type', 'Start time (s)':'MissionTime', 'X':'BestPogX', 'Y':'BestPogY'}, inplace = True) 
    df = df[df.Event_Type != "Saccade"]
    df.reset_index(drop=True, inplace=True)
    inpPerf_name = inputPerf_name.get()
    performance = pd.read_csv(inpPerf_name)
    xErr = int(xError.get())
    yErr = int(yError.get())
    dq(df, performance, xErr, yErr, out_file2)
    
         
"""
Given x and y coordinates, this function determines which UAV the corrdinates would
fall into. Future edit may be to combine this function with the secondary task function. 
"""
       
# def which_uav(x, y):
#     counter=0
#     for uav in UAVs:
#         xacc= (x >= uav[0] and x <= uav[1])
#         yacc = (y >= uav[2] and y <= uav[3])
#         if xacc and yacc:
#             return counter+1
#         counter+=1
#     return "Inconclusive"

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

def dq(df, performance, xError, yError,out_file2):

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
    #read in performance file
        
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
                if -.1 <= (mt - clickTime) <= .1:
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
                    if -.1 < mt -  clickTime < .1:
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
    # for each in performance["TDTargetPresent"]:
    #     if each == 1.0:
    #         sanityCheck[each,"RowNum"] = performance[each].index
    #         clickTime = performance.iloc[count, 27]
    """
    Here, we repeat the logic used for target detection but in the context of 
    the secondary tasks. 
    """
    RRPanel = [0, 910, 0, 1440] #including map panel because participants could have been looking at map and using peripheral vision to check alternate routes
    FLPanel = [930, 2560, 833, 1158]
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
                        continue
                    # if (performance.at[perf_counter,"MessageAnswerAccuracy"] != 1):
                    #     perf_counter+=1
                    #     #print(each)
                    #     continue
                    
                    
                raw_counter=0
                for mt in df["MissionTime"]:
                    if (-.5 <= mt - each <= .5):#only checking eye tracking data 0.5 seconds before and after click time of target task
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
   #Sam: These three lines name the ED with DQ output a different file name you don't have to explicitly define each time and so you have both versions (ED with and without DQ)
    out_file2 = out_file2[:-4]        
    out_file3 = [out_file2,'_DQ','.csv']
    out_file3 =''.join(out_file3)
    
    df.to_csv(out_file3, index=False)
  
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
frame12 = Frame(window)

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
frame12.pack()

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

# text4 = Label(frame4, text='Enter Peak Threshold:                                     ')
# text4.pack(side=LEFT)
# peak_thresh = (Entry(frame4))
# peak_thresh.pack(side=LEFT)

# text5 = Label(frame5, text='Enter Onset Threshold:                                   ')
# text5.pack(side=LEFT)
# on_thresh = Entry(frame5)
# on_thresh.pack(side=LEFT)

# text6 = Label(frame6, text='Enter Offset Threshold:                                   ')
# text6.pack(side=LEFT)
# off_thresh = Entry(frame6)
# off_thresh.pack(side=LEFT)
 
text7 = Label(frame7, text='Enter Fixation Radius (px):                             ')
text7.pack(side=LEFT)
fix_radius = Entry(frame7)
fix_radius.pack(side=LEFT)

text8 = Label(frame8, text='Enter Fixation Duration Threshold (ms):      ')
text8.pack(side=LEFT)
dur_thresh = Entry(frame8)
dur_thresh.pack(side=LEFT)

text9 = Label(frame9, text='Enter Performance file name  (only for Gazepoint):                        ')
text9.pack(side=LEFT)
inputPerf_name = Entry(frame9)
inputPerf_name.pack(side=LEFT)

text10= Label(frame10, text='Enter xError (only for Gazepoint):                ')
text10.pack(side=LEFT)
xError = Entry(frame10) #error for horizontal direction
xError.pack(side=LEFT)

text11 = Label(frame11, text='Enter yError (only for Gazepoint):               ')
text11.pack(side=LEFT)
yError = Entry(frame11) #error for vertical direction
yError.pack(side=LEFT)

# text9 = Label(frame9, text='Enter Participant Number:                             ')
# text9.pack(side=LEFT)
# participant = Entry(frame9)
# participant.pack(side=LEFT)

# text10 = Label(frame10, text='Enter Workload type:                                      ')
# text10.pack(side=LEFT)
# workload = Entry(frame10)
# workload.pack(side=LEFT)
one = Button(window, text="Gazepoint", width="10", height="3",command=lambda : event_detection(1))
one.pack(side="top")

two = Button(window, text="FOVIO", width="10", height="3", command=lambda : event_detection(2))
two.pack(side="top")

text12 = Label(frame12, text='Status: N/A')
text12.pack()

window.mainloop()