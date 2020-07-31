import pandas as pd
from tkinter import *
from os import path
import os
import numpy as np
import math
'''
Dustin Nguyen and Sam Smith
ddn3aq sjs5pg 
2/18/2020
Riggs Lab

Update 3/3: New UI interface!
Update 4/2: Multiple files allowed!

Update to-do : get multiple files into one output file
4/5: all go into one file now

'''

"""
This function is called by the GUI when user presses the submit button.
It contains all of the logic for the file. 
"""


def preProcess(tracker_type):
    # CHANGE OPTIONS OF THE PROGRAM HERE!!!!!!

    file_name = input_name.get()
    if path.exists(file_name) and os.path.isfile(file_name):
        if output_name.get() == '':
            text6.configure(text='Status: Output file name not specified!')
            return
        output_file_name = output_name.get()

        # Default width is 2560 and default height is 1440
        if x_response.get() == '':
            width_of_screen = 2560
        else:
            width_of_screen = x_response.get()

        if y_response.get() == '':
            height_of_screen = 1440
        else:
            height_of_screen = y_response.get()

        df = pd.read_csv(file_name)
        column_names_X = []
        column_names_Y = []
        column_names_bool = []
        column_names_Pupil_Diameter = []
        if tracker_type == 1:
            # Tracker used is that of experiment 1
            # all the names of the columns we want to convert proportions to pixels for
            column_names_X = ['CursorX', 'LeftEyeX', 'RightEyeX', 'FixedPogX', 'LeftPogX', 'RightPogX', 'BestPogX',
                              'LeftPupilX', 'RightPupilX']
            column_names_Y = ['CursorY', 'LeftEyeY', 'RightEyeY', 'FixedPogY', 'LeftPogY', 'RightPogY', 'BestPogY',
                              'LeftPupilY', 'RightPupilY']
            column_names_bool = ['LeftEyePupilValid', 'RightEyePupilValid', 'FixedPogValid', 'LeftPogValid',
                                 'RightPogValid', 'BestPogValid', 'LeftPupilValid', 'RightPupilValid', 'MarkerValid']
            column_names_Pupil_Diameter = ['LeftEyePupilDiamet', 'RightEyePupilDiame']

            # turn TRUES and FALSES to 1s and 0s
            for each in column_names_bool:
                df[each].replace(True, 1, inplace=True)
                df[each].replace(False, 0, inplace=True)
        elif tracker_type == 2:
            #Tracker used is that of experiment 2 (60 Hz)
            column_names_X = ['Lft X Pos', 'Rt X Pos', 'L Eye Rot (X)', 'R Eye Rot (X)','L Eye Pos (X)','R Eye Pos (X)',
                              'Head Rot (X)','Head Pos (X)']
            column_names_Y = ['Lft Y Pos', 'Rt Y Pos', 'L Eye Rot (Y)', 'R Eye Rot (Y)','L Eye Pos (Y)','R Eye Pos (Y)',
                              'Head Rot (Y)','Head Pos (Y)']
            column_names_Pupil_Diameter = ['Lft Pupil Diameter', 'Rt Pupil Diameter']

        # CHANGE RESOLUTION OF X HERE
        for each in column_names_X:
            df[each] = df[each].multiply(width_of_screen)

        # CHANGE RESOLUTION OF Y HERE
        for each in column_names_Y:
            df[each] = df[each].multiply(height_of_screen)

        # Change pupil diameters to mm from meters
        for each in column_names_Pupil_Diameter:
            df[each] = df[each].multiply(1000)
 

################################################################
# In this section we calculate the visual angles, angular velocities, and append the to the dataframe
        Delta = [] #in pixels
        Angular_Velocity = []
        Delta_mm = []
        Delta_rad = [] 
        if tracker_type==1: #If Gazepoint Tracker
            for i in range(0,len(df.index)):
                if i==len(df.index)-1: #in this case we reach the end of the dataframe and dont have an i+1
                    x1 = df['BestPogX'][i-1]
                    y1 = df['BestPogY'][i-1]  
                    time_diff =abs(df['Time'][i-1])
                    
                else:
                    
                    x1 = df['BestPogX'][i+1]-df['BestPogX'][i]
                    y1 = df['BestPogY'][i+1]-df['BestPogY'][i]
                    time_diff=abs(df['Time'][i+1]-df['Time'][i])  
                    
                Delta.append(math.sqrt(pow(x1,2)+pow(y1,2)))
                Delta_mm.append(Delta[i]*0.207565625)
                Delta_rad.append(math.atan(Delta_mm[i]/(23.62204724*25.4)))
                velocity = Delta_rad[i]*57.29577951/time_diff #convert to degrees and divide by time difference
                Angular_Velocity.append(velocity)
                
        elif tracker_type ==2: #If FOVIO Tracker
            for i in range(0,len(df.index)):
                if i==len(df.index)-1: #in this case we reach the end of the dataframe and dont have an i+1
                    x1 = df['Lft X Pos'][i-1]
                    y1 = df['Lft Y Pos'][i-1]  
                    time_diff =abs(df['Time'][i-1])
                    
                else:
                    
                    x1 = df['Lft X Pos'][i+1]-df['Lft X Pos'][i]
                    y1 = df['Lft Y Pos'][i+1]-df['Lft Y Pos'][i]
                    time_diff=abs(df['Time'][i+1]-df['Time'][i])
                
                Delta.append(math.sqrt(pow(x1,2)+pow(y1,2)))
                Delta_mm.append(Delta[i]*0.269279688)
                Delta_rad.append(math.atan(Delta_mm[i]/(29.5*25.4)))
                velocity = Delta_rad[i]*57.29577951*1000/time_diff #convert to degrees and divide by time difference
                Angular_Velocity.append(velocity)

            
        df['Delta (in pixels)'] = Delta #Create a new column and append the visual angle values in pixels
        df['Delta (in mm)'] = Delta_mm #Create a new column and append the visual angle values in mm
        df['Delta (in rad)'] = Delta_rad #Create a new column and append the visual angle values in rad
        df['Angular Velocity (in degrees/second)'] = Angular_Velocity #Create a new column and append the angular velocity in degrees per second
################################################################
        
        df.to_csv(output_file_name, index=False)
        text6.configure(text='Status: Success! PreProcessed file created')
    # if its a folder instead of a file
    elif os.path.isdir(file_name):

        if output_name.get() == '':
            text6.configure(text='Status: Output file name not specified!')
            return

        output_file_name = output_name.get()

        if x_response.get() == '':
            width_of_screen = 2560
        else:
            width_of_screen = x_response.get()

        if y_response.get() == '':
            height_of_screen = 1440
        else:
            height_of_screen = y_response.get()

        counter = 1
        # Essentially, we iterate through the files in the specified folder and process each one.
        for each in os.listdir(file_name):
            df = pd.read_csv(file_name + '/' + each)
            columns = df.columns
        final_df = pd.DataFrame(columns=columns)

        for each in os.listdir(file_name):

            df = pd.read_csv(file_name + '/' + each)

            # all the names of the columns we want to convert proportions to pixels for (X coordinates)
            column_names_X = ['CursorX', 'LeftEyeX', 'RightEyeX', 'FixedPogX', 'LeftPogX', 'RightPogX', 'BestPogX',
                              'LeftPupilX', 'RightPupilX']

            # CHANGE RESOLUTION OF X HERE
            for each in column_names_X:
                df[each] = df[each].multiply(width_of_screen)

            # all the names of the columns we want to convert proportions to pixels for (Y coordinates)
            column_names_Y = ['CursorY', 'LeftEyeY', 'RightEyeY', 'FixedPogY', 'LeftPogY', 'RightPogY', 'BestPogY',
                              'LeftPupilY', 'RightPupilY']

            # CHANGE RESOLUTION OF Y HERE
            for each in column_names_Y:
                df[each] = df[each].multiply(height_of_screen)

            # turn TRUES and FALSES to 1s and 0s
            column_names_bool = ['LeftEyePupilValid', 'RightEyePupilValid', 'FixedPogValid', 'LeftPogValid',
                                 'RightPogValid', 'BestPogValid', 'LeftPupilValid', 'RightPupilValid', 'MarkerValid']

            for each in column_names_bool:
                df[each].replace(True, 1, inplace=True)
                df[each].replace(False, 0, inplace=True)
            # Change pupil diameters to mm from meters

            column_names_Pupil_Diameter = ['LeftEyePupilDiamet', 'RightEyePupilDiame']
            for each in column_names_Pupil_Diameter:
                df[each] = df[each].multiply(1000)

            # Change pupil diameters from pixels to mm by multiplying with column AT
            column_names_Pupil_to_mm = ['LeftPupilDiameter', 'RightPupilDiameter']
            for each in column_names_Pupil_to_mm:
                df[each] = df[each].multiply(df['MarkerScale'])

            y_pupil_data = ['RightPupilY', 'LeftPupilY']
            for each in y_pupil_data:
                df[each] = df[each].multiply(height_of_screen)
                df[each] = df[each].multiply(df['MarkerScale'])

            x_pupil_data = ['RightPupilX', 'LeftPupilX']
            for each in x_pupil_data:
                df[each] = df[each].multiply(width_of_screen)
                df[each] = df[each].multiply(df['MarkerScale'])

            # Logic for naming the multiple output files
            index_counter = 0
            for char in output_file_name:
                if char == ".":
                    break
                else:
                    index_counter += 1
            # Each dataframe is appended to a master dataframe, which contains all of the preprocessed data for the folder.
            # We also create individual output files for each raw file.
            final_df = final_df.append(df)
            # The below statement allows us to create an output file for each file in the given folder.
            df.to_csv(output_file_name[:index_counter] + str(counter) + ".csv", index=False)

            counter += 1
        # Add option in GUI to process folder into one master file or one file
        # for each eyetracking file. Save this response as a boolean
        """
        something like if boolean, final_df.to_csv else make individual preprocessed file
        """
        final_df.to_csv(output_file_name, index=False)

        text6.configure(text='Status: Success! Multiple files processed into one file as well as individual files.')


    else:
        text6.configure(text='Status: File/Folder not Found! Try again.')


# UI things
"""
Below is the logic for the simple GUI that we created for this program. It uses 
a python package called tkinter. 
"""
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

window.title("Eye Tracking Data")

text0 = Label(frame0,
              text='1. Leave X and Y resolution BLANK if you want the default values of 2560x1440 \n 2. Include ".csv" in the Input and Output file names \n '
                   '3. If you want to process multiple files, place all the files into a single folder and put the path of the folder in the "Input" box below')
text0.pack()

text1 = Label(frame1, text='Enter X resolution: ')
text1.pack(side=LEFT)
x_response = Entry(frame1)
x_response.pack(side=LEFT)

text2 = Label(frame2, text='Enter Y resolution: ')
text2.pack(side=LEFT)
y_response = Entry(frame2)
y_response.pack(side=LEFT)

text3 = Label(frame3, text='Enter Input File/Folder Name: ')
text3.pack(side=LEFT)
input_name = Entry(frame3)
input_name.pack(side=LEFT)

text4 = Label(frame4, text='Enter Output File Name: ')
text4.pack(side=LEFT)
output_name = Entry(frame4)
output_name.pack(side=LEFT)


text5 = Label(frame5, text='Eye Tracker Type:')

one = Button(window, text="Gazepoint", width="10", height="3",command=lambda : preProcess(1))
one.pack(side="top")

two = Button(window, text="FOVIO", width="10", height="3", command=lambda : preProcess(2))
two.pack(side="top")

text6 = Label(frame7, text='Status: N/A')
text6.pack()

window.mainloop()
