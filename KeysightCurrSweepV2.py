"""import pyvisa
RM = pyvisa.ResourceManager()
RM.list_resources()
SMU = RM.open_resource('USB0::0x0957::0x8B18::MY51143520::INSTR') #names instrument
SMU.write("*RST")                                                 #resets to all default settings
SMU.write('syst.lfr 60')                                          #sets power line freq to 60 Hz
SMU.write('sour:func:mode curr')                                  #sets source output to current
SMU.write('sour:func:shap puls')                                  #sets source function to pulse
SMU.write('sour:curr:mode sweep')                                 #sets source output to sweep
SMU.write('sour:curr:star 0')                                     #sets curr sweep start to 0 A
SMU.write('sour:curr:stop 2')                                     #sets curr sweep max to 2 A
SMU.write('sour:curr:step 0.05')                                  #sweeps by 0.05 A steps
SMU.write('puls:del 1E-04')                                       #pulse delay to 0.1 ms
SMU.write('puls:widt 1E-04')                                      #pulse width to 0.1 ms  
SMU.write('sens:volt:aper 1E-05')                                 #sensor measurement integration @ 10 us
SMU.write('sens:volt:auto on')                                    #sensor volt range to auto
SMU.write('sens:rem on')                                          #enables remote sensing
SMU.write('form:elem:sens volt, curr, time')                      #data format for output
SMU.write('trac:feed sens')                                       #save data to trace buffer
SMU.write('outp:filt off')                                        #disables lowpass filter of output
SMU.write('outp:off:auto on')                                     #allows output to turn off after sweep
SMU.write('outp on')                                              #turns on output
SMU.write('init (@1)')                                            #starts pulse sweep
"""
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
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
values = [0 for i in range(50)]
SMU.write('outp on')
SMU.write('init (@1)')
def setCurRead(val):
    SMU.write('sour:curr ' + val)
    SMU.write('init (@1)')
    return SMU.query('fetc:arr?')
ind = np.arange(50)
iv = (ind*ind)*2 / 50*50
for k,v in enumerate(iv):
    values[k] = setCurRead(v)

SMU.write('outp off')
values = np.array(values)
np.savetxt('VoltCurrMeas.csv', values,fmt = '%s', delimiter=',', newline = '\n')
mydata = np.genfromtxt('VoltCurrMeas.csv', delimiter=',')
voltage = mydata[:,0]
current = mydata[:,1]
plt.scatter(voltage, current)
plt.show()