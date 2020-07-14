# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 14:28:58 2020
July 2nd: 
Sam added code for Gaze Point Eye Tracker.
July 12th: 
Jad Atweh Added a code for FOVIO Eye Tracker.
July 13th:
Jad Atweh combined both codes and altered the GUI for the user to choose which tracker is used.

"""


import pandas as pd
from os import path
import math
from datetime import time, datetime, timedelta
from tkinter import *
from os import path
import os
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

"""
This files enables the user to choose if he/she is using eye tracker 1: Gaze Point Eye Tracker or eye tracker 2: FOVIO eye tracker and the the appropriate code will run accordingly.
"""

#Reference for how to set up the filter 
#https://oceanpython.org/2013/03/11/signal-filtering-butterworth-filter


def butter(tracker_type):
    #Checking that input file is valid
    if path.exists(inputET_name.get()) and os.path.isfile(inputET_name.get()) and path.exists(inputET_name.get()) and os.path.isfile(inputET_name.get()):
        df = pd.read_csv(inputET_name.get())
        #Converting coordinates into arrays that are usable by filtfilt function
        # In the FOVIO eye tracker, the coordinates are x and y but for each eye
        if tracker_type == 1:
            x = np.array(df["BestPogX"])
            y = np.array(df["BestPogY"])
            order = int(N.get())
            freq = float(Wn.get())
            #Creating the filter
            B, A = signal.butter(order, freq, output='ba')
            #Passing x and y coordinates through the filter
            filtered_x = signal.filtfilt(B, A, x)
            filtered_y = signal.filtfilt(B, A, y)
            #Changing updating the coordinates with the filtered ones
            df["BestPogX"] = filtered_x
            df["BestPogY"] = filtered_y
            df.to_csv(output_file.get())
            text5.configure(text='Status: Success! Left and right eye coordinates from ' + inputET_name.get() + ' have been filtered into ' + output_file.get() + '.')
            
            #Before and after plot to see the difference
            plt.plot(filtered_x, linewidth=2.0)
            plt.plot(x, linewidth=.75)
            plt.show()
        
        elif tracker_type == 2:      
            x = np.array(df["Lft X Pos"])
            y = np.array(df["Lft Y Pos"])
            z = np.array(df["Rt X Pos"])
            w = np.array(df["Rt Y Pos"])
            order = int(N.get())
            freq = float(Wn.get())
            #Creating the filter
            B, A = signal.butter(order, freq, output='ba')
            #Passing x and y coordinates through the filter
            filtered_x = signal.filtfilt(B, A, x)
            filtered_y = signal.filtfilt(B, A, y)
            filtered_z = signal.filtfilt(B, A, z)
            filtered_w = signal.filtfilt(B, A, w)
            #Changing updating the coordinates with the filtered ones
            df["Lft X Pos"] = filtered_x
            df["Lft Y Pos"] = filtered_y
            df["Rt X Pos"] = filtered_z
            df["Rt Y Pos"] = filtered_w 
            df.to_csv(output_file.get())
            text5.configure(text='Status: Success! Left and right eye coordinates from ' + inputET_name.get() + ' have been filtered into ' + output_file.get() + '.')
            """
            If you are testing this file out, I would suggest using matplotlib to see the
            original data on a graph versus the smoothed data from after the filter was applied.
            For example, the commented code below plots both the filtered x coordinates and the raw 
            x coordinates. 
            """
            plt.plot(filtered_x, linewidth=2.0)
            plt.plot(x, linewidth=.75)
            plt.show()
        
   
    else:
        text5.configure(text='Error. Make sure both your input and output files exist.')

  

#setting up GUI
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

window.title("Data Quality GUI")

text0 = Label(frame0, text='Enter Eye tracking file name (.csv): ')
text0.pack(side=LEFT)
inputET_name = Entry(frame0)
inputET_name.pack(side=LEFT)

text1 = Label(frame1, text='Enter order of the filter (N): ')
text1.pack(side=LEFT)
N = Entry(frame1)
N.pack(side=LEFT)

text2 = Label(frame2, text='Enter critical frequency (Wn, must be between 0 and 1): ')
text2.pack(side=LEFT)
Wn = Entry(frame2)
Wn.pack(side=LEFT)

text3 = Label(frame3, text='Enter output file name(.csv): ')
text3.pack(side=LEFT)
output_file = Entry(frame3)
output_file.pack(side=LEFT)

text4 = Label(frame5, text='Eye Tracker Type: Choose which eye tracker you are using')
text4.pack(side=LEFT)


one = Button(window, text="GazePoint", width="10", height="3",command=lambda : butter(1))
one.pack(side="top")


two = Button(window, text="FOVIO", width="10", height="3", command=lambda : butter(2))
two.pack(side="top")

text5 = Label(frame7, text='Status: N/A')
text5.pack(side=LEFT)

window.mainloop()