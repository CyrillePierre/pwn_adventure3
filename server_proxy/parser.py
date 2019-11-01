import struct
import binascii

def raw(data):
    s = 'raw: '
#    s += str(data)
    for b in data:
        s += '{:02x} '.format(b)
    return s


def pos(data):
    x,y,z, hp,hy,hr, mx,my = struct.unpack_from('fffhhhbb', data, 2)

    bx = ['b', ' ', 'f'][int(mx/127) + 1]
    by = ['l', ' ', 'r'][int(my/127) + 1]

    roll = hr * 180. / 32768
    pitch = hp * 180. / 32768
    yaw = hy * 180. / 32768

    s = 'pos[{:6.0f}{:6.0f}{:6.0f}]  rpy[{:7.1f}{:7.1f}{:7.1f}]  btn[{}{}]'.format(
        x,y,z, roll,pitch,yaw, bx,by)
    return s


def parse(name, data):
    cases = { 
        b'0000': (0, lambda x: 'ok'),
        b'6d76': (0, pos),
    }
    default = (1, raw)
    
    code = binascii.hexlify(data[:2])
    enabled, fn = cases.get(code, default)
    if enabled: 
        print('[{}] '.format(name), end='')
        print(fn(data))
