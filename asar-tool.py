#!/usr/bin/env python3
import fnmatch, json, os, stat, struct, sys


def _read_header(path):
    with open(path, 'rb') as f:
        f.read(4)
        pickle_size = struct.unpack('<I', f.read(4))[0]
        buf = f.read(pickle_size)
    json_len = struct.unpack('<I', buf[4:8])[0]
    return json.loads(buf[8:8 + json_len]), 8 + pickle_size


def extract(asar, dest):
    header, data_start = _read_header(asar)
    unpacked_dir = asar + '.unpacked'

    def walk(node, base):
        for name, info in node.get('files', {}).items():
            full = os.path.join(base, name)
            if 'files' in info:
                os.makedirs(full, exist_ok=True)
                walk(info, full)
            elif 'link' in info:
                os.makedirs(os.path.dirname(full), exist_ok=True)
                if os.path.lexists(full):
                    os.remove(full)
                os.symlink(info['link'], full)
            elif info.get('unpacked'):
                rel = os.path.relpath(full, dest)
                src = os.path.join(unpacked_dir, rel)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(src, 'rb') as s, open(full, 'wb') as d:
                    d.write(s.read())
                if info.get('executable'):
                    os.chmod(full, os.stat(full).st_mode | 0o111)
            else:
                offset = int(info.get('offset', '0'))
                size = info.get('size', 0)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(asar, 'rb') as f:
                    f.seek(data_start + offset)
                    data = f.read(size)
                with open(full, 'wb') as out:
                    out.write(data)
                if info.get('executable'):
                    os.chmod(full, os.stat(full).st_mode | 0o111)

    os.makedirs(dest, exist_ok=True)
    walk(header, dest)


def pack(src_dir, dest_asar, unpack_glob=''):
    file_list = []
    tree = {}
    offset = 0

    def scan(directory, node):
        nonlocal offset
        node['files'] = {}
        for name in sorted(os.listdir(directory)):
            full = os.path.join(directory, name)
            rel = os.path.relpath(full, src_dir)
            info = {}
            if os.path.islink(full):
                info['link'] = os.readlink(full)
            elif os.path.isdir(full):
                scan(full, info)
            else:
                fstat = os.stat(full)
                size = fstat.st_size
                is_exe = bool(fstat.st_mode & stat.S_IXUSR)
                should_unpack = unpack_glob and fnmatch.fnmatch(name, unpack_glob)
                if should_unpack:
                    info = {'size': size, 'unpacked': True}
                    if is_exe:
                        info['executable'] = True
                    unpack_dest = os.path.join(dest_asar + '.unpacked', rel)
                    os.makedirs(os.path.dirname(unpack_dest), exist_ok=True)
                    with open(full, 'rb') as f, open(unpack_dest, 'wb') as d:
                        d.write(f.read())
                else:
                    info = {'offset': str(offset), 'size': size}
                    if is_exe:
                        info['executable'] = True
                    with open(full, 'rb') as f:
                        file_list.append(f.read())
                    offset += size
            node['files'][name] = info

    scan(src_dir, tree)

    hdr = json.dumps(tree, separators=(',', ':')).encode()
    padded = (len(hdr) + 3) & ~3
    payload = struct.pack('<I', len(hdr)) + hdr + b'\x00' * (padded - len(hdr))
    pickle = struct.pack('<I', len(payload)) + payload
    outer = struct.pack('<I', 4) + struct.pack('<I', len(pickle))

    with open(dest_asar, 'wb') as f:
        f.write(outer)
        f.write(pickle)
        for data in file_list:
            f.write(data)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'e':
        extract(sys.argv[2], sys.argv[3])
    elif cmd == 'p':
        unpack = sys.argv[sys.argv.index('--unpack') + 1] if '--unpack' in sys.argv else ''
        pack(sys.argv[2], sys.argv[3], unpack)
    else:
        sys.exit(f'usage: {sys.argv[0]} e <asar> <dest> | p <src> <dest.asar> [--unpack <glob>]')
