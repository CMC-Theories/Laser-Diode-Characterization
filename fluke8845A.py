

# XXX: Standalone needs to be converted to python object
import serial
import time

# NOTE: You need to look up which COM port the fluke 8845A is connected to
# For mine it was COM4, replace below with it.
settings = {'port': 'COM3', 'baudrate':38400, 'timeout':5, 'parity':serial.PARITY_EVEN, 'stopbits':serial.STOPBITS_TWO, 'bytesize':serial.SEVENBITS}

def SARCommand(line: serial.serialwin32.Serial, command,default_wait_time=0.05, ending=b'\r\n', should_halt=False)->str:
    """Sends and recieves data along the RS232 line.

    Args:
        line (serial.serialwin32.Serial): 
        command (str): Command to send to the device, without line feed and carrage.
        default_wait_time (float, optional): How much time to wait for between sending and receiving. Defaults to 0.01s. Uses time.sleep.
        ending (bytes, optional): Line ending to send to device, appended to the end of the command. Defaults to b'\r\n'.
        should_halt (bool, optional): Should the system wait for ANY response from the device? Defaults to False.

    Returns:
        str: Recieved data, may be nothing if no response, might be more if data wasn't previously read. 
    """
    line.write(command.encode('utf-8') + ending)
    while line.out_waiting != 0:
        time.sleep(0.01)
    time.sleep(default_wait_time)
    while line.in_waiting == 0 and should_halt:
        time.sleep(0.01)
    return line.read(line.in_waiting).decode('utf-8')

def SACRCommand(line: serial.serialwin32.Serial, command: str, wait_for_timeout = 0.1,default_wait_time=0.05, ending=b'\r\n', should_halt=False):
    """Sends and recieves data along the RS232 line.

    Args:
        line (serial.serialwin32.Serial): 
        command (str): Command to send to the device, without line feed and carrage.
        wait_for_timeout (float, optional): Amount of time before declaring the input to be dead. It will wait at least this amount before returning. Defaults to 0.1.
        default_wait_time (float, optional): How much time to wait for between sending and receiving. Defaults to 0.01s. Uses time.sleep.
        ending (bytes, optional): Line ending to send to device, appended to the end of the command. Defaults to b'\r\n'.
        should_halt (bool, optional): Should the system wait for ANY response from the device? Defaults to False.

    Returns:
        str: Recieved data, may be nothing if no response, might be more if data wasn't previously read. 
    """
    line.write(command.encode('utf-8') + ending)
    while line.out_waiting != 0:
        time.sleep(0.01)
    time.sleep(default_wait_time)
    output = ""
    while line.in_waiting == 0 and should_halt:
        time.sleep(0.01)
    output = line.read(line.in_waiting).decode('utf-8')
    time.sleep(wait_for_timeout)
    while line.in_waiting != 0:
        output = output+ line.read(line.in_waiting).decode('utf-8')
        time.sleep(wait_for_timeout)
    return output

ser = serial.Serial(**settings)

SARCommand(ser, "*cls") # Clear all errors
SARCommand(ser, "conf:volt:dc 0.1")
SARCommand(ser, "volt:dc:nplc 0.02")
SARCommand(ser, "zero:auto 0")
SARCommand(ser, "trig:sour imm")
SARCommand(ser, "trig:del 0")
SARCommand(ser, "trig:coun 1")
SARCommand(ser, "disp off")
SARCommand(ser, "syst:rem") # Set the system to remote mode
SARCommand(ser, "samp:coun 5", default_wait_time=0.1) # Set the sample count to 100??????
SARCommand(ser, ":INIT")
while "1" not in SARCommand(ser, "*OPC?"):
    print("Waiting...")
    time.sleep(0.1)

print(SACRCommand(ser, ":FETCH?", wait_for_timeout=0.2, default_wait_time=0.2,should_halt=True)) # gets 1 measurement.
SARCommand(ser, 'syst:loc', default_wait_time=0.2) # Sets the system to local mode
SARCommand(ser, "disp on", default_wait_time=0.2)
SARCommand(ser, "*cls", default_wait_time=0.1) # Clear all errors
ser.close()