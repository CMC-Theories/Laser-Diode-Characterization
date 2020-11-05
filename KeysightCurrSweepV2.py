import pyvisa
RM = pyvisa.ResourceManager()
RM.list_resources()
SMU = RM.open_resource('USB0::0x0957::0x8B18::MY51143520::INSTR') #names instrument
SMU.write("*RST")                                                 #resets to all default settings
SMU.write('sour:func:mode curr')                                  #sets source output to current
SMU.write('sour:func:shap puls')                                  #sets source function to pulse
SMU.write('sour:curr:mode sweep')                                 #sets source output to sweep
SMU.write('sour:curr:star 0')                                     #sets curr sweep start to 0 A
SMU.write('sour:curr:stop 2')                                     #sets curr sweep max to 2 A
SMU.write('sour:curr:step 0.05')                                  #sweeps by 0.05 A steps
SMU.write('puls:del 1E-04')                                       #pulse delay to 0.1 ms
SMU.write('puls:widt 1E-04')                                      #pulse width to 0.1 ms  
SMU.write('sens:volt:aper 1E-04')                                 #sensor measurement integration @ 0.1 ms
SMU.write('sens:volt:auto on')                                    #sensor volt range to auto
SMU.write('sens:rem on')                                          #enables remote sensing
SMU.write('form:elem:sens volt, curr, time')                      #data format for output
SMU.write('trac:feed sens')                                       #save data to trace buffer
SMU.write('outp:filt off')                                        #disables lowpass filter of output
SMU.write('outp:off:auto on')                                     #allows output to turn off after sweep
SMU.write('outp on')                                              #turns on output
SMU.write('init (@1)')                                            #starts pulse sweep
