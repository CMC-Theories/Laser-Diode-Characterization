import pyvisa
RM = pyvisa.ResourceManager()
RM.list_resources()
#this returns the resources names in a list
SMU = RM.open_resource('<name of keysight b2901a>')
SMU.write(":curr:mode sweep; start 0; stop 2; step 0.05")
#sets the current source to be in sweep mode from 0-2A in 0.05A steps
SMU.write(":puls:del 1E-05; widt 1E-05")
#sets pulse width of source output and delay to be 10 us. not sure yet if this will work with the sweep steps.