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

"""
This function is called by the GUI when user presses the submit button.
It contains all of the logic for the file. 
"""
def preProcess():

    """
    The following series of if statements checks that the provided raw 
    eyetracking file exists, and grabs the file name so that we can process the 
    file. Essentially, it looks at certain columns whose units need to be converted
    at some capacity (for example, the raw eye positions were represented in terms of
    a proportion to the screen, which we then had to multiply by the width and height of
    the screen in terms of pixels). We are using the pandas library with python, which 
    allows us to easily access and manipulate the columns of a csv. The pandas documentation 
    can be found here: https://pandas.pydata.org/docs/reference/index.html
    """
    #CHANGE OPTIONS OF THE PROGRAM HERE!!!!!!

    file_name = input_name.get()
    if path.exists(file_name) and os.path.isfile(file_name):
        if output_name.get() == '':
            text6.configure(text='Status: Output file name not specified!')
            return
        output_file_name = output_name.get()

        #Default width is 2560 and default height is 1440 
        if x_response.get() == '':
            width_of_screen = 2560
        else:
            width_of_screen = x_response.get()

        if y_response.get() == '':
            height_of_screen = 1440
        else:
            height_of_screen = y_response.get()

        #read_csv is an important function. It allows us to utilize the data in the csv with pandas using a dataframe. 
        """
        Essentially, we are reading the csv into something called a dataframe, which contains the
        data from the raw eyetracking file. In the series of for loops below, we change the data in certain
        columns based on our specifications (that are stored within the dataframe, so we are not changing the input file)
        and convert the dataframe into the output csv file at the end of this program. 
        """
        df = pd.read_csv(file_name)

        #all the names of the columns we want to convert proportions to pixels for (X coordinates)
        column_names_X = ['CursorX','LeftEyeX','RightEyeX', 'FixedPogX', 'LeftPogX', 'RightPogX', 'BestPogX', 'LeftPupilX', 'RightPupilX']

        #CHANGE RESOLUTION OF X HERE
        for each in column_names_X:
            df[each] = df[each].multiply(width_of_screen)

        #all the names of the columns we want to convert proportions to pixels for (Y coordinates)
        """
        Something incredibly useful about pandas is that you can just use the names of the columns to refer to 
        them rather than using numerical indices. The expression 'df[column_name]' would yield the entire column of 
        data stored within the specified column name. Overall pandas is a very useful tool and I would recommend 
        learning the basics of how it works using the documentation.
        """
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
        #Essentially, we iterate through the files in the specified folder and process each one. 
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
            """
            Inplace=True means change the dataframe that is being referenced. If inplace=False,
            a copy of the dataframe with the requested change will be made. 
            """
            for each in column_names_bool:
                df[each].replace(True, 1, inplace=True)
                df[each].replace(False, 0, inplace=True)
            # Change pupil diameters to mm from meters

            column_names_Pupil_Diameter = ['LeftEyePupilDiamet', 'RightEyePupilDiame']
            for each in column_names_Pupil_Diameter:
                df[each] = df[each].multiply(1000)

            # Change pupil diameters from pixels to mm by multiplying with column AT
            """
            The following code shows how to multiply one column by another using pandas. 
            Note that because we are using for loops, we often use 'each' to describe
            each column. However, if you did something like df['RightPupilY'], that would 
            return the specified column as well. The column 'MarkerScale,' when multiplied by 
            by the pupil data, gave us the conversions we needed.
            """
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
            
            #Logic for naming the multiple output files
            index_counter=0
            for char in output_file_name:
                if char==".":
                    break
                else:
                    index_counter+=1
            #Each dataframe is appended to a master dataframe, which contains all of the preprocessed data for the folder.
            #We also create individual output files for each raw file. 
            final_df = final_df.append(df)
            #The below statement allows us to create an output file for each file in the given folder.
            df.to_csv(output_file_name[:index_counter] + str(counter)+".csv", index=False)

            counter += 1
        #Add option in GUI to process folder into one master file or one file
        #for each eyetracking file. Save this response as a boolean
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