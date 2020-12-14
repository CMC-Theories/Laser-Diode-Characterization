
import serial
import time

class Fluke:
    # NOTE: You need to look up which COM port the fluke 8845A is connected to
    # For mine it was COM4, replace below with it.
    def __init__(self, port: str, baudrate: int, timeout: float, parity: str, stopbits: int, bytesize: int, **kwargs):
        self.settings = kwargs
        self.settings.update({'port':port, 'baudrate': baudrate, 'timeout':timeout, 'parity':parity, 'stopbits': stopbits, 'bytesize':bytesize})
        print(self.settings)
        self.ser = serial.Serial(**self.settings)
    
    def SARCommand(self, command,default_wait_time=0.05, ending=b'\r\n', should_halt=False)->str:
        """Sends and recieves data along the RS232 line.

        Args:
            command (str): Command to send to the device, without line feed and carrage.
            default_wait_time (float, optional): How much time to wait for between sending and receiving. Defaults to 0.01s. Uses time.sleep.
            ending (bytes, optional): Line ending to send to device, appended to the end of the command. Defaults to b'\r\n'.
            should_halt (bool, optional): Should the system wait for ANY response from the device? Defaults to False.

        Returns:
            str: Recieved data, may be nothing if no response, might be more if data wasn't previously read. 
        """
        self.ser.write(command.encode('utf-8') + ending)
        while self.ser.out_waiting != 0:
            time.sleep(0.01)
        time.sleep(default_wait_time)
        while self.ser.in_waiting == 0 and should_halt:
            time.sleep(0.01)
        return self.ser.read(self.ser.in_waiting).decode('utf-8')

    def SACRCommand(self, command: str, wait_for_timeout = 0.1,default_wait_time=0.05, ending=b'\r\n', should_halt=False):
        """Sends and recieves data along the RS232 line.

        Args:
            command (str): Command to send to the device, without line feed and carrage.
            wait_for_timeout (float, optional): Amount of time before declaring the input to be dead. It will wait at least this amount before returning. Defaults to 0.1.
            default_wait_time (float, optional): How much time to wait for between sending and receiving. Defaults to 0.01s. Uses time.sleep.
            ending (bytes, optional): Line ending to send to device, appended to the end of the command. Defaults to b'\r\n'.
            should_halt (bool, optional): Should the system wait for ANY response from the device? Defaults to False.

        Returns:
            str: Recieved data, may be nothing if no response, might be more if data wasn't previously read. 
        """
        self.ser.write(command.encode('utf-8') + ending)
        while self.ser.out_waiting != 0:
            time.sleep(0.01)
        time.sleep(default_wait_time)
        output = ""
        while self.ser.in_waiting == 0 and should_halt:
            time.sleep(0.01)
        output = self.ser.read(self.ser.in_waiting).decode('utf-8')
        time.sleep(wait_for_timeout)
        while self.ser.in_waiting != 0:
            output = output+ self.ser.read(self.ser.in_waiting).decode('utf-8')
            time.sleep(wait_for_timeout)
        return output
    def Close(self):
        self.ser.close()

"""
settings = {'port': 'COM3', 'baudrate':38400, 'timeout':5, 'parity':serial.PARITY_EVEN, 'stopbits':serial.STOPBITS_TWO, 'bytesize':serial.SEVENBITS}
fluke = Fluke(**settings)
fluke.SARCommand("*cls") # Clear all errors
fluke.SARCommand("conf:volt:dc 0.1") # Set DC range to manual at 100mV
fluke.SARCommand("volt:dc:nplc 0.2") # Set NPLC to faster reading rate at 4 1/2 digits??? (15 pulses per read)
fluke.SARCommand("zero:auto 0") # Turns off autozero
fluke.SARCommand("trig:sour imm") # Set the trigger to immediate
fluke.SARCommand("trig:del 0") # Trigger delay is 0 (fast read)
fluke.SARCommand("trig:coun 1") # Set trigger count to one
fluke.SARCommand("disp off") # Turns off displace for faster reading
fluke.SARCommand("syst:rem") # Set the system to remote mode
fluke.SARCommand("samp:coun 5", default_wait_time=0.1) # Set the sample count to 5 (Variance check)
fluke.SARCommand(":INIT") # Inits the machine
while "1" not in fluke.SARCommand("*OPC?"): # Check if measurements have been taken
    print("Waiting...")
    time.sleep(0.1)

print(fluke.SACRCommand(":FETCH?", wait_for_timeout=0.2, default_wait_time=0.2,should_halt=True)) # gets all measurements, comma sep.
fluke.SARCommand('syst:loc', default_wait_time=0.2) # Sets the system to local mode again
fluke.SARCommand("disp on", default_wait_time=0.2) # Turns on displays
fluke.SARCommand("*cls", default_wait_time=0.1) # Clear all errors
fluke.Close()
"""