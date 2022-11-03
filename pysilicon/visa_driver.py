from time import sleep
import os, time
import pyvisa
import sys

# Written for, and only tested with Siglent supplies
class VisaController:
    def __init__(self, default_v = 0.85, default_i = 0.5):
        self.supplies = {}
        self.ports = {}
        self.osc = None
        self.rm = pyvisa.ResourceManager('@py')
        self.default_v = default_v
        self.default_i = default_i
        print(self.rm.list_resources())
        
    def add_osc(self, visa_id):
        if self.osc is not None:
            print(f'Oscilloscope already exists!')
        else:
            self.osc = self.rm.open_resource(visa_id)
    
    def add_supply(self, name, visa_id):
        if name in self.supplies.keys():
            print(f'Supply {name} already exists!')
        else:
            self.supplies[name] = self.rm.open_resource(visa_id)
            self.supplies[name].write_termination='\n'
            self.supplies[name].read_termination='\n'
            self.supplies[name].query_delay=0.1
    
    def add_port(self, name, supply_name, channel_id):
        if name in self.ports.keys():
            print(f'Port {name} already exists!')
        else:
            self.ports[name] = (supply_name, channel_id)
            self.set_lims(name, self.default_v, self.default_i)
    
    def set_lims(self, port_name, v = None, i = None, noassert = False):
        supply = self.supplies[self.ports[port_name][0]]
        channel = self.ports[port_name][1]
#         print(self.ports[port_name][0], channel, f'CH{channel}:VOLT {v}', f'CH{channel}:CURR {i}')
        if v is not None:
            assert noassert | (v <= 1.2)
            supply.write(f'CH{channel}:VOLT {v}')
            time.sleep(0.05)
        if i is not None:
            assert noassert | (i <= 0.5)
            supply.write(f'CH{channel}:CURR {i}')
            time.sleep(0.05)

    def turn_on(self, port_name):
        supply = self.supplies[self.ports[port_name][0]]
        channel = self.ports[port_name][1]
        supply.write(f'OUTP CH{channel},ON')
        time.sleep(0.05)
    
    def turn_off(self, port_name):
        supply = self.supplies[self.ports[port_name][0]]
        channel = self.ports[port_name][1]
#         print(self.ports[port_name][0], channel, f'OUTP CH{channel},OFF')
        supply.write(f'OUTP CH{channel},OFF')
        time.sleep(0.05)
    
    def turn_on_all(self):
        for port_name in self.ports.keys():
            self.turn_on(port_name)
    
    def turn_off_all(self):
        for port_name in self.ports.keys():
            self.turn_off(port_name)
    
    def measure_i(self, port_name):
        supply = self.supplies[self.ports[port_name][0]]
        channel = self.ports[port_name][1]
        i = supply.query(f'MEAS:CURR? CH{channel}')
        time.sleep(0.05)
        return round(float(i),4)
    
    def measure_v(self, port_name):
        supply = self.supplies[self.ports[port_name][0]]
        channel = self.ports[port_name][1]
        v = supply.query(f'MEAS:VOLT? CH{channel}')
        time.sleep(0.05)
        return round(float(v),4)
    
    def measure_p(self, port_name):
        supply = self.supplies[self.ports[port_name][0]]
        channel = self.ports[port_name][1]
        p = supply.query(f'MEAS:POWE? CH{channel}')
        time.sleep(0.05)
        return round(float(p),4)
    
    def measure_f(self, channel):
        f = self.osc.query(f'C{channel}:PAVA? FREQ')[13:-3]
        time.sleep(0.05)
        return float(f)
    
    def autoset(self):
        self.osc.write('ASET')
        time.sleep(5)
    
    def close(self):
        self.rm.close()
