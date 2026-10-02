import subprocess


def unsafe(command):
    # ruleid: python-subprocess-shell-true
    subprocess.run(command, shell=True)
    # ruleid: python-subprocess-shell-true
    subprocess.Popen(command, shell=True)


def safe(argument):
    # ok: python-subprocess-shell-true
    subprocess.run(["echo", argument], check=True)
