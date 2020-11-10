from time import sleep
import os, time
import pyvisa

# List all availaible VISA compatible equipment
rm=pyvisa.ResourceManager()
print(rm.list_resources())

# Assumes a supply and oscilloscope is connected. Change the resource name accordingly.
supply_io_top = rm.open_resource('GPIB0::5::INSTR')
osc = rm.open_resource('USB0::62700::60984::SDSMMEBC4R1071::0::INSTR')


# ===============
# SCOPE FUNCTIONS
# ===============
#autoset
def autoset():
    osc.write('ASET')
#measure frequency
def osc_measure_freq(channel = 1):
    print(f"FREQ: osc.query(f'C{channel}:PAVA? FREQ')")
    print(f"PER: osc.query(f'C{channel}:PAVA? PER')")
    return float(osc.query(f'C{channel}:PAVA? FREQ')[13:-2])


# ==============================
# AGILENT POWER SUPPLY FUNCTIONS
# ==============================

def init_supply(vcc=0.85):
    # Init power supply. Specify voltage and current limits.
    supply_io_top.write('OUTP OFF')
    # Set IO voltage in channel 1
    supply_io_top.write('INST:SEL OUT1')
    supply_io_top.write('CURRENT 0.5')
    supply_io_top.write('VOLT 1.8')
    # Set core voltage in channel 2
    supply_io_top.write('INST:SEL OUT2')
    supply_io_top.write('CURRENT 0.5')
    supply_io_top.write('VOLT ' + str(vcc))

def turn_on():
    supply_io_top.write('OUTP ON')
    print("IO VDDs")
    print(supply_io_top.query('MEAS:CURR?;VOLT?'))

def turn_off():
    supply_io_top.write('OUTP OFF')
    print("VDD OFF")
    print(supply_io_top.query('MEAS:CURR?;VOLT?'))

# Few helper functions
def set_voltage(supply, channel, voltage):
    assert(voltage <= 1)
    supply.write('INST:SEL OUT' + str(channel))
    supply.write('VOLT ' + str(voltage))
    print("VOLTAGE: " + str(float(supply.query("VOLT?"))))
    print("CURRENT: " + str(float(supply.query("CURR?"))))

def query_voltage(chan=1):
    supply_io_top.write('INST:SEL OUT' + str(chan))
    print(float(supply_io_top.query("VOLT?")))

