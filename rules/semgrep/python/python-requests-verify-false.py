import requests


def unsafe(url):
    # ruleid: python-requests-verify-false
    requests.get(url, verify=False)
    # ruleid: python-requests-verify-false
    requests.post(url, json={}, verify=False)


def safe(url):
    # ok: python-requests-verify-false
    requests.get(url, timeout=10)
