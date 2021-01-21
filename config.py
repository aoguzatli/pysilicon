class Config:
    running_pynq = False
    running_cocotb = not running_pynq
    inv_outs = running_pynq
    _ns = 1000
    T_default = int(10 * _ns)

    def aslist(generator):
        "Function decorator to transform a generator into a list"
        def wrapper(*args, **kwargs):
            return list(generator(*args, **kwargs))
        return wrapper

    if running_cocotb:
        import cocotb
        default_decorator = cocotb.coroutine
    else:
        default_decorator = aslist
