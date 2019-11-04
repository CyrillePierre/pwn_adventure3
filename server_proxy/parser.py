import struct
import binascii

jump_state = 0
walk_state = 0


def raw_str(data):
    s = 'raw['
    for b in data:
        s += '{:02x} '.format(b)
    return s[:-1] + ']'


def unknown(data):
    s = '{} {}'.format(data[:2], data[2:])
    return s, b''


def move(data):
    x,y,z, hp,hy,hr, mx,my = struct.unpack_from('<3f3h2b', data, 2)

    # movement buttons
    bx = ['b', ' ', 'f'][int(mx/127) + 1]
    by = ['l', ' ', 'r'][int(my/127) + 1]
    bj = 'j' if jump_state else ' '
    bw = 'w' if walk_state else ' '

    roll = hr * 180. / 32768
    pitch = hp * 180. / 32768
    yaw = hy * 180. / 32768

    s = '{} pos[{:7.0f}{:7.0f}{:7.0f}]  rpy[{:7.1f}{:7.1f}{:7.1f}]  btn[{}{}{}{}]'.format(
            data[:2].decode(), x,y,z, roll,pitch,yaw, bx,by,bj,bw)
    return s, data[22:]


def jump(data):
    global jump_state
    jump_state = data[2]
    return 'jp [{}]'.format(jump_state), data[3:]


def run(data):
    global walk_state
    walk_state = not data[2]
    return '', data[3:]


def make(data):
    ind, _, str_len = struct.unpack_from('<QbH', data, 2)
    str_start = 13
    str_end = str_start + str_len
    name = data[str_start:str_end].decode()
    x,y,z = struct.unpack_from('<3f', data, str_end)

    s = '{}({:02d}) {:20s}[{:7.0f}{:7.0f}{:7.0f}] {}'.format(
        data[:2].decode(), ind, name, x,y,z, raw_str(data[str_end+12:str_end+22]))
    return s, data[str_end+22:]


def chat(data, name):
    if name[0] == 'c':
        msg_len, = struct.unpack_from('<H', data, 2)
        msg = data[4:4+msg_len].decode()
        s = '{} send: "{}"'.format(data[:2].decode(), msg)
        return s, data[4+msg_len:]

    else:
        nb, msg_len = struct.unpack_from('<IH', data, 2)
        msg = data[8:8+msg_len].decode()
        s = '{} chat: [{}] "{}"'.format(data[:2].decode(), nb, msg)
        return s, data[8+msg_len:]


def select_item(data, name):
    if name[0] == 'c':
        nb, = struct.unpack_from('<B', data, 2)
        s = '{} select item[{}]'.format(data[:2].decode(), nb)
        return s, data[3:]

    else:
        nb, = struct.unpack_from('<B', data, 2)
        s = '{} select item[{}]  {}'.format(data[:2].decode(), nb, raw_str(data[3:5]))
        return s, data[5:]


def active_item(data):
    name_len, p,y,r = struct.unpack_from('<H3I', data, 2)
    name_end = 4 + name_len
    name = data[4:name_end].decode()
#    s = '{} use[{}] rpy[{} {} {}]'.format(
#        data[:2].decode(), name, r,p,y)
    s = '{} use[{}] {}'.format(data[:2].decode(), name, raw_str(data[name_end:name_end+12]))
    return s, data[name_end+12:]


def parse(name, data):
    cases = { 
        b'\0\0': (0, lambda x: ('ok', b'')),
        b'mv': (0, move),
        b'jp': (1, jump),
        b'rn': (0, run),
        b'mk': (1, make),
        b'#*': (1, lambda x: chat(x, name)),
        b's=': (0, lambda x: select_item(x, name)),
        b'*i': (1, active_item)
    }
    default = (0, unknown)
    
    msgs = []
    while len(data):
        enabled, fn = cases.get(data[:2], default)
        s, data = fn(data)
        if enabled: msgs.append(s)

    if len(msgs):
        prefix = '[{}] '.format(name)
        sep = '\n' + prefix
        print(prefix, end='')
        print(sep.join(msgs))
