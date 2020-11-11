import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from astropy import modeling

RM = pyvisa.ResourceManager()
RM.list_resources()
SMU = RM.open_resource('USB0::0x0957::0x8B18::MY51143520::INSTR')  #Note: resource name could be different, adjust here.
SMU.write("*RST")                                                  #Resets all system settings to default
SMU.write("syst:lfr 60")                                           #Sets Power line frequency to 60 Hz
SMU.write('sour:func:mode curr')                                   #Source output to current
SMU.write('sour:func:shap puls')                                   #Source function to pulse
SMU.write('sour:puls:del 1E-04')                                   #Pulse delay of 100 us
SMU.write('sour:puls:widt 1E-04')                                  #Pulse width of 100 us
SMU.write('sour:curr 0.0')                                         #Zeros initial current value
SMU.write('sens:rem on')                                           #Remote sensing on
SMU.write('sens:volt:prot:pos 5')                                  #Maximum voltage read set to 5 V
SMU.write('form:elem:sens volt, curr')                             #Orders output data as Voltage, Current
values = [0 for i in range(100)]
SMU.write('outp on')                                               #Turns on the output
SMU.write('init (@1)')                                             #Triggers current settings


def setCurRead(val):
    """Sets the current for the KeysightB22901A. Fetches the resulting voltage and current.

    Args:
        val (float): Current (in A) for the driver to send to the laser.

    Returns:
        string: A string of scientific notation floats for voltage, followed by a comma, followed by current.
    """
    SMU.write('sour:curr ' + str(val))
    SMU.write('init (@1)')
    return SMU.query('fetc:arr?')


# The following is a numerical algorithm that will sample the high and lows, and if it
#   is too much of a difference in the voltage output, then it will resample the midpoint  
#   and repeat the process. Yields a fairly smooth curve with a variable amount of points.
low = 0
high = 2.0
measured = {}

def measure(x):
    # Read in the voltage,current string, split to just the voltage.
    combS = setCurRead(x).strip()
    combSep = combS.split(',')
    return float(combSep[0])

def step(low, high, measured_values: dict = {}, func: function = measure, threshold=0.00001, min_delta = 10**-8):
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
step(low, high, {}) # Note, stores all values in global measured value...


SMU.write('outp off')
"""values = np.array(values)
np.savetxt('VoltCurrMeas.csv', values,fmt = '%s', delimiter=',', newline = '\n')
mydata = np.genfromtxt('VoltCurrMeas.csv', delimiter=',')
voltage = mydata[:,0]
current = mydata[:,1]
"""
print(len(measured))
voltage = list(measured.keys())
current = [measured[i] for i in voltage]
fitter = modeling.fitting.LevMarLSQFitter()
model = modeling.models.Gaussian1D()
fitted_model = fitter(model, voltage, current)

plt.scatter(voltage, current, s = 2)
plt.plot(voltage, fitted_model(voltage), label = 'Gaussian Fit', color = 'g')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (A)')
plt.title('I-V Curve of Diode at 20 Deg C')
plt.legend()
plt.show()