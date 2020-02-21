import tkinter as tk
from os import path
import turtle
import pandas as pd
import numpy as np

'''
Dustin Nguyen
ddn3aq
2/4/2020
Riggs Lab
'''

def enterCSV(event):
    file = nameEntry.get()

    if True:
    #if path.exists(file):
        message = "Successful."

        #file = 'P1_Fam_D20200206T1130Output_EyeTracker1.csv'
        file = 'test2.csv'

        myscreen = turtle.Screen()
        myscreen.reset()
        #myscreen.setworldcoordinates(2560, 0, 0, 1440)
        myscreen.screensize(2560, 1440)
        myturtle = turtle.Turtle()


        if v.get() == 1:
            ...
        else:
            myscreen.tracer(0, 0)

        df = pd.read_csv(file)
        #df['Lft_X_Pos'].replace('', np.nan, inplace=True)
        df.dropna(subset=['BestPogX'], inplace=True)

        if v.get() == 0:
            for i in range(len(df)):
                myturtle.goto(x=df['BestPogX'].iloc[i], y=df["BestPogY"].iloc[i])
                myturtle.dot()
        else:
            for i in range(len(df)):
                myturtle.penup()
                myturtle.goto(x=df['BestPogX'].iloc[i], y=df["BestPogY"].iloc[i])
                myturtle.dot()
        turtle.done()

    else:
        message = "file doesnt exist! try again"


    #UPDATE UI
    update_text.configure(state='normal')
    update_text.delete("1.0", tk.END)
    update_text.insert(tk.END, message)
    update_text.configure(state='disabled')


#window UI stuff---------------------------------------
window = tk.Tk()
window.title("Eye Tracking Data")
window.geometry("500x400")

label_title = tk.Label(text = "Enter name of CSV file here: (make sure its in the same folder as this program!", font=("Times new roman",10))
label_title.grid(column=0,row=0)

nameEntry = tk.Entry()
nameEntry.grid(column=0, row=1)

enter_button = tk.Button(window, text = "Submit")
enter_button.grid(column=1, row=1)
enter_button.bind("<Button-1>", enterCSV)

update_text = tk.Text(master=window,height=2, width=30,background="gray", state='disabled')
update_text.grid(column=0)

#just making the radio button UI display ... change this when we have saccade and fixation functionality
v = tk.IntVar()
v.set(1)
choices = [
    "Include Lines",
    "Include Animation",
    "Show Fixtures (coming soon)",
    "Show saccades (coming soon)"
]
radioLabel = tk.Label(window,
         text="""Choose what you want to include:""")
radioLabel.grid(column=0,row=3)

count = 4
for val, language in enumerate(choices):
    tk.Radiobutton(window,
                  text=language,
                  padx = 20,
                  variable=v,
                  value=val).grid(column=0,row=count)
    count+=1

window.mainloop()