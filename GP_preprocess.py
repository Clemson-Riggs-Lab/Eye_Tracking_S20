import pandas as pd
import statistics
from tkinter import *
from os import path
import os
import numpy as np
import math
import DataQuality
from DataQuality import UAVs
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

#Could potentially clean this up by creating an object 

def dq():
            if input_name.get() == '' or not os.path.isfile(input_name.get()):
                raw = pd.read_csv("2ndTask_ET.csv")
            else:
                raw = pd.read_csv(input_name.get())
            
            if inputP_name.get() == '' or not os.path.isfile(inputP_name.get()):
                performance = pd.read_csv("2ndTask_P.csv")
            else:
                performance = pd.read_csv(inputP_name.get())

            # if output_name.get() == '' or not os.path.isfile(output_name.get()):
            #     output_file_name = "output1.csv"
            # else:
            #     output_file_name = output_name.get()
            output_file_name = output_name.get()
            #Gathering user input for error calculating the valid field of view for participants eyes.
            """
            Essentially, the error that the user inputs is used to extend the bounds that we would
            consider to be acceptably accurate. For example, if a video feed's x coordinates were 
            200 to 1000, an xError of 50 would mean that any eye data in the x direction
            within the window of 150 to 1050 pixels would considered as accurate. This applies
            to the y direction as well.  
            """

            """Currently commenting this out. Need to add x and yerrors to this
            GUI eventually. """
            # try: 
            #     int(xError.get())
            #     input_xError = int(xError.get())
            # except:
            #     input_xError = 0

            # try: 
            #     int(yError.get())
            #     input_yError = int(yError.get())
            # except:
            #     input_yError = 0
            
            input_yError = 0
            input_xError = 0

            totalRows=0
            for each in raw["BestPogX"]:
                totalRows+=1

            raw["NewSystemTime"] = ""
            raw.at[0, "NewSystemTime"]= raw.at[0, "SystemTime"]+ ".0"
            DataQuality.setSystemTime(raw, totalRows)
            #Calling the setMissionTime function below 
            time = DataQuality.findFirstTime(performance)
            start = (DataQuality.findFirstInstance(time, raw))
            print("starting mission time at: "+ str(start)) 
            #You can change output file with third parameter here 
            raw["MissionTime"] = 0.0

            DataQuality.setMissionTime(raw, start, output_file_name, totalRows)
            raw.to_csv(output_file_name, index=False)
            """
            Create dictionary of the mission times (from the button clicks), assign 
            coordinates as values to the mission times key 
            """
            missionDict = {}
            #Tells us if target detection was accurate
            raw["DataAccurate"] = ""
            #Tells which uav the target appeared in
            raw["Task"] = ""
            #Tells us which uav the participant was looking at
            raw["Qualitative"] = "N/A"

            """
            Uses distance formula to calculate how far eye coordinates are 
            from the center of a video feed or secondary task.
            """
            raw["DistanceFromCenter"] = 0



            """
            When there is a target present, this loop looks at the mission time, finds a matching time in the 
            eye tracking file's mission time file (or a time that is very close to the same) and checks that the 
            participants eyes are looking in the correct area. This logic is repeated for the secondary tasks below. 
            """
            number_true = 0
            number_false = 0
            number_analyzed=0
            count=0
            for each in performance["TDTargetPresent"]:
                if each == 1.0:
                    raw_counter=0
                    clickTime = performance.iloc[count, 27]
                    for mt in raw["MissionTime"]:
                        #Finding where button click time and MissionTime align
                        if -.01 <= mt -  clickTime <= .01 :
                            #print(raw.at[raw_counter, "BestPogY"])
                            number_analyzed+=1
                            uavNum = int(performance.at[count, "UAVNumber"])
                            uav = UAVs[uavNum-1]
                            x = raw.at[raw_counter, "BestPogX"]
                            y = raw.at[raw_counter, "BestPogY"]

                            #Now accuracy takes the errors into account 
                            xacc= (x >= uav[0] - input_xError and x <= uav[1] + input_xError)
                            yacc = (y >= uav[2] - input_yError and y <= uav[3] + input_yError)
                            """
                            Value will be True if both x and y coordinates are accurate 
                            according to the current UAV and False if not. 
                            """

                            """
                            Below if statement ensures that only a time that is close
                            to clickTime will be used for the dictionary so we can pinpoint 
                            accuracy at exact clicktime.
                            """
                            if xacc and yacc:
                                number_true +=1
                            else:
                                number_false+=1
                            if -.01 < mt -  clickTime < .01:
                                missionDict[clickTime] = xacc and yacc
                            
                            cur_uav = DataQuality.which_uav(x, y)

                            #Calculating how far away the coordinates are from either 
                            #the upper or lower bound of the uav feed

                            centerx = (uav[0] + uav[1])/2
                            centery = (uav[2] + uav[3])/2


                            #Updating the output csv file
                            raw.at[raw_counter, "DataAccurate"] = xacc and yacc
                            raw.at[raw_counter, "Task"] = "Target detection task for UAV " + str(uavNum)
                            raw.at[raw_counter, "Qualitative"] = "Participant was looking at UAV " + str(cur_uav)
                            raw.at[raw_counter, "DistanceFromCenter"] = DataQuality.calculateDistance(centerx,centery,x,y)

                        raw_counter+=1
                count+=1

            print(missionDict)

            """
            Here, we repeat the logic used for target detection but in the context of 
            the secondary tasks. 
            """
            RRPanel = [0, 920, 930, 1440]
            FLPanel = [920, 2560, 812 ,1158]
            CMPanel = [920, 2560, 1158 ,1440]
            task_dict = {"RRTimeofRR" :RRPanel, "FLStopTime":FLPanel, "MessageTime":CMPanel}
            for task in task_dict:
                perf_counter=0
                for each in performance[task]:
                   
                    if not pd.isnull(each):
                        if task == "MessageTime":
                            if (performance.at[perf_counter,"MessageFrom"] != 'user'):
                                perf_counter+=1
                                continue
                            
                            
                        raw_counter=0
                        for mt in raw["MissionTime"]:
                            if (-.01 <= mt- each <= .01):
                                number_analyzed+=1
                                x = raw.at[raw_counter, "BestPogX"]
                                y = raw.at[raw_counter, "BestPogY"]
                                xacc= (x >= task_dict[task][0] - input_xError and x <= task_dict[task][1] + input_xError)
                                yacc = (y >= task_dict[task][2] - input_yError and y <= task_dict[task][3] + input_yError)

                                centerx = (task_dict[task][0] + task_dict[task][1])/2
                                centery = (task_dict[task][2] + task_dict[task][3])/2
                                raw.at[raw_counter, "Task"] = "Secondary detection task for "+ task
                                raw.at[raw_counter, "DataAccurate"] = xacc and yacc
                                raw.at[raw_counter, "DistanceFromCenter"] = DataQuality.calculateDistance(centerx,centery,x,y)
                                
                                if xacc and yacc:
                                    number_true+=1
                                    raw.at[raw_counter, "Qualitative"] = "Participant was correctly looking at the " + task
                                else: 
                                    cur_uav = DataQuality.which_uav(x, y)
                                    number_false+=1
                                    if cur_uav == "Inconclusive":
                                        cur_task = DataQuality.which_secondary_task(x, y, task_dict)
                                        if cur_task=="Inconclusive":
                                            raw.at[raw_counter, "Qualitative"] = "Unable to pinpoint participant's gaze location."
                                        else:
                                            raw.at[raw_counter, "Qualitative"] = "Participant was looking at "+ cur_task
                                    else:
                                        raw.at[raw_counter, "Qualitative"] = "Participant was looking at "+ str(cur_uav)
                            raw_counter+=1
                    perf_counter+=1
           
            raw.to_csv(output_file_name, index=False)
            text6.configure(text='Status: Success! The output file now shows data quality information.')
            #Creating summary statistics file (STILL IN PROGRESS)
            percent_accurate = number_true/number_analyzed
            summary_stats = open("quality_summary.txt", 'w')
            summary_stats.write("The data was "+ str(100 * percent_accurate) + " percent accurate.\n")
            summary_stats.write("Of the "+ str(number_analyzed)+  " data points analyzed, " + str(number_true)+" data points were accurate while " + str(number_false) + " were inaccurate." )
            summary_stats.close()

            #Return the dataframe so we can then use it in preProcess()
            return raw
def ThresholdEstimation(df):
    mean = 0
    std_dev = 0
    summ = 0
    N = 0
    vel_list = []
    PTold = 250 #Dummy value .Initially, it is the value set by us (in the 100-300 degrees/sec range)
    PTnew = 0
    diff = PTnew - PTold
    velocities = df['Angular Velocity (in degrees/second)'] #list of angular velocities, probably a column from a Pandas dataframe 
    mean_velocities=sum(velocities)/len(velocities)
    std_dev_velocities = statistics.stdev(velocities,mean_velocities)
    i=0
    while abs(diff)>1:
        summ = 0
        N = 0
        for vel in velocities:
            if vel < PTold:
                summ=summ+vel
                N=N+1
                vel_list.append(vel)   
        if (N!=0):
            mean=summ/N
        std_dev = statistics.stdev(vel_list,mean)
        PTold = PTnew
        PTnew = mean +6*std_dev
        onset_threshold = mean +3*std_dev
        offset_threshold = 0.7*onset_threshold + 0.3*(mean_velocities+3*std_dev_velocities)
        diff = PTnew - PTold
    return PTnew,onset_threshold, offset_threshold
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

        #Calling the data quality function! This returns a dataframe that was passed through the Data quality process
        df = dq()
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
            # CHANGE RESOLUTION OF X HERE
            for each in column_names_X:
                df[each] = df[each].multiply(width_of_screen)

            # CHANGE RESOLUTION OF Y HERE
            for each in column_names_Y:
                df[each] = df[each].multiply(height_of_screen)
                
                
################################################################
# In this section we calculate the visual angles, angular velocities, and append the to the dataframe
        Delta = [] #in pixels
        Angular_Velocity = []
        Delta_mm = []
        Delta_rad = [] 
        for i in range(0,len(df.index)):
                if i==len(df.index)-1: #in this case we reach the end of the dataframe and dont have an i+1
                    x1 = df['BestPogX'][i-1]
                    y1 = df['BestPogY'][i-1]  
                    time_diff =abs(df['Time'][i-1])
                    
                else:
                    
                    x1 = df['BestPogX'][i+1]-df['BestPogX'][i]
                    y1 = df['BestPogY'][i+1]-df['BestPogY'][i]
                    time_diff=abs(df['Time'][i+1]-df['Time'][i]) 
                    
                if tracker_type==1: #If Gazepoint Tracker                    
                        Delta.append(math.sqrt(pow(x1,2)+pow(y1,2)))
                        Delta_mm.append(Delta[i]*0.207565625)
                        Delta_rad.append(math.atan(Delta_mm[i]/(23.62204724*25.4)))
                        velocity = Delta_rad[i]*57.29577951/time_diff #convert to degrees and divide by time difference
                        Angular_Velocity.append(velocity)
                    
            
        df['Delta (in pixels)'] = Delta #Create a new column and append the visual angle values in pixels
        df['Delta (in mm)'] = Delta_mm #Create a new column and append the visual angle values in mm
        df['Delta (in rad)'] = Delta_rad #Create a new column and append the visual angle values in rad
        df['Angular Velocity (in degrees/second)'] = Angular_Velocity #Create a new column and append the angular velocity in degrees per second
        Threshold=ThresholdEstimation(df)
        print(Threshold)
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

text4 = Label(frame4, text='Enter Performance File/Folder Name: ')
text4.pack(side=LEFT)
inputP_name = Entry(frame4)
inputP_name.pack(side=LEFT)


text5 = Label(frame5, text='Enter Output File Name: ')
text5.pack(side=LEFT)
output_name = Entry(frame5)
output_name.pack(side=LEFT)


text6 = Label(frame6, text='Eye Tracker Type:')

one = Button(window, text="Gazepoint", width="10", height="3",command=lambda : preProcess(1))
one.pack(side="top")


text7 = Label(frame7, text='Status: N/A')
text7.pack()

window.mainloop()
