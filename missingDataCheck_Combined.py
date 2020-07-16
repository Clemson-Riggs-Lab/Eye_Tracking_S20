# -*- coding: utf-8 -*-
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
Mohamad El Iskandarani
7/13/20 - added support for FOVIO tracker and refined codes & comments
'''


def missingDataCheck(tracker):
    ''''''
    '''----------SET UP----------------'''

    #setting the background of the plot
    #im = plt.imread('UAVSimPic.png')
    #implot = plt.imshow(im)

    #getting new files from the input the user types in
    file = input_file_response.get()
    newfile = output_file_response.get()

    #checking to see if the file exists and it is a FILE not a folder
    if path.exists(file) and os.path.isfile(file) and newfile != '':
        text3.configure(
            text='Status: Success!')

        df = pd.read_csv(file)
        output_file = open("ErrorLog.txt", "w")
        X_coords = []
        Y_coords = []
        negative_coordinates = []
        missing_packets = []
        marker_bad = []
        final_index = len(df.index)
        final_time = df.iloc[-1]['Time'] 
        print(final_time)
        '''----------Checking errors in the file-----------------'''
        #Function returns the following lists given the dataframe        
        negative_coordinates,missing_packets,marker_bad,X_coords,Y_coords = CheckErrors(df,output_file,tracker)
        '''----------Gathering statistics-----------------'''
        Statistics(negative_coordinates,missing_packets,marker_bad,final_index,final_time,output_file)
        '''----------deleting errors from file-----------------'''
        # combining the lists together for duplicate rows
        combined_list = list(set(negative_coordinates).union(set(marker_bad)))
        DeleteErrors(combined_list,df,newfile)
        '''----------displaying the plot-----------------'''
        ScatterPlot(X_coords,Y_coords,file)
         
    #If path detected is a folder 
    elif os.path.isdir(file):
        '''--------------------------DOING STUFF WITH FOLDERS-----------------------------'''
        text3.configure(
            text='Status: Success!')

        output_file = open("ErrorLog.txt", "w")

        #initializing empty lists
        X_coords = []
        Y_coords = []
        negative_coordinates = []
        missing_packets = []
        marker_bad = []

        #read in each file individually
        for each in os.listdir(file):
            df = pd.read_csv(file + '/' + each)
            columns = df.columns
        final_df = pd.DataFrame(columns = columns)
        final_index = len(final_df.index)
        final_time = final_df.iloc[-1]['Time']   
        
        for each in os.listdir(file):
            df = pd.read_csv(file + '/' + each)
            '''----------Checking errors in the file-----------------''' 
            negative_coordinates,missing_packets,marker_bad,X_coords,Y_coords = CheckErrors(df,output_file)
            final_df = final_df.append(df)           
        '''----------Gathering statistics-----------------'''
        Statistics(negative_coordinates,missing_packets,marker_bad,final_index,final_time,output_file)      
    else:
        text3.configure(
            text='Status: Either the path to the input is wrong, or an output file name was not specified. Please try again.')
def Statistics(negative_coords,missing_data,bad_markers,final_index,final_time,output_file):     
        #writing summary statistics
        output_file.write('\nTotal Negative/Zero/Impossible Coordinates: ' + str(len(negative_coords)) + '\n')
        output_file.write('Total Unordered Data Packets: ' + str(len(missing_data)) + '\n')
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
            '\nProportion of Negative/Zero/Impossible Coordinates: ' + str(proportion_impossible) + ' (' + str(
                percentage_impossible) + '%)' + '\n')
        output_file.write('Proportion of Unordered Data Packets: ' + str(proportion_packets) + ' (' + str(
            percentage_packets) + '%)' + '\n')
        output_file.write(
            'Proportion of Invalid Data based on Gazepoint: ' + str(proportion_gazepoint) + ' (' + str(
                percentage_gazepoint) + '%)' + '\n')

        # Time recorded is in ms, fetch last time recorded in csv file
        total_time_seconds = final_time / 1000
        total_time_minutes = total_time_seconds / 60

        output_file.write('\nTotal Time Elapsed: ' + str(total_time_minutes) + ' minutes (' + str(
            total_time_seconds) + ' seconds)' + '\n')

        # combining the lists together for duplicate rows
        combined_list = list(set(negative_coords).union(set(bad_markers)))

        total_error_time_seconds = len(combined_list) / 150
        total_error_time_minutes = total_error_time_seconds / 60

        output_file.write('Error Time Elapsed: ' + str(total_error_time_minutes) + ' minutes (' + str(total_error_time_seconds) + ' seconds)' + '\n')  
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
                if df['Lft X Pos'][i] <= 0 or df['Lft X Pos'][i] >= 2560 or df['Rt X Pos'][i] <= 0 or df['Rt X Pos'][i] >= 2560 or df['Lft Y Pos'][i] <= 0 or df['Lft Y Pos'][i] >= 1440  or df['Rt Y Pos'][i] <= 0 or df['Rt Y Pos'][i] >= 1440 :
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
                #report when gazepoint has a 0 in the either L Display or R Display columns
                if df['L Display'][i] == 0 or df['R Display'][i] == 0 :
                    output_file.write('Row ' + str(i + 2) + ': Invalid Data based on Gazepoint\n')
                    marker_bad.append(i)
                    valid_point = FALSE 
            if valid_point == TRUE and (i%100==0): #modulo condition to reduce number of points and explore a wider scope (take 1 point every 100 iterations)
                X_coords.append(df['Lft X Pos'][i])
                Y_coords.append(df['Lft Y Pos'][i])
            valid_point = TRUE #reset boolean variable for next iteration
        return negative_coordinates,missing_packets,marker_bad,X_coords,Y_coords
def ScatterPlot(X_coords,Y_coords,file):
        # displaying points on the background ... density inversely related to number
        plt.scatter(X_coords,Y_coords, s=2, c='r')
        plt.title(file)
        plt.show()
        print(v.get())
        print(type(v.get())) 
 
def DeleteErrors(combined_list,df,newfile):
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

text0 = Label(frame0, text='1. Enter input file or folder name. Make sure all files have already been PreProccesed. \n  2. Enter output file name \n 3. A file named ErrorLog.txt will show up where you can view all errors.')
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

text4 = Label(frame5, text='Eye Tracker Type:')
text4.pack(side=LEFT)


one = Button(window, text="Gazepoint", width="10", height="3",command=lambda : missingDataCheck(1))
one.pack(side="top")


two = Button(window, text="FOVIO", width="10", height="3", command=lambda : missingDataCheck(2))
two.pack(side="top")

text3 = Label(frame4, text='Status: N/A')
text3.pack()

window.mainloop()
