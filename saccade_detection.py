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
maxima_count = (len(local_maxima[0]))
threshold = 50 
for i in local_maxima[0]:
    """
    for every index at which we found a local maximum, check that it exceeds the 
    threshold. Thene look backwards and forwards, until you find points that are below the threshold.
    Save the indices of the start and end points. 
    """
    index = i
    num= 50
    #Not a saccade if this if statement is true
    if x[i] < threshold:
        continue
    else: 
        while num >= threshold: 
            if (index-1 == -1) or x[index-1] < threshold:
                print(index)
                break
            index-=1
            num = x[index]
    #Now also have to check on the other side of the peak, which still is saved in the index variable 

