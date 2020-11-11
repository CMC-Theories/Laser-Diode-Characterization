import pyvisa
class Keysight:
    def __init__(self, resource_name: str, initialize_w_def: bool, pyvisaRM):
        self.RM = pyvisaRM
        self.line = self.RM.open_resource(resource_name)
        if initialize_w_def:
            self.line.write("*RST")                                                  #Resets all system settings to default
            self.line.write("syst:lfr 60")                                           #Sets Power line frequency to 60 Hz
            self.line.write('sour:func:mode curr')                                   #Source output to current
            self.line.write('sour:func:shap puls')                                   #Source function to pulse
            self.line.write('sour:puls:del 1E-04')                                   #Pulse delay of 100 us
            self.line.write('sour:puls:widt 1E-04')                                  #Pulse width of 100 us
            self.line.write('sour:curr 0.0')                                         #Zeros initial current value
            self.line.write('sens:rem on')                                           #Remote sensing on
            self.line.write('sens:volt:prot:pos 5')                                  #Maximum voltage read set to 5 V
            self.line.write('form:elem:sens volt, curr')                             #Orders output data as Voltage, Current
    def SAR(self, writelist, querylist):
        for i in writelist:
            self.line.write(str(i))
        queries = []
        for j in querylist:
            queries.append(self.line.query(j))
        return queries
    def SASR(self, writelist, query):
        for i in writelist:
            self.line.write(str(i))
        return self.line.query(query)
        
