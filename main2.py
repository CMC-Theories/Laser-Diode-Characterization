from Keysight import *
from fluke8845A import *
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from astropy import modeling


RM = pyvisa.ResourceManager()
print(RM.list_resources())
settings = {'port': 'COM3', 'baudrate':38400, 'timeout':5, 'parity':serial.PARITY_EVEN, 'stopbits':serial.STOPBITS_TWO, 'bytesize':serial.SEVENBITS}
fluke = Fluke(**settings)

fluke.SARCommand("*cls") # Clear all errors
fluke.SARCommand("sens:func volt") #sets sensor function to DC volts
fluke.SARCommand("sens:volt:rang:auto on") #sets voltage range to auto
fluke.SARCommand("volt:dc:nplc 0.2") # sets 
fluke.SARCommand("zero:auto 0") # Turns off autozero
fluke.SARCommand("trig:sour imm") # Set the trigger to immediate
fluke.SARCommand("trig:del 0") # Trigger delay is 0 (fast read)
fluke.SARCommand("trig:coun 1") # Set trigger count to one
#fluke.SARCommand("disp off") # Turns off displace for faster reading
fluke.SARCommand("syst:rem") # Set the system to remote mode
fluke.SARCommand("samp:coun 5", default_wait_time=0.1) # Set the sample count to 5 (Variance check)
fluke.SARCommand(":INIT") # Inits the machine
while "1" not in fluke.SARCommand("*OPC?"): # Check if measurements have been taken
    print("Waiting...")
    time.sleep(0.1)



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
dic = {}
dic = step(low, high, dic) # Note, stores all values in global measured value...

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
plt.title('I-L Curve of Diode at 20 Deg C')
plt.legend()
plt.show()

