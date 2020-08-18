# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 13:39:55 2020

@author: Iska1999
"""

import pandas as pd
import statistics
from tkinter import *
from os import path
import os
import numpy as np
import math
from os import path
from datetime import time, datetime, timedelta
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

def eyeTracking():
        #Checking that input file is valid
    file_name = input_name.get()
    if path.exists(file_name) and os.path.isfile(file_name):
        if output_name.get() == '':
            Status.configure(text='Status:Output file name not specified!')
            return
        file=input_name.get()
        newfile = output_name.get()
        df = pd.read_csv(file_name)
        t= tracker_type.get() # t stores the tracker_type int variable
        df= butter(t,df) # the panda dataframe that we wil carry throughout the whole process
        df=preProcess(t,df)
        df=missingDataCheck(t,df,file)
        df=VelocityCalculation(t,df)
        df=ThresholdEstimation(df)
        # after all changes are made
        df.to_csv(newfile, index=False)
        Status.configure(text='Success!')  
    else:
        Status.configure(text='Status: Invalid input path!')        
    return
def butter(tracker_type,df):
        #Converting coordinates into arrays that are usable by filtfilt function
    if tracker_type == 1:
            x = np.array(df["BestPogX"])
            y = np.array(df["BestPogY"])
            order = int(N.get())
            freq = float(Wn.get())
            #Creating the filter
            B, A = signal.butter(order, freq, fs=150, output='ba')
            #Passing x and y coordinates through the filter
            filtered_x = signal.filtfilt(B, A, x)
            filtered_y = signal.filtfilt(B, A, y)
            #Changing updating the coordinates with the filtered ones
            df["BestPogX"] = filtered_x
            df["BestPogY"] = filtered_y
            
            
            #Before and after plot to see the difference

            
            fig, axs = plt.subplots(2)
            axs[0].plot(x, linewidth=1)
            axs[1].plot(filtered_x, linewidth=1)
            plt.show()      
    elif tracker_type == 2:    
            x = np.array(df["Lft X Pos"])
            y = np.array(df["Lft Y Pos"])
  
            order = int(N.get())
            freq = float(Wn.get())
            #Creating the filter
            B, A = signal.butter(order, freq, fs=60, output='ba')
            #Passing x and y coordinates through the filter
            filtered_x = signal.filtfilt(B, A, x)
            filtered_y = signal.filtfilt(B, A, y)
        
            #Changing updating the coordinates with the filtered ones
            df["Lft X Pos"] = filtered_x
            df["Lft Y Pos"] = filtered_y
            df["Rt X Pos"] = filtered_x
            df["Rt Y Pos"] = filtered_y            
            fig, axs = plt.subplots(2)
            axs[0].plot(x, linewidth=1)
            axs[1].plot(filtered_x, linewidth=1)
            plt.show()
    return df
def preProcess(tracker_type,df):
        # Default width is 2560 and default height is 1440
        if x_response.get() == '':
            width_of_screen = 2560
        else:
            width_of_screen = x_response.get()

        if y_response.get() == '':
            height_of_screen = 1440
        else:
            height_of_screen = y_response.get()
        column_names_X = []
        column_names_Y = []
        column_names_bool = []
        column_names_Pupil_Diameter = []
        if tracker_type == 1:
            # Tracker used is that of experiment 1
            # all the names of the columns we want to convert proportions to pixels for
            column_names_X = ['CursorX', 'LeftEyeX', 'RightEyeX', 'FixedPogX', 'LeftPogX', 'RightPogX', 'BestPogX',
                              'LeftPupilX', 'RightPupilX']
            column_names_Y = ['CursorY', 'LeftEyeY', 'RightEyeY', 'FixedPogY', 'LeftPogY', 'RightPogY', 'BestPogY',
                              'LeftPupilY', 'RightPupilY']
            column_names_bool = ['LeftEyePupilValid', 'RightEyePupilValid', 'FixedPogValid', 'LeftPogValid',
                                 'RightPogValid', 'BestPogValid', 'LeftPupilValid', 'RightPupilValid', 'MarkerValid']
            column_names_Pupil_Diameter = ['LeftEyePupilDiamet', 'RightEyePupilDiame']

            # turn TRUES and FALSES to 1s and 0s
            for each in column_names_bool:
                df[each].replace(True, 1, inplace=True)
                df[each].replace(False, 0, inplace=True)
            # CHANGE RESOLUTION OF X HERE
            for each in column_names_X:
                df[each] = df[each].multiply(width_of_screen)

            # CHANGE RESOLUTION OF Y HERE
            for each in column_names_Y:
                df[each] = df[each].multiply(height_of_screen)
                
        elif tracker_type == 2:
             #Tracker used is that of experiment 2 (60 Hz)
             column_names_X = ['Lft X Pos', 'Rt X Pos', 'L Eye Rot (X)', 'R Eye Rot (X)','L Eye Pos (X)','R Eye Pos (X)',
                               'Head Rot (X)','Head Pos (X)']
             column_names_Y = ['Lft Y Pos', 'Rt Y Pos', 'L Eye Rot (Y)', 'R Eye Rot (Y)','L Eye Pos (Y)','R Eye Pos (Y)',
                               'Head Rot (Y)','Head Pos (Y)']
             column_names_Pupil_Diameter = ['Lft Pupil Diameter', 'Rt Pupil Diameter']  
        return df             
def missingDataCheck(tracker_type,df,file):
        output_file = open("ErrorLog.txt", "w")
        X_coords = []
        Y_coords = []
        negative_coordinates = []
        missing_packets = []
        marker_bad = []
        final_index = len(df.index)
        final_time = df.iloc[-1]['Time'] 
        if tracker_type ==2:
            df=FOVIOPog(df)
        '''----------checking errors in the file-----------------'''
        #Function returns the following lists given the dataframe        
        negative_coordinates,missing_packets,marker_bad,X_coords,Y_coords = CheckErrors(df,output_file,tracker_type)
        '''----------gathering statistics-----------------'''
        Statistics(negative_coordinates,missing_packets,marker_bad,final_index,final_time,output_file)
        '''----------deleting errors from file-----------------'''
        # combining the lists together for duplicate rows
        combined_list = list(set(negative_coordinates).union(set(marker_bad)))
        df=DeleteErrors(combined_list,missing_packets,df)
        '''-------------displaying the plot-------------------'''
        ScatterPlot(X_coords,Y_coords,file)
        return df
def Statistics(negative_coords,missing_data,bad_markers,final_index,final_time,output_file):     
        #writing summary statistics
        output_file.write('\nTotal Negative/Zero/Impossible Coordinates: ' + str(len(negative_coords)) + '\n')
        output_file.write('Total Unordered Data Packets: ' + str(len(missing_data)) + '\n')
        output_file.write('Total Invalid Data based on Gazepoint: ' + str(len(bad_markers)) + '\n')

        #calculating more summary statistics
        proportion_impossible = len(negative_coords) / final_index
        proportion_packets = len(missing_data) / final_index
        proportion_gazepoint = len(bad_markers) / final_index
        percentage_impossible = len(negative_coords) / final_index * 100
        percentage_packets = len(missing_data) / final_index * 100
        percentage_gazepoint = len(bad_markers) / final_index * 100

        #write these additional statistics to the output file
        output_file.write(
            '\nProportion of Negative/Zero/Impossible Coordinates: ' + str(proportion_impossible) + ' (' + str(
                percentage_impossible) + '%)' + '\n')
        output_file.write('Proportion of Unordered Data Packets: ' + str(proportion_packets) + ' (' + str(
            percentage_packets) + '%)' + '\n')
        output_file.write(
            'Proportion of Invalid Data based on Gazepoint: ' + str(proportion_gazepoint) + ' (' + str(
                percentage_gazepoint) + '%)' + '\n')

        # Time recorded is in ms, fetch last time recorded in csv file
        total_time_seconds = final_time / 1000
        total_time_minutes = total_time_seconds / 60

        output_file.write('\nTotal Time Elapsed: ' + str(total_time_minutes) + ' minutes (' + str(
            total_time_seconds) + ' seconds)' + '\n')

        # combining the lists together for duplicate rows
        combined_list = list(set(negative_coords).union(set(bad_markers)))

        total_error_time_seconds = len(combined_list) / 150
        total_error_time_minutes = total_error_time_seconds / 60

        output_file.write('Error Time Elapsed: ' + str(total_error_time_minutes) + ' minutes (' + str(total_error_time_seconds) + ' seconds)' + '\n')  
def CheckErrors(df,output_file,tracker):
        X_coords = []
        Y_coords = []
        valid_point = TRUE #initial condition of boolean. If it fails any of the checks, it flips to FALSE. If it remains true, it is a valid point
        negative_coordinates = []
        missing_packets = []
        marker_bad = []
        #identify and report bad data (coordinates that are negative or greater than 2560x1440)
        for i in range(0,len(df.index)):
            #If gazepoint tracker
            if tracker ==1:
                if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][i] >= 1440:
                    output_file.write('Row ' + str(i + 2) + ': Negative/Zero/Impossible Coordinates (Columns AE and AF)\n')
                    negative_coordinates.append(i)
                    valid_point = FALSE    
                #ignore the first loop to avoid errors
                if i == 0:
                    ...
                else:
                    #check for missing data ... see how the packet counter is
                    if df['Counter'][i] != df['Counter'][i-1] + 1:
                        output_file.write('Row ' + str(i + 2) + ': Unordered Data Packet Counters (Column E)\n')
                        missing_packets.append(i)
                        valid_point = FALSE
                #report when gazepoint has a 0 in the BESTPOGVALID column
                if df['BestPogValid'][i] != 1:
                    output_file.write('Row ' + str(i + 2) + ': Invalid Data based on Gazepoint (Column AG)\n')
                    marker_bad.append(i)
                    valid_point = FALSE
            #If FOVIO tracker        
            elif tracker ==2:
                #Check if recorded coordinates are within the resolution ranges
                if df['Lft X Pos'][i] <= 0 or df['Lft X Pos'][i] >= 2560 or df['Rt X Pos'][i] <= 0 or df['Rt X Pos'][i] >= 2560 or df['Lft Y Pos'][i] <= 0 or df['Lft Y Pos'][i] >= 1440  or df['Rt Y Pos'][i] <= 0 or df['Rt Y Pos'][i] >= 1440 :
                    output_file.write('Row ' + str(i + 2) + ': Negative/Zero/Impossible Coordinates\n')
                    negative_coordinates.append(i)
                    valid_point = FALSE
                #ignore the first loop to avoid errors
                if i == 0:
                    ...
                else:
                    #check for missing data by verifying the continuity of the frames column
                    if df['Frame'][i] != df['Frame'][i-1] + 1:
                        output_file.write('Row ' + str(i + 2) + ': Unordered Data Packet Counters\n')
                        missing_packets.append(i)
                        valid_point = FALSE
                #report when gazepoint has a 0 in the either L Display or R Display columns
                if df['L Display'][i] == 0 or df['R Display'][i] == 0 :
                    output_file.write('Row ' + str(i + 2) + ': Invalid Data based on Gazepoint\n')
                    marker_bad.append(i)
                    valid_point = FALSE 
            if valid_point == TRUE and (i%100==0): #modulo condition to reduce number of points and explore a wider scope (take 1 point every 100 iterations)
                X_coords.append(df['Lft X Pos'][i])
                Y_coords.append(df['Lft Y Pos'][i])
            valid_point = TRUE #reset boolean variable for next iteration
        return negative_coordinates,missing_packets,marker_bad,X_coords,Y_coords
def ScatterPlot(X_coords,Y_coords,file):
        # displaying points on the background ... density inversely related to number
        plt.scatter(X_coords,Y_coords, s=2, c='r')
        plt.title(file)
        plt.show()
def DeleteErrors(combined_list,missing_packets,df):
        if v.get() == 1:
            df.drop(combined_list, axis=0, inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif v.get() == 2:
            #do the stuff with marking the excel file here'

            defaultvals = ['0'] * len(df.index)

            for each in combined_list:
                defaultvals[each] = 'ERROR'

            for each in missing_packets:
                defaultvals[each] = 'Packet ERROR'

            series = pd.Series(defaultvals)
            df['MissingDataCheck'] = series  
        return df
def FOVIOPog(df):
    BestPogX = []
    BestPogY = []
    for i in range(0,len(df.index)):
        if (df['Lft X Pos'][i]==0) and (df['Rt X Pos'][i] ==0):
            BestPogX.append(0)
        else:
            if (df['Lft X Pos'][i]!=0):
                BestPogX.append((df['Lft X Pos'][i]))
            elif (df['Rt X Pos'][i]!=0):
                BestPogX.append((df['Rt X Pos'][i]))
            
        if (df['Lft Y Pos'][i]==0) and (df['Rt Y Pos'][i] ==0):
            BestPogY.append(0)
        else:
            if (df['Lft Y Pos'][i]!=0):
                BestPogY.append((df['Lft Y Pos'][i]))
            elif (df['Rt Y Pos'][i]!=0):
                BestPogY.append((df['Rt Y Pos'][i]))                  
    df['BestPogX'] = BestPogX #Create a new column and append BestPogX
    df['BestPogY'] = BestPogY #Create a new column and append BestPogY
    return df   
def VelocityCalculation(tracker_type,df):
# In this function we calculate the visual angles, angular velocities, and append the to the dataframe
        Delta = [] #in pixels
        Angular_Velocity = []
        Delta_mm = []
        Delta_rad = [] 
        for i in range(0,len(df.index)):
                if i==len(df.index)-1: #in this case we reach the end of the dataframe and dont have an i+1
                    x1 = df['BestPogX'][i-1]
                    y1 = df['BestPogY'][i-1]  
                    time_diff =abs(df['Time'][i-1])
                    
                else:
                    
                    x1 = df['BestPogX'][i+1]-df['BestPogX'][i]
                    y1 = df['BestPogY'][i+1]-df['BestPogY'][i]
                    time_diff=abs(df['Time'][i+1]-df['Time'][i]) 
                    
                  
                if tracker_type==1: #If Gazepoint Tracker                    
                    Delta.append(math.sqrt(pow(x1,2)+pow(y1,2)))
                    Delta_mm.append(Delta[i]*0.207565625)
                    Delta_rad.append(math.atan(Delta_mm[i]/(23.62204724*25.4)))
                    velocity = Delta_rad[i]*57.29577951/time_diff #convert to degrees and divide by time difference
                    Angular_Velocity.append(velocity)
                    
                elif tracker_type ==2: #If FOVIO Tracker
                    Delta.append(math.sqrt(pow(x1,2)+pow(y1,2)))
                    Delta_mm.append(Delta[i]*0.269279688)
                    Delta_rad.append(math.atan(Delta_mm[i]/(29.5*25.4)))
                    velocity = Delta_rad[i]*57.29577951*1000/time_diff #convert to degrees and divide by time difference
                    Angular_Velocity.append(velocity)
          
        df['Delta (in pixels)'] = Delta #Create a new column and append the visual angle values in pixels
        df['Delta (in mm)'] = Delta_mm #Create a new column and append the visual angle values in mm
        df['Delta (in rad)'] = Delta_rad #Create a new column and append the visual angle values in rad
        df['Angular Velocity (in degrees/second)'] = Angular_Velocity #Create a new column and append the angular velocity in degrees per second
        return df
def ThresholdEstimation(df):
    mean = 0
    std_dev = 0
    summ = 0
    N = 0
    vel_list = []
    PTold = 250 #Dummy value .Initially, it is the value set by us (in the 100-300 degrees/sec range)
    PTnew = 0
    diff = PTnew - PTold
    velocities = df['Angular Velocity (in degrees/second)'] #list of angular velocities, probably a column from a Pandas dataframe 
    mean_velocities=sum(velocities)/len(velocities)
    std_dev_velocities = statistics.stdev(velocities,mean_velocities)
    while abs(diff)>1:
        summ = 0
        N = 0
        for vel in velocities:
            if vel < PTold:
                summ=summ+vel
                N=N+1
                vel_list.append(vel)   
        if (N!=0):
            mean=summ/N
        std_dev = statistics.stdev(vel_list,mean)
        PTold = PTnew
        PTnew = mean +6*std_dev
        onset_threshold = mean +3*std_dev
        offset_threshold = 0.7*onset_threshold + 0.3*(mean_velocities+3*std_dev_velocities)
        diff = PTnew - PTold
        
    df['Peak Threshold']=PTnew
    df['Onset Threshold']=onset_threshold
    df['Offset Threshold']=offset_threshold
    return df

###############################################################################
## UI stuff

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
frame13 = Frame(window)
frame14 = Frame(window)

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
frame13.pack()
frame14.pack()

window.title("Eye Tracking Data")

text0 = Label(frame0,
              text='\n 1. Basic Information: \n')
text0.pack()

text1 = Label(frame1, text='Enter X resolution (default: 2560):                    ')
text1.pack(side=LEFT)
x_response = Entry(frame1) # x resolution variable
x_response.pack(side=LEFT)

text2 = Label(frame2, text='Enter Y resolution (default: 1440):                    ')
text2.pack(side=LEFT)
y_response = Entry(frame2) # y resolution variable
y_response.pack(side=LEFT)

text3 = Label(frame3, text='Enter Input File/Folder Name (include .csv):  ')
text3.pack(side=LEFT)
input_name = Entry(frame3) # input name variable 
input_name.pack(side=LEFT)

text4 = Label(frame4, text='Enter Output File Name (include .csv):            ')
text4.pack(side=LEFT)
output_name = Entry(frame4) #output name variable
output_name.pack(side=LEFT)

text5 = Label(frame5,
              text='\n 2. Filtering Information:\n')
text5.pack()

text6 = Label(frame6, text='Enter filter order (N):                                         ')
text6.pack(side=LEFT)
N = Entry(frame6) #Filter order variable
N.pack(side=LEFT)

text7 = Label(frame7, text='Enter critical frequency (Wn):                          ')
text7.pack(side=LEFT)
Wn = Entry(frame7) #Wn variable
Wn.pack(side=LEFT)

text8 = Label(frame8,
              text='\n 3. MissingDataCheck Information:\n')
text8.pack()

v = IntVar() # Options variable

button2 = Radiobutton(frame9,
              text=" Delete Rows Automatically",
              padx = 20,
              variable=v,
              value=1).pack()
button3 = Radiobutton(frame10,
              text="Mark in Excel File for review",
              padx = 20,
              variable=v,
              value=2).pack()

tracker_type = IntVar() #tracker type variable
text11 = Label(frame11, text='\n 4. Eye Tracker Type: \n')
text11.pack()
button4 = Radiobutton(frame12,
              text="Gazepoint",
              padx = 200,
              variable=tracker_type,
              value=1).pack()
button5 = Radiobutton(frame13,
              text="      FOVIO",
              padx = 20,
              variable=tracker_type,
              value=2).pack()

one = Button(window, text="GO", width="10", height="2",command=lambda : eyeTracking())
one.pack(side="top")

Status = Label(frame14, text='Status: N/A')
Status.pack()

window.mainloop()

