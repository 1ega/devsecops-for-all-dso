# dso: security baseline and exception checks

A dependency-free Python 3 entry point for private inventory, assessment and risk
registers. It validates owner-supplied evidence; it does not scan providers or
apply exceptions automatically.

```bash
cp baseline/assessment.example.json /private/path/assessment.json
cp baseline/assets.example.csv /private/path/assets.csv
python3 tools/dso/dso.py inventory --input /private/path/assets.csv
python3 tools/dso/dso.py assess --input /private/path/assessment.json --all
python3 tools/dso/dso.py exceptions --input /private/path/exceptions.json
python3 -m unittest discover -s tools/dso/tests -v
```

Refresh example dates before use. The sample intentionally contains gaps.
Assessment snapshots must be at most seven days old; implemented controls need
an owner, current review and nonempty text evidence. Exceptions require an asset,
rule, owner, approver, reason, compensating control, ticket and 1–90 day expiry.
Expiry on today's date already fails. Use `--format json` for machine output.

Exit codes: `0` valid/no gaps, `1` gaps/expired exceptions, `2` malformed input.
Keep real inventories, findings and evidence outside public git. See
[baseline](../../baseline/README.md), [exception template](../../reporting/exceptions.example.json)
and [SMB adoption](../../guides/smb-security.md). Scanner orchestration remains
future work; `dso` currently provides these three commands only.
