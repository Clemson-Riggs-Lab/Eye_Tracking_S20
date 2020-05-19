from numpy import c_
'''future potential code to use? can show heat maps but not sure how to exactly use them yet'''
import numpy as np
import matplotlib.pyplot as plt
import random
import pandas
from tkinter import *
'''
Dustin Nguyen
ddn3aq
4/29/20

5/9/20 - added UI to heatmap

'''

def showPlot():
    #reading in the CSV file
    data = pandas.read_csv(str(input_file_response.get()), header=0)

    #change this value to change how detailed the heatmap is... lower numbers mean higher quality.
    precision = int(precision_response.get()) + 4

    #extracting the data from the file
    col_a = list(data['BestPogX'])
    col_b = list(data['BestPogY'])


    #code taken from: https://stackoverflow.com/questions/47915951/heatmap-in-python-to-represent-x-y-coordinates-in-a-given-rectangular-area
    fig, ax = plt.subplots()
    h = ax.hist2d(col_a, col_b, bins=[np.arange(0,2560,precision),np.arange(0,1440,precision)])
    plt.colorbar(h[3], ax=ax)

    #inverting the axis so that the plot displays properly
    plt.gca().invert_yaxis()

    plt.title("Heat Map Demo")
    plt.show()
    plt.close()


'''UI THINGS'''

window = Tk()
frame0 = Frame(window)
frame1 = Frame(window)
frame2 = Frame(window)
frame3 = Frame(window)

frame0.pack()
frame1.pack()
frame2.pack()
frame3.pack()

window.title("Heat Map Visualizer")

text0 = Label(frame0, text='1. Enter input file name. Make sure file has been preProcessed.  \n 2. Enter a precision value (1-10) With 10 being the LEAST precise. ')
text0.pack()

text1 = Label(frame1, text='Input File Name: ')
text1.pack(side=LEFT)
input_file_response = Entry(frame1)
input_file_response.pack(side=LEFT)

text2 = Label(frame2, text='Precision Value: ')
text2.pack(side=LEFT)
precision_response = Entry(frame2)
precision_response.pack(side=LEFT)


button1 = Button(frame3, text='Submit',command=showPlot)
button1.pack(side=RIGHT)


window.mainloop()

