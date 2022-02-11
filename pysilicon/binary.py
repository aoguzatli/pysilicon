import random, copy, math, collections


def rand_binary_str(length):
    out = ''
    for i in range(length):
        out = out + str(random.randint(0, 1)) 
    return out

def rm_header(b):
    if b.startswith("0b"):
        return b[2:]
    else:
        return b

def onehot(val, num_bits):
    if is_bin(val):
        val = int(val, 2)

    assert val <= num_bits, 'Val must be less than or equal to num_bits'

    out = ['0'] * num_bits
    out[val] = '1'
    return ''.join(out[::-1])

def bitblast(bits):
    return list(bits)[::-1]

def bitmerge(arr):
    return ''.join(arr[::-1])

def hex2bin(hex_val):
    bin_val = ''

    for char in hex_val:
        if char in ['x', 'X']:
            bin_val = bin_val + 'x'
        elif char in ['z', 'Z']:
            bin_val = bin_val + 'z'
        else:
            bin_val = bin_val + bin(int(char, 16))[2:].zfill(4)

    return bin_val.lower()

def bin2hex(bin_val):
    hex_val = ''
    num_hex_digits = math.ceil(len(bin_val)/4)
    bin_val = bin_val.zfill(num_hex_digits*4)

    for i in range(0, len(bin_val), 4):
        bin_quad = bin_val[i:i+4]

        if 'x' in bin_quad or 'X' in bin_quad:
            hex_val = hex_val + 'x'
        elif 'z' in bin_quad or 'Z' in bin_quad:
            hex_val = hex_val + 'z'
        else:
            hex_val = hex_val + hex(int(bin_val[i:i+4], 2))[2:]

    return hex_val.lower()

def as_bin(n, width = None):
    out = rm_header(bin(int(n)))
    if width:
        assert len(out) <= width, f'as_bin: {n} contains more bits than the requested width ({width})'
        out = out.zfill(width)
    return out

def is_bin(n):
    return isinstance(n, str) and all([bit in ['0', '1'] for bit in n])

def as_int(b, invalid = -9999):
    if b.startswith("b'"):
        b = b[2:]

    if all([bit in ['0', '1'] for bit in b]):
        return int(b, 2)
    else:
        return invalid

def as_sint(b, invalid = -9999):
    b = rm_header(b)

    if all([bit in ['0', '1'] for bit in b]):
        if b[0] == '1':
            return (int(inv(b), 2) + 1) * -1
        else:
            return int(b, 2)
    else:
        return invalid

def inv(n):
    n = rm_header(n)
    out = ''
    for bit in n:
        if bit == '1':
            out = out + '0'
        elif bit == '0':
            out = out + '1'
        else:
            print('inv: Not a binary string!')
    return out

def onehot(n, width):
    out = ['0'] * width
    out[n] = '1'
    return ''.join(out[::-1])

def randbits(length):
    out = ''
    for i in range(length):
        out = out + str(random.randint(0, 1))

    return out

def log2up(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return math.ceil(math.log2(n))

def diff(a, b):
    if(len(a) != len(b)):
        print('lengths are different')
        l = min(len(a), len(b))
    else:
        l = len(a)

    for i in range(l):
        if(a[i] != b[i]):
            print(i, a[i], b[i])

def rotating_equals(a, b):
    length = len(a)
    b = collections.deque(b)
    a = collections.deque(a)
    for i in range(1, length):
        if list(a) == list(b):
            return True
        b.rotate(1)

    return False
