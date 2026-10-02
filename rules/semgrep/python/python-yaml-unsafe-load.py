import yaml


def unsafe(content):
    # ruleid: python-yaml-unsafe-load
    yaml.unsafe_load(content)
    # ruleid: python-yaml-unsafe-load
    yaml.load(content, Loader=yaml.Loader)


def safe(content):
    # ok: python-yaml-unsafe-load
    yaml.safe_load(content)
