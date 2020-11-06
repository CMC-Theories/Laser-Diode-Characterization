import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from astropy import modeling

RM = pyvisa.ResourceManager()
RM.list_resources()
SMU = RM.open_resource('USB0::0x0957::0x8B18::MY51143520::INSTR')
SMU.write("*RST")
SMU.write("syst:lfr 60")
SMU.write('sour:func:mode curr')
SMU.write('sour:func:shap puls')
SMU.write('sour:puls:del 1E-04')
SMU.write('sour:puls:widt 1E-04')
SMU.write('sour:curr 0.0')
SMU.write('sens:rem on')
SMU.write('sens:volt:prot:pos 5')
SMU.write('form:elem:sens volt, curr')
values = [0 for i in range(100)]
SMU.write('outp on')
SMU.write('init (@1)')
def setCurRead(val):
    SMU.write('sour:curr ' + str(val))
    SMU.write('init (@1)')
    return SMU.query('fetc:arr?')
"""ind = np.linspace(0,2,100)
iv = ind*ind*ind/4
for k,v in enumerate(iv):
    values[k] = setCurRead(v)
"""
low = 0
high = 2.0
measured = {}

def measure(x):
    # do actual measurement here, instead we are doing sin(x)/(x+.00001)
    combS = setCurRead(x).strip()
    combSep = combS.split(',')
    return float(combSep[0])
    

def step(low, high, threshold=0.00001, min_delta = 10**-8):
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