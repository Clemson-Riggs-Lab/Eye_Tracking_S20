import matplotlib.pyplot as plt
import pandas as pd
from tkinter import *
from os import path
import os
import more_itertools as mit

'''
Dustin Nguyen
ddn3aq
5/19/20

5/19 update - added comments

'''


def command():
    ''''''
    '''----------SET UP----------------'''

    #setting the background of the plot
    im = plt.imread('UAVSimPic.png')
    implot = plt.imshow(im)

    #getting new files from the input the user types in
    file = input_file_response.get()
    newfile = output_file_response.get()

    #checking to see if the file exists and it is a FILE not a folder
    if path.exists(file) and os.path.isfile(file) and newfile != '':
        text3.configure(
            text='Status: Success!')

        df = pd.read_csv(file)
        output_file = open("ErrorLog.txt", "w")

        negative_coordinates = []
        missing_packets = []
        marker_bad = []

        '''----------Checking errors in the file-----------------'''

        #identify and report bad data (coordinates that are negative or greater than 2560x1440)
        for i in range(0,len(df.index)):

            #negative coordinates
            """
            This statement checks for negative eyetracking coordinates, because this would mean that 
            the data was collected incorrectly (participants were looking at a 2560x1440 pixel screen).
            If negative points are found, the coordinates are appended to a list which is later displayed in 
            an output text file called errorlog.txt
            """
            #Go back later and look at the logic
            if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][i] >= 1440:
                output_file.write('Row ' + str(i + 2) + ': Negative/Zero/Impossible Coordinates (Columns AE and AF)\n')
                negative_coordinates.append(i)

            #ignore the first loop to avoid errors
            if i == 0:
                ...
            else:
                #check for missing data ... see how the packet counter is
                if df['Counter'][i] != df['Counter'][i-1] + 1:
                    output_file.write('Row ' + str(i + 2) + ': Unordered Data Packet Counters (Column E)\n')
                    missing_packets.append(i)

            #report when gazepoint has a 0 in the BESTPOGVALID column
            if df['BestPogValid'][i] != 1:
                output_file.write('Row ' + str(i + 2) + ': Invalid Data based on Gazepoint (Column AG)\n')
                marker_bad.append(i)

        #3 lines that write to ErrorLog.txt the summary statistics
        output_file.write('\nTotal Negative/Zero/Impossible Coordinates: ' + str(len(negative_coordinates)) +'\n')
        output_file.write('Total Unordered Data Packets: ' + str(len(missing_packets)) +'\n')
        output_file.write('Total Invalid Data based on Gazepoint: ' + str(len(marker_bad)) +'\n')

        #doing simple calculaations to report more summary statistics
        proportion_impossible = len(negative_coordinates) / len(df.index)
        proportion_packets = len(missing_packets) / len(df.index)
        proportion_gazepoint = len(marker_bad) / len(df.index)
        percentage_impossible = len(negative_coordinates) / len(df.index) * 100
        percentage_packets = len(missing_packets) / len(df.index) * 100
        percentage_gazepoint = len(marker_bad) / len(df.index) * 100

        #writing these statistics to the file
        output_file.write('\nProportion of Negative/Zero/Impossible Coordinates: ' + str(proportion_impossible) + ' (' + str(percentage_impossible) + '%)' + '\n')
        output_file.write('Proportion of Unordered Data Packets: '+ str(proportion_packets) + ' (' + str(percentage_packets) + '%)' + '\n')
        output_file.write('Proportion of Invalid Data based on Gazepoint: ' + str(proportion_gazepoint) + ' (' + str(percentage_gazepoint) + '%)' + '\n')


        total_time_seconds = len(df.index) / 150
        total_time_minutes = total_time_seconds / 60

        output_file.write('\nTotal Time Elapsed: ' + str(total_time_minutes) + ' minutes (' + str(total_time_seconds) + ' seconds)' + '\n')

        # combining the lists together for duplicate rows
        combined_list = list(set(negative_coordinates).union(set(marker_bad)))

        #sorting the list so row numbers show in order
        sorted_combined_list = sorted(combined_list)

        #putting consequetive rows into individual lists. sub_lists is a list of lists.
        sub_lists = [list(group) for group in mit.consecutive_groups(sorted_combined_list)]

        #if a sublist is > 150 in length, report that there is an unusual amount of error rows at that location
        for each in sub_lists:
            if len(each) >= 150:
                output_file.write('There is an unusual amount of missing data from row ' + str(each[0] + 2) + ' to row ' + str(each[len(each) - 1] + 2))

        #more summary statistics
        total_error_time_seconds = len(combined_list) / 150
        total_error_time_minutes = total_error_time_seconds / 60

        output_file.write('Error Time Elapsed: ' + str(total_error_time_minutes) + ' minutes (' + str(
        total_error_time_seconds) + ' seconds)' + '\n')


        output_file.close()

        '''----------deleting errors from file-----------------'''

        if v.get() == 1:
            df.drop(combined_list, axis=0, inplace=True)

            # after all changes are made
            df.to_csv(newfile, index=False)
        elif v.get() == 2:
            #do the stuff with marking the excel file here'

            defaultvals = ['0'] * len(df.index)

            for each in combined_list:
                defaultvals[each] = 'ERROR'

            for each in missing_packets:
                defaultvals[each] = 'Packet ERROR'

            series = pd.Series(defaultvals)
            df['MissingDataCheck'] = series

            # after all changes are made
            df.to_csv(newfile, index=False)

        '''----------displaying the plot-----------------'''

        # displaying points on the background ... density inversely related to number
        #Third parameter means the plot is displaying every 100 points
        for i in range(0, len(df.index), 100):
            if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][i] >= 1440:
                ...
            else:
                # parameters: c='' for color , s=___ for size
                plt.scatter([df['BestPogX'][i]], [df['BestPogY'][i]], s=2, c='r')
        plt.title(file)
        plt.show()

        print(v.get())
        print(type(v.get()))


    #only go here if it is detected that it is a folder instead
    elif os.path.isdir(file):
        '''--------------------------DOING STUFF WITH FOLDERS-----------------------------'''
        text3.configure(
            text='Status: Success!')

        output_file = open("ErrorLog.txt", "w")

        #initializing empty lists
        negative_coordinates = []
        missing_packets = []
        marker_bad = []

        #read in each file individually
        for each in os.listdir(file):
            df = pd.read_csv(file + '/' + each)
            columns = df.columns
        final_df = pd.DataFrame(columns = columns)

        for each in os.listdir(file):

            df = pd.read_csv(file + '/' + each)

            '''----------Checking errors in the file-----------------'''

            # identify and report bad data (coordinates that are negative or greater than 2560x1440)
            for i in range(0, len(df.index)):

                # negative coordinates
                if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][
                    i] >= 1440:
                    output_file.write('Row ' + str(i + 2) + ': Negative/Zero/Impossible Coordinates (Columns AE and AF)\n')
                    negative_coordinates.append(i)

                # ignore the first loop to avoid errors
                if i == 0:
                    ...
                else:
                    # check for missing data ... see how the packet counter is
                    if df['Counter'][i] != df['Counter'][i - 1] + 1:
                        output_file.write('Row ' + str(i + 2) + ': Unordered Data Packet Counters (Column E)\n')
                        missing_packets.append(i)

                if df['BestPogValid'][i] != 1:
                    output_file.write('Row ' + str(i + 2) + ': Invalid Data based on Gazepoint (Column AG)\n')
                    marker_bad.append(i)

            final_df = final_df.append(df)

        #writing summary statistics
        output_file.write('\nTotal Negative/Zero/Impossible Coordinates: ' + str(len(negative_coordinates)) + '\n')
        output_file.write('Total Unordered Data Packets: ' + str(len(missing_packets)) + '\n')
        output_file.write('Total Invalid Data based on Gazepoint: ' + str(len(marker_bad)) + '\n')

        #calculating more summary statistics
        proportion_impossible = len(negative_coordinates) / len(final_df.index)
        proportion_packets = len(missing_packets) / len(final_df.index)
        proportion_gazepoint = len(marker_bad) / len(final_df.index)
        percentage_impossible = len(negative_coordinates) / len(final_df.index) * 100
        percentage_packets = len(missing_packets) / len(final_df.index) * 100
        percentage_gazepoint = len(marker_bad) / len(final_df.index) * 100

        #write these additional statistics to the output file
        output_file.write(
            '\nProportion of Negative/Zero/Impossible Coordinates: ' + str(proportion_impossible) + ' (' + str(
                percentage_impossible) + '%)' + '\n')
        output_file.write('Proportion of Unordered Data Packets: ' + str(proportion_packets) + ' (' + str(
            percentage_packets) + '%)' + '\n')
        output_file.write(
            'Proportion of Invalid Data based on Gazepoint: ' + str(proportion_gazepoint) + ' (' + str(
                percentage_gazepoint) + '%)' + '\n')

        total_time_seconds = len(final_df.index) / 150
        total_time_minutes = total_time_seconds / 60

        output_file.write('\nTotal Time Elapsed: ' + str(total_time_minutes) + ' minutes (' + str(
            total_time_seconds) + ' seconds)' + '\n')

        # combining the lists together for duplicate rows
        combined_list = list(set(negative_coordinates).union(set(marker_bad)))

        total_error_time_seconds = len(combined_list) / 150
        total_error_time_minutes = total_error_time_seconds / 60

        output_file.write('Error Time Elapsed: ' + str(total_error_time_minutes) + ' minutes (' + str(total_error_time_seconds) + ' seconds)' + '\n')

    else:
        text3.configure(
            text='Status: Either the path to the input is wrong, or an output file name was not specified. Please try again.')


'''----------UI things-----------------'''
window = Tk()
frame0 = Frame(window)
frame1 = Frame(window)
frame2 = Frame(window)
frame5 = Frame(window)
frame3 = Frame(window)
frame4 = Frame(window)
frame0.pack()
frame1.pack()
frame2.pack()
frame5.pack()
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

v = IntVar()

button2 = Radiobutton(frame5,
              text="Delete Rows Automatically",
              padx = 20,
              variable=v,
              value=1).pack()
button3 = Radiobutton(frame5,
              text="Mark in Excel File for review",
              padx = 20,
              variable=v,
              value=2).pack()

button1 = Button(frame3, text='Submit',command=command)
button1.pack(side=RIGHT)

text3 = Label(frame4, text='Status: N/A')
text3.pack()


window.mainloop()