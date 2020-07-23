import numpy as np
import random
from scipy.signal import argrelextrema

rand_list = []
for i in range(10):
    rand_list.append(random.randint(0,100))
x = np.array(rand_list)

# for local maxima. Returns a tuple of arrays. 
local_maxima = argrelextrema(x, np.greater)
print(x)
print(local_maxima)
maxima_count = (len(local_maxima[0]))
threshold = 50 
for i in local_maxima[0]:
    """
    for every index at which we found a local maximum, check that it exceeds the 
    threshold. Thene look backwards and forwards, until you find points that are below the threshold.
    Save the indices of the start and end points. 
    """
    index = i
    #Num is set equal to the threshold to begin with so the algorithm starts
    num= 50
    #This condition is for when we find a peak (local maximum) that is below threshold
    if x[i] < threshold:
        continue

    #if we do find a peak that is above the threshold, check backward and forward.
    #Currently, this prints the start and end indices of saccades within list of data
    else: 
        #need to check before and after the peak, so we have two while loops
        while num >= threshold: 
            index-=1
            num = x[index]
            if index -1 == -1:
                break
        before = str(index + 1)

        #resetting index variable and num so we go back to the peak
        #this way we can check after the peak to see where the saccade ends
        index = i
        num = 50
        while num >= threshold:
            index+=1
            num = x[index]
            if index+1 == len(x):
                break
        after = str(index-1)
        print("(" + before + ", " + after + ")")                
        
    #Now also have to check on the other side of the peak, which still is saved in the index variable 

