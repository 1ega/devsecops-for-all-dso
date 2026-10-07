"""Scanner adapters named by tools/dso/plugins.json.

Each adapter module defines:

- ``OPTIONS``: profile option names mapped to ``'file'`` or ``'dirs'`` (trusted kit paths).
- ``policy_files(options, root)``: trusted files that decide what the scanner reports.
- ``prepare(ctx)``: write the scanner's configuration into ``ctx.config_host``.
- ``command(ctx)``: scanner arguments after the executable or image command.
- ``parse(data, plugin, source)``: allowlisted findings from the scanner's JSON report.

An adapter may also define ``preflight(ctx)`` to reject input the scanner would
silently skip. The core runs, sandboxes, times out and validates every plugin the
same way; adapters never see credentials, the network policy or the report.
"""
