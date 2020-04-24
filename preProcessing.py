import pandas as pd
from tkinter import *
from os import path
import os
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

def preProcess():
    #CHANGE OPTIONS OF THE PROGRAM HERE!!!!!!
    file_name = input_name.get()
    if path.exists(file_name) and os.path.isfile(file_name):
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

        df = pd.read_csv(file_name)

        #all the names of the columns we want to convert proportions to pixels for (X coordinates)
        column_names_X = ['CursorX','LeftEyeX','RightEyeX', 'FixedPogX', 'LeftPogX', 'RightPogX', 'BestPogX', 'LeftPupilX', 'RightPupilX']

        #CHANGE RESOLUTION OF X HERE
        for each in column_names_X:
            df[each] = df[each].multiply(width_of_screen)

        #all the names of the columns we want to convert proportions to pixels for (Y coordinates)
        column_names_Y = ['CursorY','LeftEyeY','RightEyeY', 'FixedPogY', 'LeftPogY', 'RightPogY', 'BestPogY', 'LeftPupilY', 'RightPupilY']

        # CHANGE RESOLUTION OF Y HERE
        for each in column_names_Y:
            df[each] = df[each].multiply(height_of_screen)

        #turn TRUES and FALSES to 1s and 0s
        column_names_bool = ['LeftEyePupilValid', 'RightEyePupilValid', 'FixedPogValid', 'LeftPogValid', 'RightPogValid', 'BestPogValid', 'LeftPupilValid', 'RightPupilValid', 'MarkerValid']

        for each in column_names_bool:
            df[each].replace(True, 1, inplace=True)
            df[each].replace(False, 0, inplace=True)
                #Change pupil diameters to mm from meters

        column_names_Pupil_Diameter = ['LeftEyePupilDiamet', 'RightEyePupilDiame']
        for each in column_names_Pupil_Diameter:
            df[each] = df[each].multiply(1000)

        df.to_csv(output_file_name, index=False)
        text6.configure(text='Status: Success! PreProcessed file created')

    #if its a folder instead of a file
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

        for each in os.listdir(file_name):
            df = pd.read_csv(file_name + '/' + each)
            columns = df.columns
        final_df = pd.DataFrame(columns = columns)

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


            #df.to_csv(output_file_name + str(counter), index=False)
            final_df = final_df.append(df)
            counter += 1

        final_df.to_csv(output_file_name, index=False)

        text6.configure(text='Status: Success! Multiple files processed into one file.')


    else:
        text6.configure(text='Status: File/Folder not Found! Try again.')



# UI things
window = Tk()
frame0 = Frame(window)
frame1 = Frame(window)
frame2 = Frame(window)
frame3 = Frame(window)
frame4 = Frame(window)
frame5 = Frame(window)
frame6 = Frame(window)
frame0.pack()
frame1.pack()
frame2.pack()
frame3.pack()
frame4.pack()
frame5.pack()
frame6.pack()

window.title("Eye Tracking Data")

text0 = Label(frame0, text='1. Leave X and Y resolution BLANK if you want the default values of 2560x1440 \n 2. Include ".csv" in the Input and Output file names \n '
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

button1 = Button(frame5, text='Submit',command=preProcess)
button1.pack(side=RIGHT)

text6 = Label(frame6, text='Status: N/A')
text6.pack()

window.mainloop()