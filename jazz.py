import numpy as np
import matplotlib.pyplot as plt

from math import sin

low = 0
high = 2.0
measured = {}

def measure(x):
    # do actual measurement here, instead we are doing sin(x)/(x+.00001)
    return sin(x)/(x+0.00001)

def step(low, high, threshold=0.000001, min_delta = 10**-6):
    if high - low <= min_delta:
        return
    if low not in measured:
        yl = measure(low)
        measured[low] = yl
    else:
        yl = measured[low]
    if high not in measured:
        yh = measure(high)
        measured[high] = yh
    else:
        yh = measured[high]
    mp = (low + high)/2
    if mp not in measured:
        y = measure(mp)
        measured[mp] = y
    else:
        y = measured[mp]
    if abs(y - yl) > threshold:
        step(low, mp)
    if abs(y - yh) > threshold:
        step(mp, high)
step(low, high)
print(len(measured))
k = list(measured.keys())
plt.scatter(k, [measured[i] for i in k])
plt.show()