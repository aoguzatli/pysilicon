import os

class Config:
    running_pynq = 'xilinx' in os.getcwd()
    running_cocotb = not running_pynq
    inv_outs = False
    _ns = 1000
    T_default = int(10 * _ns)

    def aslist(generator):
        "Function decorator to transform a generator into a list"
        def wrapper(*args, **kwargs):
            try:
                next(generator(*args, **kwargs))
            except StopIteration as ex:
                return ex.value
        return wrapper

    if running_cocotb:
        import cocotb
        default_decorator = cocotb.coroutine
    else:
        default_decorator = aslist
