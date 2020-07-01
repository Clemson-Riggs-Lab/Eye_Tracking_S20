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

"""
The code is working, now I just need to put everything
into a GUI.
"""

df = pd.read_csv("2ndTask_ET.csv")
x = np.array(df["BestPogX"])
y = np.array(df["BestPogY"])

N=2
Wn = 0.01
B, A = signal.butter(N, Wn, output='ba')
filtered_x = signal.filtfilt(B, A, x)
filtered_y = signal.filtfilt(B, A, y)
df["BestPogX"] = filtered_x
df["BestPohY"] = filtered_y

plt.plot(filtered_x)
plt.plot(filtered_y)

plt.show()