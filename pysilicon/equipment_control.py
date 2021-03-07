from time import sleep
import os, time
import pyvisa
import sys

rm = pyvisa.ResourceManager()
supply_dummy_obfus = rm.open_resource('GPIB0::4::INSTR')
supply_fpga_sensor = rm.open_resource('GPIB0::7::INSTR')
supply_io_top = rm.open_resource('GPIB0::5::INSTR')
func_gen = rm.open_resource('GPIB0::10::INSTR')
osc = rm.open_resource('USB0::62700::60984::SDSMMEBC4R1071::0::INSTR')


def autoset():
    osc.write('ASET')

def osc_measure_freq(channel = 1):
    channel = int(channel)
    print(f"FREQ: {float(osc.query(f'C{channel}:PAVA? FREQ')[13:-3])}")
    print(f"PER: {float(osc.query(f'C{channel}:PAVA? PER')[12:-2])}")

    return float(osc.query(f'C{channel}:PAVA? FREQ')[13:-3])


def set_voltage(supply, channel, voltage):
    if isinstance(supply, str):
        supply = globals()[supply]
    channel = int(channel)
    voltage = float(voltage)
    assert(voltage <= 1)

    supply.write('INST:SEL OUT' + str(channel))
    supply.write('VOLT ' + str(voltage))
    print("VOLTAGE: " + str(float(supply.query("VOLT?"))))
    print("CURRENT: " + str(float(supply.query("CURR?"))))

def turn_on(supply):
    if isinstance(supply, str):
        supply = globals()[supply]

    if supply == func_gen:
        func_gen.write('OUTP1:POS ON')
    else:
        supply.write('OUTP ON')
        time.sleep(0.2)
        print('Channel 1 I, V: ' + supply.query('MEAS:CURR?;VOLT?'))

def query_voltage(supply, chan=1):
    if isinstance(supply, str):
        supply = globals()[supply]
    chan = int(chan)

    supply.write('INST:SEL OUT' + str(chan))
    print(float(supply_fpga_sensor.query("VOLT?")))


def turn_off(supply):
    if isinstance(supply, str):
        supply = globals()[supply]

    if supply == func_gen:
        func_gen.write('OUTP1:POS OFF')
    else:
        supply.write('OUTP OFF')
        time.sleep(0.2)
        print(supply.query('MEAS:CURR?;VOLT?'))

def set_freq(freq):
    freq = float(freq)
    func_gen.write('FREQ ' + str(freq) + ' MHz')
    time.sleep(1)
    func_gen.query('FREQ?')

def init_test(vcc=0.85, vdd_core=0.7):
    vcc = float(vcc)
    vdd_core = float(vdd_core)

    # Init power supplies
    supply_fpga_sensor.write('OUTP OFF')
    supply_dummy_obfus.write('OUTP OFF')
    supply_io_top.write('OUTP OFF')

    supply_io_top.write('INST:SEL OUT1')
    supply_io_top.write('CURRENT 0.5')
    supply_io_top.write('VOLT 1.8')
    supply_io_top.write('INST:SEL OUT2')
    supply_io_top.write('CURRENT 0.5')
    supply_io_top.write('VOLT ' + str(vcc))

    #vdd_test = 0.7
    #vdd_core = 0.7
    supply_dummy_obfus.write('INST:SEL OUT1')
    supply_dummy_obfus.write('CURRENT 0.1')
    supply_dummy_obfus.write('VOLT 0.0')
    supply_dummy_obfus.write('INST:SEL OUT2')
    supply_dummy_obfus.write('CURRENT 0.1')
    supply_dummy_obfus.write('VOLT 0.0')
    supply_fpga_sensor.write('INST:SEL OUT1')
    supply_fpga_sensor.write('CURRENT 0.25')
    supply_fpga_sensor.write('VOLT 0.0')
    supply_fpga_sensor.write('INST:SEL OUT2')
    supply_fpga_sensor.write('CURRENT 0.1')
    supply_fpga_sensor.write('VOLT 0.0')

    # Func gen
    #func_gen.write('OUTP1 OFF')
    #func_gen.write('OUTP2 OFF')
    #func_gen.write('FUNC:MOD1 SQUAre')
    #func_gen.write('OUTP1:DIV 1')
    #func_gen.write('PM1 OFF')
    #func_gen.write('DEL1 0ns')
    #func_gen.write('VOLT1:LOW 0mV')
    #func_gen.write('VOLT1:HIGH 1.6V')
    #func_gen.write('VOLT1:TERM 0V')
    #func_gen.write('FREQ 20 MHz')
    #time.sleep(1)
    #func_gen.query('FREQ?')
    #func_gen.write('OUTP1:POS ON')

def turn_off_all():
    supply_fpga_sensor.write('OUTP OFF')
    print("CORE VDD OFF")
    print(supply_fpga_sensor.query('MEAS:CURR?;VOLT?'))
    supply_dummy_obfus.write('OUTP OFF')
    print("TEST VDD OFF")
    print(supply_dummy_obfus.query('MEAS:CURR?;VOLT?'))
    supply_io_top.write('OUTP OFF')
    print("IO VDDs OFF")
    print(supply_io_top.query('MEAS:CURR?;VOLT?'))

def turn_on_top():
    supply_io_top.write('OUTP ON')
    print("IO VDDs")
    print(supply_io_top.query('MEAS:CURR?;VOLT?'))

def turn_on_core(core, vcc_core = 0.7):
    vcc_core = float(vcc_core)
    if core == 'efpga':
        supply_fpga_sensor.write('INST:SEL OUT1')
        supply_fpga_sensor.write('CURRENT 0.1')
        supply_fpga_sensor.write('VOLT ' + str(vcc_core))
        supply_fpga_sensor.write('OUTP ON')
        print("CORE VDD ON")
        print(supply_fpga_sensor.query('MEAS:CURR?;VOLT?'))

    elif core == 'sensor':
        supply_fpga_sensor.write('INST:SEL OUT2')
        supply_fpga_sensor.write('CURRENT 0.1')
        supply_fpga_sensor.write('VOLT ' + str(vcc_core))
        supply_fpga_sensor.write('OUTP ON')
        print("CORE VDD ON")
        print(supply_fpga_sensor.query('MEAS:CURR?;VOLT?'))

    elif core == 'dummy':
        supply_dummy_obfus.write('INST:SEL OUT1')
        supply_dummy_obfus.write('CURRENT 0.1')
        supply_dummy_obfus.write('VOLT ' + str(vcc_core))
        supply_dummy_obfus.write('OUTP ON')
        print("CORE VDD ON")
        print(supply_fpga_sensor.query('MEAS:CURR?;VOLT?'))

    elif core == 'obfus':
        supply_dummy_obfus.write('INST:SEL OUT2')
        supply_dummy_obfus.write('CURRENT 0.1')
        supply_dummy_obfus.write('VOLT ' + str(vcc_core))
        supply_dummy_obfus.write('OUTP ON')
        print("CORE VDD ON")
        print(supply_fpga_sensor.query('MEAS:CURR?;VOLT?'))


def measure_all():
    print('FPGA')
    supply_io_top.write('INST:SEL OUT1')
    val = supply_fpga_sensor.query('MEAS:CURR?;VOLT?')
    print( "CUR : " + str(round(float(val.split(";")[0]),4)) )
    print( "VOLT: " + str(round(float(val.split(";")[1]),4)) )

    print('\nDUMMY')
    supply_dummy_obfus.write('INST:SEL OUT1')
    val = supply_dummy_obfus.query('MEAS:CURR?;VOLT?')
    print( "CUR : " + str(round(float(val.split(";")[0]),4)) )
    print( "VOLT: " + str(round(float(val.split(";")[1]),4)) )

    print('\nIO')
    supply_io_top.write('INST:SEL OUT1')
    val = supply_io_top.query('MEAS:CURR?;VOLT?')
    print( "CUR : " + str(round(float(val.split(";")[0]),4)) )
    print( "VOLT: " + str(round(float(val.split(";")[1]),4)) )

    print('\nCLKGEN')
    supply_io_top.write('INST:SEL OUT2')
    val = supply_io_top.query('MEAS:CURR?;VOLT?')
    print( "CUR : " + str(round(float(val.split(";")[0]),4)) )
    print( "VOLT: " + str(round(float(val.split(";")[1]),4)) )


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please call this script with the name of the function and the parameters you want to pass")
    else:
        func = sys.argv[1]
        args = sys.argv[2:]
        locals()[func](*args)
