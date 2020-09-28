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
all_indices=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
onset_indices=[4,10,17]
offset_indices=[6,12,19]
#NOTE: THIS NEEDS TO BE STORED VALUES PROVIDED BY THE USER. E.g. FOVIO has a sample rate of 16.6667 and Gazepoint has a sample rate of 6.66667 so need the user to either enter this value or add FOVIO and Gazepoint buttons to the GUI like we have for every other script
samp_rate=16.6667
min_dur=30
spatial_threshold=1

##################################FINDING ALL FIXATION INDICES##############################
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
    
j=(offset_indices[len(offset_indices)-1])+1
mini_lst = []
while j < len(all_indices):#all_indices would be length of the original entered df
    mini_lst.append(j)
    j+=1
fixation_indices.append(mini_lst)
   
###########################FIXATION DETECTION CODE####################### 
#initialize list variables for storing fixation indices after the spatial and duration constraitns are applied
fixations_after_constraints = []
center_points = []
for fixation in fixation_indices: #loop thur the list of lists to apply thresholds
    #initialize variables   
    g=""
    fix_lst=[]
    if len(fixation) < 2: #if a given mini fixation list only has two or less points, just skip this list entirely
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
                dist = fixation[index]-g #normally we would be doing the distance calculation as detatiled in the calculateDistance function, but just did a difference between index values for distance since I was testing with index values and not their associated coordinates
                if dist <= spatial_threshold: #made up threshold for testing code purposes, but for our work, we do not want to hardcode any values and would want to ask the user for this value in the GUI and store it 
                    fix_lst.append(fixation[index])#add the index to the list that is storing "close" fixation indices
                    index+=1 #increase the counter to search for the next index and test its distance
                    if index >= len(fixation): #This might seem like a random/unnecessary check here but if we increase the counter and then are at the end of this fixation index list, if we immediately go to the while loop this code is all housed in (line 66) we will lose any collection of fixation indices we just previously collected. So we need to proactively check the duration value to see what we have collected thus far is a potential fixation before going to the next mini list (i.e. what is called fixation)
                        if len(fix_lst) * samp_rate>min_dur: #made up threshold for testing code purposes, but for our work, we do not want to hardcode any values and would want to ask the user for this value in the GUI and store it 
                            #store this collection of indices since it meets spatial and duration constriants and store its center point separate so we can pull its x,y coordinates for the output file
                            fixations_after_constraints.append(fix_lst)
                            center_points.append(fix_lst[0])
                            #exit the while to go back to the over arching for loop since we are at the last index of the mini list
                            break
                        else: #if the last points in the list do not meet the duraiton threshold, then go to the next fixation incdice list
                            break       
                else: #if the current index is outside the spatial threshold, check to see if the previous collected indices fits the duration threshold
                    if len(fix_lst) * samp_rate>min_dur:
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
                        g=fixation[z+1] #the new g is determined by z and not index because we had collection of points that were closer togetehr but did not meet the duration threshold so we need to go to the point that is after g, not the next index point as it might be a few point from g
                        fix_lst=[]
                        fix_lst=[g]
            else: #this section of code is if this is not our first search in the mini list (i.e. what is called fixation), complete the same process with the updated g value                                  
                dist = fixation[index]-g
                if dist <= spatial_threshold:
                    fix_lst.append(fixation[index])
                    index+=1
                    if index >= len(fixation):
                        if len(fix_lst) * samp_rate>min_dur:
                            fixations_after_constraints.append(fix_lst)
                            center_points.append(fix_lst[0])
                            break
                        else: 
                            break                           
                else:                                   
                    if len(fix_lst) * samp_rate>min_dur:
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
                        g=fixation[z+1]
                        fix_lst=[]
                        fix_lst=[g]
