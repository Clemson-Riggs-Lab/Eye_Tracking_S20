import pandas as pd
'''
Dustin Nguyen
ddn3aq
2/18/2020
Riggs Lab


Usage Notes:

1. put the name of the file you want to PROCESS at like 20
2. put the name of what you want the output file name to be in line 21
3. You can change the resolution of the screen with the X and Y vairables
4. Run once, and its processed!

'''

def preProcess():
    #CHANGE OPTIONS OF THE PROGRAM HERE!!!!!!
    file_name = "dustinsTestFiles/test.csv"
    output_file_name = "dustinsTestFiles/test2.csv"
    width_of_screen = 2560
    height_of_screen = 1440
    #-------------------------------------------------------

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
    

    #Change pupil diameters from pixels to mm by multiplying with column AT

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


    df.to_csv(output_file_name, index=False)

preProcess()