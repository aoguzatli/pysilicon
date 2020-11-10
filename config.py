class Config:
    running_pynq = False
    running_cocotb = not running_pynq
    inv_outs = running_pynq
    _ns = 1000
    T_default = int(10 * _ns)
