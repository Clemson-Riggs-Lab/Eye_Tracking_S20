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
from scipy.signal import savgol_filter

def eyeTracking():       
    file=input_name.get()
    newfile = output_name.get()
    t= tracker_type.get() # t stores the tracker_type int variable
    file_name = input_name.get()
    if path.exists(file_name) and os.path.isfile(file_name):     #Checking that input file is valid
        if output_name.get() == '':
            Status.configure(text='Status:Output file name not specified!')
            return
        if (t==2 and (t0.get()=='' or tf.get() =='')):
            Status.configure(text='Status: Times not specified!')
            return
        start_time=int(t0.get())
        end_time=int(tf.get())
        # We will use the start and end times to only use the data within these two values and discard all the rest
        df = pd.read_csv(file_name) 
        if t ==2:  #truncate the dataframe if the tracker is a FOVIO one      
            df=df[(df.Time>=start_time)&(df.Time<=end_time)]
            df.reset_index(drop=True, inplace=True)
            samp_rate=16.6667
            w=2560 #width of screen in pixels
            h=1600 #height of screen in pixels
            screen=32 #diagonal of screen in inches
            D = 29.5 #participants distance from screen in inches
            herz=60 #refresh rate of eye tracker
            period = float(1.0/float(herz)) #period of the eye tracker (i.e. time between samples)
        else:
            w=2560 #width of screen in pixels
            h=1440 #height of screen in pixels
            screen=24 #diagonal of screen in inches
            D = 23.6 #participants distance from screen in inches
            herz=150 #refresh rate of eye tracker
            period = float(1.0/float(herz)) #period of the eye tracker (i.e. time between samples)
        ##############################################
        df=preProcess(t,df)
        df=missingDataCheck(t,df,file)
        #df= butter(t,df) # the panda dataframe that we wil carry throughout the whole process
        df=VelocityCalculation(t,df)
        df=ThresholdEstimation(df)
        # after all changes are made
        df.drop(df.filter(regex="Unnamed"),axis=1, inplace=True)
        if 'Panel' in df.columns:
            del df['Panel']
        if 'Panel.1' in df.columns:
            del df['Panel.1']
        if 'Occurences' in df.columns:
            del df['Occurences']
        df.to_csv(newfile, index=False)
        Status.configure(text='Success!')  
    else:
        Status.configure(text='Status: Invalid input path!')        
    return
# def butter(tracker_type,df):
#         #Converting coordinates into arrays that are usable by filtfilt function
#     x = np.array(df["BestPogX"])
#     y = np.array(df["BestPogY"])
#     order = int(N.get())
#     freq = float(fc.get())
#     #Creating the filter
#     if tracker_type == 1:
#             B, A = signal.butter(order, freq, fs=150, output='ba')      
#     elif tracker_type == 2:    
#             B, A = signal.butter(order, freq, fs=60, output='ba') 
#     #Passing x and y coordinates through the filter
#     filtered_x = signal.filtfilt(B, A, x)
#     filtered_y = signal.filtfilt(B, A, y)
#     #Changing updating the coordinates with the filtered ones
#     df["BestPogX"] = filtered_x
#     df["BestPogY"] = filtered_y 
#     fig, axs = plt.subplots(2)
#     axs[0].plot(x, linewidth=1)
#     axs[1].plot(filtered_x, linewidth=1)
#     plt.show()           
#     return df
def preProcess(tracker_type,df):
        # Default width is 2560 and default height is 1440 for Gazepoint
        column_names_X = []
        column_names_Y = []
        column_names_bool = []
        column_names_Pupil_Diameter = []
        if tracker_type == 1:
            # Default width is 2560 and default height is 1440 for Gazepoint
            # Tracker used is that of experiment 1
            # all the names of the columns we want to convert proportions to pixels for
            width_of_screen = int(2560)
            height_of_screen = int(1440)
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
            # Find BestPogX and BestPogY values for FOVIO tracker
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
def missingDataCheck(tracker_type,df,file):
        output_file = open("ErrorLog.txt", "w")
        output_file.write(
        'File name:'+str(file)+'\n')
        output_file.write(
        '-------------------------------------------------------------------------'+'\n')
        X_coords = []
        Y_coords = []
        negative_coordinates = []
        missing_packets = []
        marker_bad = []
        final_index = len(df.index)
        final_time = df.iloc[-1]['Time'] 
        '''----------checking errors in the file-----------------'''
        #Function returns the following lists given the dataframe        
        negative_coordinates,missing_packets,marker_bad,X_coords,Y_coords = CheckErrors(df,output_file,tracker_type)
        '''----------gathering statistics-----------------'''
        Statistics(negative_coordinates,missing_packets,marker_bad,final_index,final_time,file,output_file,tracker_type)
        '''----------deleting errors from file-----------------'''
        # combining the lists together for duplicate rows
        combined_list = list(set(negative_coordinates).union(set(marker_bad)))
        df=DeleteErrors(combined_list,missing_packets,df)
        '''-------------displaying the plot-------------------'''
        ScatterPlot(X_coords,Y_coords,file)
        '''-------------displaying the plot-------------------'''
        TimeGap(tracker_type,df,output_file)
        return df
def Statistics(negative_coords,missing_data,bad_markers,final_index,final_time,file,output_file,tracker_type):     
        #writing summary statistics

        output_file.write('\nTotal Negative/Zero/Impossible Coordinates: ' + str(len(negative_coords)) + '\n')
        output_file.write('Total Unordered Data Packets: ' + str(len(missing_data)) + '\n')
        if tracker_type==1:
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
            'Negative/Zero/Impossible Coordinates: ' + str(
                percentage_impossible) + '%' + '\n')
        output_file.write('Unordered Data Packets: ' + str(
            percentage_packets) + '%' + '\n')
        if tracker_type==1:
            output_file.write(
                'Invalid Data based on Eye Tracker: ' + str(
                    percentage_gazepoint) + '%' + '\n')

        # Time recorded is in ms, fetch last time recorded in csv file
        total_time_seconds = final_time / 1000
        total_time_minutes = total_time_seconds / 60

        output_file.write('\nTotal Time Elapsed: ' + str(total_time_minutes) + ' minutes (' + str(
            total_time_seconds) + ' seconds)' + '\n')

        # combining the lists together for duplicate rows
        combined_list = list(set(negative_coords).union(set(bad_markers)))
        if tracker_type == 1:
            total_error_time_seconds = len(combined_list)/6.6667 #multiply by 1/refresh rate
            total_error_time_seconds = total_error_time_seconds/1000 #convert to seconds            
        elif tracker_type ==2: 
            total_error_time_seconds = len(combined_list) / 16.6667 
            total_error_time_seconds = total_error_time_seconds/1000 #convert to seconds
        total_error_time_minutes = total_error_time_seconds / 60

        output_file.write('Total Amount Of Time Of Invalid Data: ' + str(total_error_time_minutes) + ' minutes (' + str(total_error_time_seconds) + ' seconds)' + '\n')  
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
                if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][i] >= 1600:
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
            if valid_point == TRUE and (i%100==0): #modulo condition to reduce number of points and explore a wider scope (take 1 point every 100 iterations)
                X_coords.append(df['BestPogX'][i])
                Y_coords.append(df['BestPogY'][i])
            valid_point = TRUE #reset boolean variable for next iteration
        return negative_coordinates,missing_packets,marker_bad,X_coords,Y_coords
def ScatterPlot(X_coords,Y_coords,file):
        # displaying points on the background ... density inversely related to number
        plt.scatter(X_coords,Y_coords, s=2, c='r')
        plt.title(file)
        plt.show()
def DeleteErrors(combined_list,missing_packets,df):
        if v == 1: #.get()
            df.drop(combined_list, axis=0, inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif v == 2: #.get()
            #do the stuff with marking the excel file here'

            defaultvals = ['0'] * len(df.index)

            for each in combined_list:
                defaultvals[each] = 'ERROR'

            for each in missing_packets:
                defaultvals[each] = 'Packet ERROR'

            series = pd.Series(defaultvals)
            df['MissingDataCheck'] = series  
        return df
def VelocityCalculation(tracker_type,df):
# In this function we calculate the velocity of gazepoints with the SG filter approach and append the to the dataframe.We also compute the velocity with the 2-tap (sample-to-sample approach)
    dfwidth=5 #window length for SG filter
    dfdegree=2 #order of the polynomial for SG filter
    dfo=1 #level of derivative for SG filter. 1 because we want to calculate velocity between points as we smooth
    
    #separate data out by x and y coordinates
    XCoord=df["BestPogX"]
    YCoord=df["BestPogY"]
    #filter x and y coordinates with the inputted filter length, polynomial order, and derivative level with SG approach
    FiltXCoord=savgol_filter(XCoord, window_length = dfwidth, polyorder = dfdegree, deriv = dfo)
    FiltYCoord=savgol_filter(YCoord, window_length = dfwidth, polyorder = dfdegree, deriv = dfo)
    #collecting information in order to convert derivative to visual angle and calculate velocity (i.e. divide by time elapsed)
    dt = period * float(dfwidth) #change of time between samples to account for the fact multiple were accounted for velocity calculation
    r = math.sqrt(float(w)*float(w) + float(h)*float(h)) #pythagorean theorem to get hypotenuse of screen (i.e. screen diagonal) in units of pixels
    ppi = r/float(screen) #pixels per inch
    #convert pixels to degrees of visual angle. store in a array for later mathematical calculations
    degx=[0]*len(FiltXCoord)
    degy=[0]*len(FiltYCoord)
    for point in range(len(FiltXCoord)):
        degx[point]=math.degrees(math.atan2((FiltXCoord[point]/ppi),(2*D)))
        degy[point]=math.degrees(math.atan2((FiltYCoord[point]/ppi),(2*D)))
    degx=np.array(degx)
    degy=np.array(degy)
    #calculate velocity for x and y and then combine for a singular velocity value
    velx= degx/dt 
    vely= degy/dt    
    vel=[0]*len(velx)
    for a in range(len(velx)):
        vel[a] = math.sqrt(velx[a]*velx[a] + vely[a]*vely[a])
    df["Velocity (degrees of visual angle/second)"]=vel
    ###2 tap (sample-to-sample) velocity calculation approach
    #keeping so (1) less chance of code breaking (2) for comparative reference
    Delta = [] #in pixels
    Angular_Velocity = []
    Delta_mm = []
    Delta_rad = [] 
    inch_to_mm=25.4
    rad_to_degrees = 57.29577951

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
                pixel_to_mm=0.207565625
                Delta.append(math.sqrt(pow(x1,2)+pow(y1,2)))
                Delta_mm.append(Delta[i]*pixel_to_mm)
                Delta_rad.append(math.atan(Delta_mm[i]/(D*inch_to_mm)))
                velocity = Delta_rad[i]*rad_to_degrees/time_diff #convert to degrees and divide by time difference
                Angular_Velocity.append(velocity)
                
            elif tracker_type ==2: #If FOVIO Tracker
                pixel_to_mm=0.269279688
                Delta.append(math.sqrt(pow(x1,2)+pow(y1,2)))
                Delta_mm.append(Delta[i]*pixel_to_mm)
                Delta_rad.append(math.atan(Delta_mm[i]/(D*inch_to_mm)))
                velocity = Delta_rad[i]*rad_to_degrees*1000/time_diff #convert to degrees and divide by time difference
                Angular_Velocity.append(velocity)
      
    df['Delta (in pixels)'] = Delta #Create a new column and append the visual angle values in pixels
    df['Delta (in mm)'] = Delta_mm #Create a new column and append the visual angle values in mm
    df['Delta (in rad)'] = Delta_rad #Create a new column and append the visual angle values in rad
    df['2 point velocity (degrees/second)'] = Angular_Velocity #Create a new column and append the angular velocity in degrees per second
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
        vel_list.clear #clear list at each iteration according to Holmqvist's desription of the algorithm
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
def TimeGap(tracker_type,df,output_file):
    #This function calculates the time gap in seconds
    times=[]
    times = df['Time']
    gap = 0
    for i in range(0,len(times)-1): 
        diff = times[i+1]-times[i]
        if diff>gap:
            gap=diff
    if tracker_type ==2: #FOVIO time is in ms while Gazepoint time is in second
        gap=gap/1000
    output_file.write('\nLargest Timegap of missing data: ' + str(gap) +' seconds' + '\n')    
    return
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
frame15  = Frame(window)
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
frame15.pack()

window.title("Eye Tracking Data")

text0 = Label(frame0,
              text='\n 1. Basic Information: \n')
text0.pack()
text14 = Label(frame1,
              text='\n Select Tracker Type: \n')
text14.pack()
tracker_type = IntVar() #tracker type variable
button4 = Radiobutton(frame2,
              text="Gazepoint",
              padx = 200,
              variable=tracker_type,
              value=1).pack()
button5 = Radiobutton(frame3,
              text="      FOVIO",
              padx = 20,
              variable=tracker_type,
              value=2).pack()

text3 = Label(frame4, text='Enter Input File/Folder Name (include .csv):  ')
text3.pack(side=LEFT)
input_name = Entry(frame4) # input name variable 
input_name.pack(side=LEFT)

text4 = Label(frame5, text='Enter Output File Name (include .csv):           ')
text4.pack(side=LEFT)
output_name = Entry(frame5) #output name variable
output_name.pack(side=LEFT)

text5 = Label(frame6, text='Enter start time(ms):                                          ')
text5.pack(side=LEFT)
t0 = Entry(frame6) # input name variable 
t0.pack(side=LEFT)

text6 = Label(frame7, text='Enter end time (ms):                                          ')
text6.pack(side=LEFT)
tf = Entry(frame7) #output name variable
tf.pack(side=LEFT)

# text7 = Label(frame8,
#               text='\n 2. Butterworth Filtering Information:\n')
# text7.pack()

# text8 = Label(frame9, text='Enter filter order (N):                                         ')
# text8.pack(side=LEFT)
# N = Entry(frame9) #Filter order variable
# N.pack(side=LEFT)

# text9 = Label(frame10, text='Enter the critical frequency (fc):                          ')
# text9.pack(side=LEFT)
# fc = Entry(frame10) #fc variable
# fc.pack(side=LEFT)

text10 = Label(frame11,
              text='\n 3. Missing Data Check Information:\n')
text10.pack()

v = IntVar() # Options variable

button2 = Radiobutton(frame12,
              text="                   Delete rows in output file",
              padx = 20,
              variable=v,
              value=1).pack()
button3 = Radiobutton(frame13,
              text="Mark in separate Excel file for review",
              padx = 20,
              variable=v,
              value=2).pack()




one = Button(window, text="GO", width="10", height="2",command=lambda : eyeTracking())
one.pack(side="top")

Status = Label(frame14, text='Status: N/A')
Status.pack()

window.mainloop()

