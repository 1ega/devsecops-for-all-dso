# osquery: endpoint inventory and investigation

**Version covered:** 5.23.1. **License:** Apache-2.0.
[Upstream/releases](https://github.com/osquery/osquery/releases/tag/5.23.1) ·
[Documentation](https://osquery.readthedocs.io/en/stable/).

osquery exposes operating-system state as SQL tables. Use it to investigate
users, running processes and listening ports on managed endpoints. It is not
an automatic malware-blocking engine or a substitute for device management.

## Install and inspect

Deploy the upstream 5.23.1 package matching the OS through your package/device
manager, verifying the published artifact/checksum/signature. Check
`osqueryi --version`; test one representative OS before broad enrollment.

```bash
osqueryi --json 'SELECT uid, username, directory, shell FROM users;'
osqueryi --json 'SELECT pid, name, path, uid FROM processes;'
osqueryi --json 'SELECT pid, port, protocol, address FROM listening_ports;'
```

Tables and permissions differ by OS. Preserve collection time, host and owner;
restrict results because account and process metadata can identify people.
Do not interpret an empty/permission-denied query as a clean endpoint.

## Schedule and collect

Use the [starter config](../scanners/osquery/osquery.conf.example) in a private
copy. Validate with `osqueryi --config_path PATH --config_check`, then manage
`osqueryd` with your OS service/device tooling. The example writes filesystem
logs; configure rotation, retention and a authenticated collector separately.
Observe CPU, differential results, failed queries and offline agents.

For a remote deployment use a documented TLS enrollment/config/logging service,
restricted enrollment credentials and a verified server trust chain. Separate
operator roles and audit remote query access. Avoid logging broad command-line
data without a privacy/data-retention decision. Process-event collection needs
additional OS-specific audit configuration and performance testing.

Acceptance: a known test user/process appears, a failed query is visible,
results reach controlled storage and a missing agent alerts the owner. Link
coverage to `END-01/02`; combine with MDM/encryption/patch/EDR evidence.
Sources: [remote deployment](https://osquery.readthedocs.io/en/stable/deployment/remote/)
and [process auditing](https://osquery.readthedocs.io/en/stable/deployment/process-auditing/).
