from Keysight import *
from fluke8845A import *
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


RM = pyvisa.ResourceManager()
print(RM.list_resources())
settings = {'port': 'COM4', 'baudrate':38400, 'timeout':5, 'parity':serial.PARITY_EVEN, 'stopbits':serial.STOPBITS_TWO, 'bytesize':serial.SEVENBITS}
fluke = Fluke(**settings)

fluke.SARCommand("*cls") # Clear all errors
fluke.SARCommand("sens:func volt") #sets sensor function to DC volts
fluke.SARCommand("conf:volt:dc 2") # Set DC range to manual at 2 V
fluke.SARCommand("volt:dc:nplc 0.2") # sets 
fluke.SARCommand("zero:auto 0") # Turns off autozero
fluke.SARCommand("trig:sour imm") # Set the trigger to immediate
fluke.SARCommand("trig:del 0") # Trigger delay is 0 (fast read)
fluke.SARCommand("trig:coun 1") # Set trigger count to one
#fluke.SARCommand("disp off") # Turns off displace for faster reading
fluke.SARCommand("syst:rem") # Set the system to remote mode
fluke.SARCommand("samp:coun 2", default_wait_time=0.1) # Set the sample count to 5 (Variance check)
fluke.SARCommand(":INIT") # Inits the machine
while "1" not in fluke.SARCommand("*OPC?"): # Check if measurements have been taken
    print("Waiting...")
    time.sleep(0.1)



keysight = Keysight('USB0::0x0957::0x8B18::MY51143520::INSTR', True, RM)

keysight.SAR(["outp on","init (@1)"],[])

def readFunc(inp):
    keysight.SAR(["sour:curr " + str(inp), "init (@1)"], [])
    fluke.SARCommand(":INIT") # Inits the machine
    while "1" not in fluke.SARCommand("*OPC?"): # Check if measurements have been taken
        print("Waiting...")
        time.sleep(0.1)
    return fluke.SACRCommand(":FETCH?", wait_for_timeout=0.2, default_wait_time=0.2,should_halt=True)
def measure(inp):
    combS = readFunc(inp).strip()
    combSep = combS.split(',')
    return [float(i) for i in combSep]
def convert(inp):
    return sum(inp)/len(inp)
def step(low, high, measured_values: dict = {}, func = measure, converter = convert, threshold=0.05, min_delta = 10**-8):
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
        yl = converter(yl)
    else:
        yl = converter(measured_values[low])
    if high not in measured_values:
        yh = func(high)
        measured_values[high] = yh
        yh = converter(yh)
    else:
        yh = converter(measured_values[high])
    mp = (low + high)/2
    if mp not in measured_values:
        y = func(mp)
        measured_values[mp] = y
        y = converter(y)
        print("Measuring " + str(mp))
    else:
        y = converter(measured_values[mp])
    if abs(y - yl) > threshold:
        step(low, mp, measured_values, func, converter, threshold, min_delta)
    if abs(y - yh) > threshold:
        step(mp, high, measured_values, func, converter, threshold, min_delta)
    return measured_values





low = 0
high= 2.0

current = np.linspace(0, 2, num=100)
dic = {i:measure(i) for i in current}


#dic = step(low, high, dic) # Note, stores all values in global measured value...

keysight.SAR(["outp off"],[])
fluke.Close()

print("Number of values measured: " + str(len(dic)))
current = list(dic.keys())
current.sort()
voltage = [convert(dic[i]) for i in current]
#def func(x,x0,A,s,off):
#    return off + (A / (np.exp(-s*(x-x0)) + 1))
#popt, pcov = curve_fit(func, current, np.diff(voltage), bounds=(0,[2, 50, 5, 10]))

yerr = [np.std(dic[i]) for i in current]

plt.scatter(current, voltage,  s = 2)
plt.errorbar(current, voltage, yerr=yerr)
#plt.plot(current, np.gradient(np.gradient(voltage,current), current))
#plt.plot(current, func(current, *popt), label = 'Curve Fit', color = 'g')
plt.ylabel('Voltage (V)')
plt.xlabel('Current (A)')
plt.title('I-L Curve of Diode at 20 Deg C')
plt.legend()
plt.show()
np.savetxt("current.csv", current, delimiter=",")
np.savetxt("voltage.csv", voltage, delimiter=",")