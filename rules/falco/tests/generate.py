#!/usr/bin/env python3
"""Generate harmless rule triggers only INSIDE the disposable smoke container.

No network targets, real secrets, host mounts or system services are used.
"""
import ctypes
import os
import pty
import shutil
import socket
import subprocess
import sys
from pathlib import Path


def execute(path):
    subprocess.run([str(path)], check=False, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


if len(sys.argv) != 2 or sys.argv[1] not in {"positive", "negative"}:
    sys.exit("Usage: generate.py positive|negative (disposable test container only)")
if sys.argv[1] == "negative":
    Path('/tmp/dso-public.txt').write_text('public fixture')
    Path('/tmp/dso-public.txt').read_text()
    execute('/usr/bin/true')
    sys.exit(0)

# Event-based rules examine successful exec/open calls, not program exit codes.
for name in ('apt', 'nmap', 'xmrig', 'su'):
    target = Path('/usr/local/bin') / name
    shutil.copy('/usr/bin/true', target)
    execute(target)
shutil.copy('/usr/bin/true', '/tmp/dso-test')
execute('/tmp/dso-test')

for name in ('/root/.aws/credentials',
             '/var/run/secrets/kubernetes.io/serviceaccount/token'):
    target = Path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('DSO dummy; not a credential')
    subprocess.run(['/usr/bin/cat', name], stdout=subprocess.DEVNULL, check=True)

for name in ('/tmp/dso-home/.ssh/authorized_keys', '/etc/cron.d/dso-test', '/etc/gshadow'):
    target = Path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('DSO dummy test')
Path('/var/log/auth.log').write_text('DSO dummy log')
Path('/var/log/auth.log').unlink()

with socket.socket(socket.AF_UNIX) as server, socket.socket(socket.AF_UNIX) as client:
    server.bind('/run/docker.sock')  # Dummy socket in this container's own filesystem.
    server.listen(1)
    client.connect('/run/docker.sock')

pid, terminal = pty.fork()
if pid == 0:
    os.execl('/bin/sh', 'sh', '-c', 'true')
os.waitpid(pid, 0)
os.close(terminal)

libc = ctypes.CDLL(None, use_errno=True)
pid = os.fork()
if pid == 0:
    libc.prctl(15, b'nginx', 0, 0, 0)  # Set only our dummy parent's process name.
    subprocess.run(['/bin/sh', '-c', 'true'], check=True)
    os._exit(0)
os.waitpid(pid, 0)

pid = os.fork()
if pid == 0:
    descriptor = os.memfd_create('dso-fixture', 0)
    with open('/usr/bin/true', 'rb') as source:
        os.write(descriptor, source.read())
    os.execve(descriptor, ['dso-memory-test'], {})
os.waitpid(pid, 0)

pid = os.fork()
if pid == 0:
    result = libc.ptrace(0, 0, None, None)  # PTRACE_TRACEME; trace only ourselves.
    os._exit(0 if result == 0 else 1)
_, status = os.waitpid(pid, 0)
if os.waitstatus_to_exitcode(status) != 0:
    sys.exit('Sandbox denied PTRACE_TRACEME; positive test incomplete')
