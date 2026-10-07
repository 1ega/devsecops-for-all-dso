"""Grype image: package vulnerabilities of an image pulled by digest straight from its registry."""
from __future__ import annotations

from plugins.grype import environment, parse, prepare  # noqa: F401 (same configuration and report format)

OPTIONS = {}


def policy_files(options, root):
    return []


def command(ctx):
    # registry: reads the image from its registry without a Docker daemon.
    return ['registry:' + ctx.source, '--config', ctx.config + '/grype.yaml', '--output', 'json',
            '--file', ctx.output, '--quiet']
