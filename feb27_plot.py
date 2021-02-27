import pandas as pd
from os import path
import math
from datetime import time, datetime, timedelta, date
from tkinter import *
from os import path
import os
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("testForSam1.csv")
velocities = np.array(df["Velocity (degrees of visual angle/second)"])
mission_time = np.array(df["MissionTime"])

plt.scatter(mission_time, velocities, 5)
plt.show()