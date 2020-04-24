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

        #identify and report bad data (coordinates that are negative or greater than 2560x1440)
        for i in range(0,len(df.index)):

            #negative coordinates
            if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][i] >= 1440:
                output_file.write('Row ' + str(i) + ': Negative/Zero/Impossible Coordinates (Columns AE and AF)\n')
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

        output_file.write('\nTotal Negative/Zero/Impossible Coordinates: ' + str(len(negative_coordinates)) +'\n')
        output_file.write('Total Unordered Data Packets: ' + str(len(missing_packets)) +'\n')
        output_file.write('Total Invalid Data based on Gazepoint: ' + str(len(marker_bad)) +'\n')

        proportion_impossible = len(negative_coordinates) / len(df.index)
        proportion_packets = len(missing_packets) / len(df.index)
        proportion_gazepoint = len(marker_bad) / len(df.index)
        percentage_impossible = len(negative_coordinates) / len(df.index) * 100
        percentage_packets = len(missing_packets) / len(df.index) * 100
        percentage_gazepoint = len(marker_bad) / len(df.index) * 100

        output_file.write('\nProportion of Negative/Zero/Impossible Coordinates: ' + str(proportion_impossible) + ' (' + str(percentage_impossible) + '%)' + '\n')
        output_file.write('Proportion of Unordered Data Packets: '+ str(proportion_packets) + ' (' + str(percentage_packets) + '%)' + '\n')
        output_file.write('Proportion of Invalid Data based on Gazepoint: ' + str(proportion_gazepoint) + ' (' + str(percentage_gazepoint) + '%)' + '\n')

        total_time_seconds = len(df.index) / 150
        total_time_minutes = total_time_seconds / 60

        output_file.write('\nTotal Time Elapsed: ' + str(total_time_minutes) + ' minutes (' + str(total_time_seconds) + ' seconds)' + '\n')

        # combining the lists together for duplicate rows
        combined_list = list(set(negative_coordinates).union(set(marker_bad)))

        total_error_time_seconds = len(combined_list) / 150
        total_error_time_minutes = total_error_time_seconds / 60

        output_file.write('Error Time Elapsed: ' + str(total_error_time_minutes) + ' minutes (' + str(
        total_error_time_seconds) + ' seconds)' + '\n')


        output_file.close()

        '''----------displaying the plot-----------------'''

        # displaying points on the background ... density inversely related to number
        for i in range(0, len(df.index), 100):
            if df['BestPogX'][i] <= 0 or df['BestPogX'][i] >= 2560 or df['BestPogY'][i] <= 0 or df['BestPogY'][i] >= 1440:
                ...
            else:
                # parameters: c='' for color , s=___ for size
                plt.scatter([df['BestPogX'][i]], [df['BestPogY'][i]], s=2, c='r')
        plt.title(file)
        plt.show()


        '''----------deleting errors from file-----------------'''

        df.drop(combined_list, axis=0, inplace=True)

        # after all changes are made
        df.to_csv(newfile, index=False)

    elif os.path.isdir(file):
        '''--------------------------DOING STUFF WITH FOLDERS-----------------------------'''
        text3.configure(
            text='Status: Success!')

        output_file = open("ErrorLog.txt", "w")

        negative_coordinates = []
        missing_packets = []
        marker_bad = []

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
                    output_file.write('Row ' + str(i) + ': Negative/Zero/Impossible Coordinates (Columns AE and AF)\n')
                    negative_coordinates.append(i)

                # ignore the first loop to avoid errors
                if i == 0:
                    ...
                else:
                    # check for missing data ... see how the packet counter is
                    if df['Counter'][i] != df['Counter'][i - 1] + 1:
                        output_file.write('Row ' + str(i + 2) + ': Unordered Data Packet Counters (Column E)\n')
                        missing_packets.append(i + 2)

                if df['BestPogValid'][i] != 1:
                    output_file.write('Row ' + str(i) + ': Invalid Data based on Gazepoint (Column AG)\n')
                    marker_bad.append(i)

            final_df = final_df.append(df)


        output_file.write('\nTotal Negative/Zero/Impossible Coordinates: ' + str(len(negative_coordinates)) + '\n')
        output_file.write('Total Unordered Data Packets: ' + str(len(missing_packets)) + '\n')
        output_file.write('Total Invalid Data based on Gazepoint: ' + str(len(marker_bad)) + '\n')

        proportion_impossible = len(negative_coordinates) / len(final_df.index)
        proportion_packets = len(missing_packets) / len(final_df.index)
        proportion_gazepoint = len(marker_bad) / len(final_df.index)
        percentage_impossible = len(negative_coordinates) / len(final_df.index) * 100
        percentage_packets = len(missing_packets) / len(final_df.index) * 100
        percentage_gazepoint = len(marker_bad) / len(final_df.index) * 100

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