import pyvisa
RM = pyvisa.ResourceManager()
RM.list_resources()
#this returns the resources names in a list
SMU = RM.open_resource('<name of keysight b2901a>')
SMU.write(":curr:mode sweep; start 0; stop 2; step 0.05")
#sets the current source to be in sweep mode from 0-2A in 0.05A steps
SMU.write(":func:puls; :puls:del 1E-04; widt 1E-04")
#sets pulse width of source output and delay to be 50 us, which is pulse width lower limit
SMU.write(':sens:func:off curr; :sens:rem on; :sens:wait off')
#turns off current sensing (which is on by default), turns on remote sensing (required for 4 wire setup)
#disables wait time of measurement, so it begins when triggered