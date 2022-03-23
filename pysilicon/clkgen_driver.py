import random, copy, math
from .binary import *
from .scan_driver import Scanner
from .config import Config
from .essentials import *

if Config.running_cocotb:
    import cocotb

class Clkgen:

    def __init__(self, chain):
        self.interface = interface
        self.chain = chain

    def set_fast_clk(division = 7, oscillator = 1, block = None):
        if block is None:
            blk = '111111'
        else:
            blk = bin(2 ** block)[2:].zfill(6)
        div = bin(2 ** division)[2:].zfill(14)
        osc = bin(2 ** oscillator)[2:].zfill(12)
        bits = blk + div + osc

        write_signal(interface['sel_clk_extern'], 1)
        write_signal(interface['global_en'], 0)
        write_signal(interface['en_common'], 0)

        if Config.running_cocotb:
            yield self.chain.scan_in(bits)
            out = yield self.chain.scan_out(bits)
        elif Config.running_pynq:
            self.chain.scan_in(bits)
            out = self.chain.scan_out(bits)
        assert out == bits, out

        write_signal(interface['global_en'], 1)
        write_signal(interface['en_common'], 1)
        write_signal(interface['sel_clk_extern'], 0)


    def set_slow_clk():
        write_signal(interface['sel_clk_extern'], 1)
        write_signal(interface['global_en'], 0)
        write_signal(interface['en_common'], 0)

        bits = ''.zfill(6+14+12)

        if Config.running_cocotb:
            yield self.chain.scan_in(bits)
            out = yield self.chain.scan_out(bits)
        elif Config.running_pynq:
            self.chain.scan_in(bits)
            out = self.chain.scan_out(bits)
        assert out == bits, out

    set_fast_clk = Config.default_decorator(set_fast_clk)
    set_slow_clk = Config.default_decorator(set_slow_clk)
