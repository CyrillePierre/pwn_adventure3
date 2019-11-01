import struct
import binascii

jump_state = 0
walk_state = 0

def raw(data):
    s = '{} raw['.format(data[:2].decode())
#    s += str(data)
    for b in data[2:]:
        s += '{:02x} '.format(b)
    s = s[:-1] + ']'
    return s, b''


def move(data, offset=2):
    x,y,z, hp,hy,hr, mx,my = struct.unpack_from('fffhhhbb', data, offset)

    # movement buttons
    bx = ['b', ' ', 'f'][int(mx/127) + 1]
    by = ['l', ' ', 'r'][int(my/127) + 1]
    bj = 'j' if jump_state else ' '
    bw = 'w' if walk_state else ' '

    roll = hr * 180. / 32768
    pitch = hp * 180. / 32768
    yaw = hy * 180. / 32768

    s = '{} pos[{:6.0f}{:6.0f}{:6.0f}]  rpy[{:7.1f}{:7.1f}{:7.1f}]  btn[{}{}{}{}]'.format(
            data[:2].decode(), x,y,z, roll,pitch,yaw, bx,by,bj,bw)
    return s, data[22:]


def jump(data):
    global jump_state
    jump_state = data[2]
    return '', data[3:]


def run(data):
    global walk_state
    walk_state = not data[2]
    return '', data[3:]


def parse(name, data):
    cases = { 
        b'\0\0': (0, lambda x: ('ok', b'')),
        b'mv': (1, move),
        b'jp': (0, jump),
        b'rn': (0, run),
    }
    default = (0, raw)
    
    msgs = []
    while len(data):
        enabled, fn = cases.get(data[:2], default)
        s, data = fn(data)
        if enabled: msgs.append(s)

    if len(msgs):
        print('[{}] '.format(name).join(msgs))
