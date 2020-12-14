from Keysight import *
from fluke8845A import *
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from astropy import modeling
import tkinter as tk
from tkinter import filedialog
import os.path as path
root = tk.Tk()
root.withdraw()
file_path = filedialog.asksaveasfilename()
xox = path.split(file_path)
root.destroy()

RM = pyvisa.ResourceManager()
print(RM.list_resources())
settings = {'port': 'COM4', 'baudrate':38400, 'timeout':5, 'parity':serial.PARITY_EVEN, 'stopbits':serial.STOPBITS_TWO, 'bytesize':serial.SEVENBITS}
fluke = Fluke(**settings)

keysight = Keysight('USB0::0x0957::0x8B18::MY51143520::INSTR', True, RM)

keysight.SAR(["outp on","init (@1)"],[])

def readFunc(inp):
    return keysight.SASR(["sour:curr " + str(inp), "init (@1)"],"fetc:arr?")
def measure(inp):
    combS = readFunc(inp).strip()
    combSep = combS.split(',')
    return float(combSep[0])
def step(low, high, measured_values: dict = {}, func = measure, threshold=0.001, min_delta = 10**-8):
    """Recursively samples the low and high points of the system, if
    the difference between the output is more than the threshold, it will
    sample the midpoint, and then recurse with the midpoint to the low and high
    values. Stops the madness when the difference between the points is less
    than the min_delta.

    Args:
        low (float): Low x to sample
        high (float): High x to sample
        measured_values (dict, optional): Dictionary for measured values to be placed into, keys are currents and values are voltages. Defaults to an empty dictionary.
        func (function, optional): Custom measure function for the step function. Must accept a single float and return a single float, can pause but will slow down this function. Defaults to the measure function above.
        threshold (float, optional): Minimum Difference between y_i and y_i+1 for the system to recursively visit the midpoint. Defaults to 0.00001.
        min_delta (float, optional): Minimum delta between x_i and x_i+1 before the system halts. Defaults to 10**-8.
    """
    if high - low <= min_delta:
        return
    if low not in measured_values:
        yl = func(low)
        measured_values[low] = yl
    else:
        yl = measured_values[low]
    if high not in measured_values:
        yh = func(high)
        measured_values[high] = yh
    else:
        yh = measured_values[high]
    mp = (low + high)/2
    if mp not in measured_values:
        y = func(mp)
        measured_values[mp] = y
    else:
        y = measured_values[mp]
    if abs(y - yl) > threshold:
        step(low, mp, measured_values)
    if abs(y - yh) > threshold:
        step(mp, high, measured_values)
    return measured_values


low = 0
high= 2.0

current = np.linspace(0, 2, num=500)
dic = {i:measure(i) for i in current}

#dic = {}
#dic = step(low, high, dic) # Note, stores all values in global measured value...

keysight.SAR(["outp off"],[])

print("Number of values measured: " + str(len(dic)))
current = list(dic.keys())
current.sort()
voltage = [dic[i] for i in current]
fitter = modeling.fitting.LevMarLSQFitter()
model = modeling.models.Gaussian1D()
fitted_model = fitter(model, voltage, current)

plt.scatter(voltage, current, s = 2)
plt.plot(voltage, fitted_model(voltage), label = 'Gaussian Fit', color = 'g')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (A)')
plt.legend()



np.savetxt(xox[0] + "/" + xox[1] + ".csv", np.transpose(np.vstack(current, voltage)), delimiter=",")
#np.savetxt(xox[0] +"/CUR" + xox[1] + ".csv", current, delimiter=",")
#np.savetxt(xox[0] +"/VOL" + xox[1]+ ".csv", voltage, delimiter=",")

plt.savefig(xox[0] + "/Fig" + xox[1] + '.png')
plt.show()
exit()