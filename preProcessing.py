import pandas as pd
from tkinter import *
from os import path
'''
Dustin Nguyen
ddn3aq
2/18/2020
Riggs Lab

Update 3/3: New UI interface!

'''

def preProcess():
    #CHANGE OPTIONS OF THE PROGRAM HERE!!!!!!
    file_name = input_name.get()
    if path.exists(file_name):
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

        df.to_csv(output_file_name, index=False)
        text6.configure(text='Status: Success! PreProcessed file created')
    else:
        text6.configure(text='Status: File not Found! Try again.')



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

text0 = Label(frame0, text='1. Leave X and Y resolution BLANK if you want the default values of 2560x1440 \n 2. Include ".csv" in the Input and Output file names')
text0.pack()

text1 = Label(frame1, text='Enter X resolution: ')
text1.pack(side=LEFT)
x_response = Entry(frame1)
x_response.pack(side=LEFT)

text2 = Label(frame2, text='Enter Y resolution: ')
text2.pack(side=LEFT)
y_response = Entry(frame2)
y_response.pack(side=LEFT)

text3 = Label(frame3, text='Enter Input File Name: ')
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