#!/usr/bin/env python3
"""Publish a CI artifact without following a caller-controlled reports symlink."""
import os
from pathlib import Path
import sys
import uuid


def publish(source, directory):
    directory = Path(directory)
    directory.mkdir(mode=0o700, exist_ok=True)
    descriptor = os.open(directory, os.O_DIRECTORY | os.O_NOFOLLOW | os.O_RDONLY)
    name = '.dso-' + uuid.uuid4().hex
    try:
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=descriptor)
        with os.fdopen(fd, 'wb') as output, Path(source).open('rb') as stream:
            while block := stream.read(1024 * 1024):
                output.write(block)
        os.replace(name, 'dso.json', src_dir_fd=descriptor, dst_dir_fd=descriptor)
    finally:
        try:
            os.unlink(name, dir_fd=descriptor)
        except FileNotFoundError:
            pass
        os.close(descriptor)


if __name__ == '__main__':
    try:
        publish(sys.argv[1], sys.argv[2])
    except (OSError, ValueError, IndexError):
        print('DSO: cannot safely publish report into reports directory', file=sys.stderr)
        sys.exit(2)
