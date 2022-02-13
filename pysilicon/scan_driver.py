from .config import Config
import random, copy, math, time
from .binary import *
from .essentials import *

if Config.running_cocotb:
    import cocotb
    from cocotb.triggers import Timer
    from cocotb.result import TestFailure
    from cocotb.binary import BinaryValue
    from cocotb.clock import Clock
    from cocotb.triggers import FallingEdge, RisingEdge


class Scanner:

    def __init__(self, T = Config.T_default, interface = None, scan_clk = None, scan_in = None, scan_out = None,
        scan_en = None, scan_wen = None, fromMSB = False, verbosity = 0, clk_running = False,
        clk_b = False, length = None, read_func = read_signal, scan_in_width = 1):

        if interface is None:
            self._scan_in = scan_in
            self._scan_clk = scan_clk
            self._scan_en = scan_en
            self._scan_out = scan_out
            self._scan_wen = scan_wen
        else:
            self._scan_in = interface.get('scan_in')
            self._scan_clk = interface.get('scan_clk')
            self._scan_en = interface.get('scan_en')
            self._scan_out = interface.get('scan_out')
            self._scan_wen = interface.get('scan_wen')

        self.T = T
        self.fromMSB = fromMSB
        self.verbosity = verbosity
        self.clk_running = clk_running
        self.clk_b = clk_b
        self.length = length
        self.read_func = read_func
        self.scan_in_width = scan_in_width

        self.halfT = int(T/2)
        self.quarterT = int(T/4)

    def scan_in(self, val, T = None, scan_clk = None, scan_in = None, scan_out = None,
        scan_en = None, scan_wen = None, fromMSB = None, verbosity = None, clk_running = None,
        clk_b = None, read_func = None):

        if T is None:
            T = self.T
            halfT = self.halfT
            quarterT = self.quarterT
        else:
            halfT = int(T/2)
            quarterT = int(T/4)

        if scan_clk is None:
            scan_clk = self._scan_clk
        if scan_in is None:
            scan_in = self._scan_in
        if scan_out is None:
            scan_out = self._scan_out
        if scan_en is None:
            scan_en = self._scan_en
        if scan_wen is None:
            scan_wen = self._scan_wen
        if fromMSB is None:
            fromMSB = self.fromMSB
        if verbosity is None:
            verbosity = self.verbosity
        if clk_running is None:
            clk_running = self.clk_running
        if clk_b is None:
            clk_b = self.clk_b
        if read_func is None:
            read_func = self.read_func

        if self.length is not None and len(val) != self.length and verbosity > 0:
            print(f'Warning: number of scanned bits ({len(val)}) is not equal to the scan chain length ({self.length})')

        if fromMSB:
            val = val[::-1]
        
        # Pad and split val to account for >1 scan in width chains
        padding = ''.zfill((self.scan_in_width - len(val)) % self.scan_in_width)
        val = padding + val
        val = [val[i:i+self.scan_in_width] for i in range(0, len(val), self.scan_in_width)]

        if Config.running_cocotb:
            if clk_running:
                if clk_b:
                    yield RisingEdge(scan_clk)
                else:
                    yield FallingEdge(scan_clk)
            else:
                yield Timer(halfT)

        if scan_en is not None:
            if Config.running_cocotb and read_func(scan_en) == '1':
                print('ERROR: scan enable is high, another chain might be using the scan ports')
                return None
            else:
                write_signal(scan_en, 1)

        outstr = ''
        for i, v in enumerate(val):
            if scan_out is not None:
                outstr = outstr + read_func(scan_out).zfill(self.scan_in_width)

            if (verbosity == 3 and i%100 == 0) or (verbosity == 4 and i%10 == 0) or (verbosity > 4):
                print(f"Scanning bit {i*self.scan_in_width} out of {len(val)*self.scan_in_width-1}...")

            write_signal(scan_in, int(v, 2))

            if Config.running_cocotb:
                yield cycle(scan_clk, T, clk_running)
            else:
                cycle(scan_clk, T, clk_running)

        if fromMSB:
            outstr = [outstr[i:i+self.scan_in_width] for i in range(0, len(outstr), self.scan_in_width)]
            outstr = ''.join(outstr[::-1])
        
        outstr = outstr[:-len(padding)]

        if scan_en is not None:
            write_signal(scan_en, 0)

        if scan_wen is not None:
            write_signal(scan_wen, 1)
            if Config.running_cocotb:
                yield cycle(scan_clk, T, clk_running)
            else:
                cycle(scan_clk, T, clk_running)
            write_signal(scan_wen, 0)

        if Config.inv_outs:
            outstr = inv(outstr)

        return outstr

    def scan_out(self, num = None, T = None, scan_clk = None, scan_in = None, scan_out = None,
        scan_en = None, fromMSB = None, verbosity = None, clk_running = None, clk_b = None):

        if num is None:
            if self.length is None:
                print('ERROR: Please either set the scan chain length or give the number of bits')
            else:
                num = self.length

        if Config.running_cocotb:
            out = yield self.scan_in(''.zfill(num), T = T, scan_clk = scan_clk, scan_in = scan_in, scan_out = scan_out,
                scan_en = scan_en, fromMSB = fromMSB, verbosity = verbosity, clk_running = clk_running, clk_b = clk_b)
        else:
            out = self.scan_in(''.zfill(num), T = T, scan_clk = scan_clk, scan_in = scan_in, scan_out = scan_out,
                scan_en = scan_en, fromMSB = fromMSB, verbosity = verbosity, clk_running = clk_running, clk_b = clk_b)

        return out

    scan_in = Config.default_decorator(scan_in)
    scan_out = Config.default_decorator(scan_out)


class JTAG:

    def __init__(self, chains, confouts, interface = None, T = Config.T_default, jtag_clk = None, jtag_in = None,
                jtag_out = None, jtag_en = None, jtag_load = None, scan_clk = None, scan_in = None, scan_out = None,
                scan_en = None, fromMSB = False, read_func = read_signal):

        if hasattr(chains, '__iter__'):
            self.chains = chains
            self.num_chains = len(chains)
        else:
            self.chains = []
            self.num_chains = chains

        self.confouts = confouts
        self.num_confouts = len(confouts)
        self.read_func = read_func

        if interface is None:
            self._jtag_in = jtag_in
            self._jtag_clk = jtag_clk
            self._jtag_load = jtag_load
            self._jtag_out = jtag_out
            self._jtag_en = jtag_en
            self._scan_in = scan_in
            self._scan_clk = scan_clk
            self._scan_en = scan_en
            self._scan_out = scan_out
        else:
            self._jtag_in = interface['jtag_in']
            self._jtag_clk = interface['jtag_clk']
            self._jtag_load = interface['jtag_load']
            self._jtag_out = interface['jtag_out']
            self._jtag_en = interface['jtag_en']
            self._scan_in = interface['scan_in']
            self._scan_clk = interface['scan_clk']
            self._scan_en = interface['scan_en']
            self._scan_out = interface['scan_out']

        self.T = T
        self.halfT = int(T/2)
        self.fromMSB = fromMSB

        self.num_chain_bits = log2up(self.num_chains)
        self.current_chain_bits = ''.zfill(self.num_chain_bits)
        self.current_confouts = ''.zfill(self.num_confouts)
        self.width = self.num_chain_bits + self.num_confouts

        self.jtag_scan_chain = Scanner(T = T, scan_clk = jtag_clk, scan_in = jtag_in, scan_out = jtag_out,
            scan_en = jtag_en, scan_wen = jtag_load, fromMSB = fromMSB, verbosity = 0, clk_running = False,
            clk_b = False, length = self.width, read_func = self.read_func)

    def set_chain(self, chain):
        if isinstance(chain, Scanner):
            chain_num = self.chains.index(chain)
        else:
            chain_num = chain

        assert chain_num < self.num_chains, 'Chain number greater than the number of chains in JTAG!'

        selected_chain_bits = bin(chain_num)[2:].zfill(self.num_chain_bits)
        val = self.current_confouts + selected_chain_bits

        assert(len(val) == self.width)

        if Config.running_cocotb:
            outstr = yield self.jtag_scan_chain.scan_in(val)
        else:
            outstr = self.jtag_scan_chain.scan_in(val)
        self.current_chain_bits = selected_chain_bits

        return outstr

    def set_confouts(self, confouts):
        confs = list(self.current_confouts)[::-1]
        for key, value in confouts.items():
            assert key in self.confouts, f'The config signal {key} not defined in the JTAG initialization.'
            confs[self.confouts.index(key)] = value

        val = ''.join(confs[::-1]) + self.current_chain_bits
        assert(len(val) == self.width)

        if Config.running_cocotb:
            outstr = yield self.jtag_scan_chain.scan_in(val)
        else:
            outstr = self.jtag_scan_chain.scan_in(val)
        self.current_confouts = ''.join(confs[::-1])

        return outstr

    def scan_in(self, val):
        chain = int(self.current_chain_bits, 2)
        clk = None
        if self.chains[chain]._scan_clk is None:
            clk = self._scan_clk

        if Config.running_cocotb:
            out = yield self.chains[chain].scan_in(val, T = self.T, scan_in = self._scan_in, scan_en = self._scan_en, scan_out = self._scan_out, scan_clk = clk, read_func = self.read_func)
        else:
            out = self.chains[chain].scan_in(val, T = self.T, scan_in = self._scan_in, scan_en = self._scan_en, scan_out = self._scan_out, scan_clk = clk, read_func = self.read_func)

        return out

    def scan_out(self, num = None):
        chain = int(self.current_chain_bits, 2)
        clk = None
        if self.chains[chain]._scan_clk is None:
            clk = self._scan_clk

        if Config.running_cocotb:
            out = yield self.chains[chain].scan_out(num, T = self.T, scan_in = self._scan_in, scan_en = self._scan_en, scan_out = self._scan_out, scan_clk = clk)
        else:
            out = self.chains[chain].scan_out(num, T = self.T, scan_in = self._scan_in, scan_en = self._scan_en, scan_out = self._scan_out, scan_clk = clk)

        return out

    def select_and_scan_in(self, chain, val):
        if Config.running_cocotb:
            yield self.set_chain(chain)
            out = yield self.scan_in(val)
        else:
            self.set_chain(chain)
            out = self.scan_in(val)
        return out

    def select_and_scan_out(self, chain, num = None):
        if Config.running_cocotb:
            yield self.set_chain(chain)
            out = yield self.scan_out(num)
        else:
            self.set_chain(chain)
            out = self.scan_out(num)
        return out

    def self_test(self):
        in_chain = rand_binary_str(self.num_chain_bits)
        while int(in_chain, 2) >= self.num_chains:
            in_chain = rand_binary_str(self.num_chain_bits)
        in_confouts = rand_binary_str(self.num_confouts)
        ins = in_confouts + in_chain

        scan_wen = self.jtag_scan_chain._scan_wen
        self.jtag_scan_chain._scan_wen = None
        if Config.running_cocotb:
            prev = yield self.jtag_scan_chain.scan_in(ins, scan_wen = None)
            out = yield self.jtag_scan_chain.scan_in(ins, scan_wen = None)
        else:
            prev = self.jtag_scan_chain.scan_in(ins, scan_wen = None)
            out = self.jtag_scan_chain.scan_in(ins, scan_wen = None)

        self.jtag_scan_chain._scan_wen = scan_wen

        if ins != out:
            print(f'ERROR: JTAG chain failed self test! in: {ins}, out: {out}')
        else:
            print('JTAG chain: pass')

        for i, chain in enumerate(self.chains):
            if chain.length is None:
                print(f'Warning: The length of chain {i} is unknown!')
            else:
                ins = rand_binary_str(chain.length)
                if Config.running_cocotb:
                    prev = yield self.select_and_scan_in(chain, ins)
                    out = yield self.select_and_scan_out(chain)
                else:
                    prev = self.select_and_scan_in(chain, ins)
                    out = self.select_and_scan_out(chain)

                if ins != out:
                    print(f'ERROR: Chain {i} failed JTAG self test!')
                    print(f'Expected: {ins}')
                    print(f'Obtained: {out}')
                else:
                    print(f'Scan chain {i}: pass')

    set_confouts = Config.default_decorator(set_confouts)
    set_chain = Config.default_decorator(set_chain)
    scan_in = Config.default_decorator(scan_in)
    scan_out = Config.default_decorator(scan_out)
    select_and_scan_in = Config.default_decorator(select_and_scan_in)
    select_and_scan_out = Config.default_decorator(select_and_scan_out)
    self_test = Config.default_decorator(self_test)


if Config.running_pynq:

    class MMIOScanner:
        def __init__(self, T = Config.T_default, interface = None, fromMSB = False):
            self.T = T
            self.interface = interface
            self.fromMSB = fromMSB
            self.num_bits = None
            self.num_rows = None

        def reset(self):
            self.interface['reset'].on()
            self.interface['valid'].off()
            self.interface['num_bits'].write(0, int('001111111111111111', 2))
            self.interface['reset'].off()

        def set_data(self, data):
            self.num_bits = len(data)
            self.num_rows = math.ceil(num_bits/32)
            slack = num_rows*32 - self.num_bits
            assert(self.num_rows <= 2048)

            if self.fromMSB:
                data = data[::-1]

            for i in range(num_rows-1):
                self.interface['mmio_scan_in'].write(offset=i*4, data = int(data[32*i:32*(i+1)][::-1], 2))

            last_line = int(data[32*(self.num_rows-1):][::-1].zfill(32), 2)
            self.interface['mmio_scan_in'].write(offset=(num_rows-1)*4, data=last_line)
            self.interface['num_bits'].write(self.num_bits, int('001111111111111111', 2))

        def scan_in(self, data = None):
            if data is not None:
                self.set_data(data)
            self.interface['valid'].on()
            time.sleep(0.001)
            self.interface['valid'].off()
            rising_edge(self.interface['ready'])

        def scan_out(self):
            out_data = ''
            array = list(self.interface['mmio_scan_out'].array)
            for i in range(num_rows-1):
                out_data = out_data + bin(array[(i+1)%2048])[2:].zfill(32)[::-1]

            last_line = bin(array[self.num_rows%2048])[2:].zfill(32)[::-1][slack:]
            out_data = out_data + last_line

            if self.fromMSB:
                out_data = out_data[::-1]

            return out_data
