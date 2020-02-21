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

def enterXLSM(event):
    file = nameEntry.get()
    if path.exists(file):
        message = "Successful."

        myscreen = turtle.Screen()
        myscreen.reset()
        myscreen.setworldcoordinates(0, 2000, 2000, 0)
        myturtle = turtle.Turtle()


        if v.get() == 1:
            ...
        else:
            myscreen.tracer(0, 0)

        df = pd.read_excel(file)
        df.columns = [c.replace(' ', '_') for c in df.columns]

        #dropping uneccesary data
        df = df.drop(df[(df.Lft_X_Pos == 0) & (df.Lft_Y_Pos == 0)].index)
        df['Lft_X_Pos'].replace('', np.nan, inplace=True)
        df.dropna(subset=['Lft_X_Pos'], inplace=True)

        if v.get() == 0:
            for i in range(len(df)):
                myturtle.goto(x=df['Lft_X_Pos'].iloc[i], y=df["Lft_Y_Pos"].iloc[i])
                myturtle.dot()
        else:
            for i in range(len(df)):
                myturtle.penup()
                myturtle.goto(x=df['Lft_X_Pos'].iloc[i], y=df["Lft_Y_Pos"].iloc[i])
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
enter_button.bind("<Button-1>", enterXLSM)

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