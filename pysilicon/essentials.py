from .config import Config
import random, copy, math, time
from .binary import *

if Config.running_cocotb:
    import cocotb
    from cocotb.triggers import Timer
    from cocotb.result import TestFailure
    from cocotb.binary import BinaryValue
    from cocotb.clock import Clock
    from cocotb.triggers import FallingEdge, RisingEdge

def read_signal(obj):
    if Config.running_cocotb:
        if type(obj) is list:
            return ''.join([str(wire.value) for wire in obj][::-1])
        else:
            return str(obj.value)
    elif Config.running_pynq:
        if type(obj) is list:
            return ''.join([str(wire.read()) for wire in obj][::-1])
        else:
            return str(obj.read())

def write_signal(obj, val):
    if Config.running_cocotb:
        if type(obj) is list:
            bits = as_bin(val, len(obj))
            for wire, bit in zip(obj, bits[::-1]):
                wire <= int(bit)
        else:
            obj <= val
    elif Config.running_pynq:
        if type(obj) is list:
            bits = as_bin(val, len(obj))
            for wire, bit in zip(obj, bits[::-1]):
                wire.write(int(bit))
        else:
            obj.write(val)

def cycle(clock, T = Config.T_default, clk_running = False):
    if Config.running_cocotb:
        if clk_running:
            yield RisingEdge(clock)
            yield FallingEdge(clock)
        else:
            halfT = int(T/2)
            yield Timer(halfT)
            clock <= int(not (int(clock)))
            yield Timer(halfT)
            clock <= int(not (int(clock)))
    elif Config.running_pynq:
        clock.on()
        clock.off()

def cycles(clock, n, T = Config.T_default, clk_running = False):
    if Config.running_cocotb:
        for i in range(n):
            yield cycle(clock, T, clk_running)
    elif Config.running_pynq:
        for i in range(n):
            cycle(clock, T, clk_running)

def wait_for_val(signal, val, clock, clk_running = True, T = Config.T_default, timeout = 5000, read_func = read_signal):
    for i in range(timeout):
        if(read_func(signal) == val):
            return
        else:
            if Config.running_cocotb:
                yield cycle(clock, T)
            elif Config.running_pynq:
                cycle(clock, T)

    assert False, 'Wait timed out!'

# These two functions are only for pynq
if Config.running_pynq:
    def rising_edge(signal):
        while(signal.read() == 0):
            time.sleep(0.001)

    def falling_edge(signal):
        while(signal.read() == 1):
            time.sleep(0.001)

cycle = Config.default_decorator(cycle)
cycles = Config.default_decorator(cycles)
wait_for_val = Config.default_decorator(wait_for_val)
