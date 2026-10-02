# Restic: backups and a restore drill

**Version covered:** 0.19.1. **License:** BSD-2-Clause.
[Upstream/releases](https://github.com/restic/restic/releases/tag/v0.19.1) ·
[Manual](https://restic.readthedocs.io/en/stable/).

Restic provides encrypted file backups. It is useful for a small company that
needs a documented backup and restore path. Use provider-native database backups
or a consistent database export alongside it; copying live database files is
not proof of a consistent backup.

## Install and run a local drill

Install the 0.19.1 package/release matching your OS and CPU from upstream. Verify
the release checksums and available signature using the release instructions;
record artifact and checksum. Confirm `restic version` reports 0.19.1.
The following creates only synthetic data in a temporary local repository:

```bash
drill_dir="$(mktemp -d)"
mkdir -p "$drill_dir/source" "$drill_dir/restore"
printf 'synthetic recovery fixture\n' > "$drill_dir/source/test.txt"
umask 077
openssl rand -base64 32 > "$drill_dir/password"
export RESTIC_REPOSITORY="$drill_dir/repository"
export RESTIC_PASSWORD_FILE="$drill_dir/password"
restic init
restic backup "$drill_dir/source"
restic snapshots --json > "$drill_dir/snapshots.json"
restic check --read-data
restic restore latest --target "$drill_dir/restore"
cmp "$drill_dir/source/test.txt" "$drill_dir/restore${drill_dir}/source/test.txt"
```

Restored absolute paths are rooted under `--target`. The final `cmp` must succeed;
keep the snapshot ID, start/end times and measured integrity result. Remove this
temporary drill directory when its evidence has been retained privately.

## Adopt for production

Record data scope, RPO/RTO, schedule, retention, owner and alert destination.
Use a secret manager for repository credentials/passwords; separate writer
access from retention/deletion and keep offline recovery material. Choose an
offsite or separately administered backend; test its retention/immutability
behavior rather than assuming encryption prevents deletion by a stolen writer.

Schedule backup and failure alerts with your existing scheduler. Record exit
codes and snapshot age; a successful command with missing business data is
insufficient. Test `check` and a sampled/full data verification suited to size.
Review retention in dry-run before applying prune/forget policies. Restore to
an isolated destination and validate a business flow using the
[restore playbook](../playbooks/restore-drill.md). Link results to `BKP-01/02`.

Sources: [backup](https://restic.readthedocs.io/en/stable/040_backup.html),
[restore](https://restic.readthedocs.io/en/stable/050_restore.html) and
[repository checks](https://restic.readthedocs.io/en/stable/045_working_with_repos.html).
