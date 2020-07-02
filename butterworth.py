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
#Sam Smith (sjs5pg)
# 07/01/2020
"""
This file applies a butterworth filter to the left and right
coordinates from an eyetracking file. 
"""

#Reference for how to set up the filter 
#https://oceanpython.org/2013/03/11/signal-filtering-butterworth-filter/


def butter():
    #Checking that input file is valid
    if path.exists(inputET_name.get()) and os.path.isfile(inputET_name.get()):
        df = pd.read_csv(inputET_name.get())
        #Converting coordinates into arrays that are usable by filtfilt function
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
        df.to_csv("output_butter.csv")
        text4.configure(text='Status: Success! Left and right eye coordinates from ' + inputET_name.get() + ' have been filtered.')
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
        text4.configure(text='Input file not found! Try again.')

  

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

text0 = Label(frame0, text='Enter Eyetracking file name: ')
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

button1 = Button(frame3, text='Submit',command=butter)
button1.pack(side=RIGHT)

text4 = Label(frame4, text='Status: N/A')
text4.pack()

window.mainloop()