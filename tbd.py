from numpy import c_



'''future potential code to use? can show heat maps but not sure how to exactly use them yet'''
import numpy as np
import matplotlib.pyplot as plt
import random

n = 100000

x = np.random.standard_normal(n)
y = 3.0 * x + 2.0 * np.random.standard_normal(n)


#x, y = np.loadtxt("data.txt",unpack=True)

x = [3.4,1.2,5.5]
y = [1.2,11,4.2]
plt.hist2d(x,y)

plt.title("How to plot a 2d histogram with matplotlib ?")

plt.show()
#plt.savefig("histogram_2d_01.png", bbox_inches='tight')

plt.close()



