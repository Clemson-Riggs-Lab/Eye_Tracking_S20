from numpy import c_
'''future potential code to use? can show heat maps but not sure how to exactly use them yet'''
import numpy as np
import matplotlib.pyplot as plt
import random
import pandas

'''
Dustin Nguyen
ddn3aq
4/29/20

'''

data = pandas.read_csv("myprocessedtest.csv", header=0)

#change this value to change how detailed the heatmap is... lower numbers mean higher quality.
precision = 5

col_a = list(data['BestPogX'])
col_b = list(data['BestPogY'])

fig, ax = plt.subplots()
h = ax.hist2d(col_a, col_b, bins=[np.arange(0,2560,precision),np.arange(0,1440,precision)])
plt.colorbar(h[3], ax=ax)

plt.gca().invert_yaxis()

plt.title("Heat Map Demo")


plt.show()


#plt.savefig("histogram_2d_01.png", bbox_inches='tight')

plt.close()



