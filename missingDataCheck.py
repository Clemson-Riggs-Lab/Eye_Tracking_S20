import matplotlib.pyplot as plt
import pandas as pd
from tkinter import *
from os import path
import os


def command():
    ''''''
    '''----------SET UP----------------'''

    im = plt.imread('UAVSimPic.png')
    implot = plt.imshow(im)

    file = input_file_response.get()
    newfile = output_file_response.get()

    if path.exists(file) and os.path.isfile(file) and newfile != '':
        text3.configure(
            text='Status: Success!')

        df = pd.read_csv(file)
        output_file = open("ErrorLog.txt", "w")

        negative_coordinates = []
        missing_packets = []
        marker_bad = []

        '''----------Checking errors in the file-----------------'''

        #identify and report bad data (coordinates that are negative or greater than 2560x14440)
        for i in range(0,len(df.index)):

            #negative coordinates
            if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][i] >= 1440:
                output_file.write('Row ' + str(i) + ': Negative/Zero Coordinates (Columns AE and AF)\n')
                negative_coordinates.append(i)

            #ignore the first loop to avoid errors
            if i == 0:
                ...
            else:
                #check for missing data ... see how the packet counter is
                if df['Counter'][i] != df['Counter'][i-1] + 1:
                    output_file.write('Row ' + str(i + 2) + ': Unordered Data Packet Counters (Column E)\n')
                    missing_packets.append(i+2)

            if df['BestPogValid'][i] != 1:
                output_file.write('Row ' + str(i) + ': Invalid Data based on Gazepoint (Column AG)\n')
                marker_bad.append(i)

        output_file.write('\nTotal Negative/Zero Coordinates: ' + str(len(negative_coordinates)) +'\n')
        output_file.write('Total Unordered Data Packets: ' + str(len(missing_packets)) +'\n')
        output_file.write('Total Invalid Data based on Gazepoint: ' + str(len(marker_bad)) +'\n')

        output_file.close()

        '''----------displaying the plot-----------------'''

        # displaying points on the background ... density inversely related to number
        for i in range(0, len(df.index), 100):
            if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][i] >= 1440:
                ...
            else:
                # parameters: c='' for color , s=___ for size
                plt.scatter([df['BestPogX'][i]], [df['BestPogY'][i]], s=2, c='r')

        plt.show()


        '''----------deleting errors from file-----------------'''

        # combining the lists together for duplicate rows
        combined_list = list(set(negative_coordinates).union(set(marker_bad)))

        df.drop(combined_list, axis=0, inplace=True)

        # after all changes are made
        df.to_csv(newfile, index=False)

    else:
        text3.configure(
            text='Status: Either the path to the input is wrong, or an output file name was not specified. Please try again.')


'''----------UI things-----------------'''
window = Tk()
frame0 = Frame(window)
frame1 = Frame(window)
frame2 = Frame(window)
frame3 = Frame(window)
frame4 = Frame(window)
frame0.pack()
frame1.pack()
frame2.pack()
frame3.pack()
frame4.pack()
window.title("Missing/Bad Data checker")

text0 = Label(frame0, text='1. Enter input file or folder name. Make sure all files have already been PreProccesed.          2. Enter output file name \n 3. A file named ErrorLog.txt will show up where you can view all errors.')
text0.pack()

text1 = Label(frame1, text='Input File/Folder: ')
text1.pack(side=LEFT)
input_file_response = Entry(frame1)
input_file_response.pack(side=LEFT)

text2 = Label(frame2, text='Output File Name: ')
text2.pack(side=LEFT)
output_file_response = Entry(frame2)
output_file_response.pack(side=LEFT)

button1 = Button(frame3, text='Submit',command=command)
button1.pack(side=RIGHT)

text3 = Label(frame4, text='Status: N/A')
text3.pack()

window.mainloop()