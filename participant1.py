#This file reads in data from one of the sample files
#that Shannon sent and and multiplies the x and y positions of the left eye
#by the correct dimensions.
import numpy as np
import matplotlib.pyplot as plt

x = open("practicedata1.csv", 'r')
lines = x.readlines()

#Finding the data we need in the csv 
columns = lines[0]
colLst = columns.split(',')
leftpogy = 0
leftpogx = 0
i = 0
for col in colLst:
    if col=="LeftPogX":
        leftpogx = i
    if col=="LeftPogY":
        leftpogy = i
    i+=1


l = lines[2].split(',')
# print(l[24])
# print(leftpogx)

counter = 0

#First two lines do not have floating point values in left eye positions 
#Only going to 50000, python doing unexpected things when intputting full list 
lstx = []
lsty = []
for i in range(2, 50000):
    cells = lines[i].split(',')

    x = float((cells[leftpogx]))*2560

    y = float((cells[leftpogy]))*1440
    lstx.append(x)
    lsty.append(y)

    strx = str(x)
    stry = str(y)
    
    #print(strx)

x = lstx
y = lsty

plt.plot(x)
plt.show()




