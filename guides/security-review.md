# Security review checklist

Use this checklist to guide a review of a change or small service. Follow the data and code paths rather than checking boxes in isolation.

## Trust boundaries

- Identify user-controlled input and every place it reaches a parser, shell, query, template, file path, or network client.
- Check authentication and authorization at the operation that reads or changes protected data.
- Verify object ownership checks cannot be bypassed with another identifier or role.

## Data and dependencies

- Keep secrets out of source, logs, errors, test fixtures, and generated output.
- Validate input shape and size before expensive processing; encode output for its destination.
- Review dependency and container versions, lockfiles, and the source of downloaded artifacts.

## Operations

- Look for unsafe defaults, disabled TLS validation, excessive privileges, and broad network exposure.
- Check failure paths, timeouts, cleanup, and whether security events are logged without sensitive payloads.
- Confirm tests exercise the security boundary and at least one failure case.

Record each issue with a reproduction path, impact, confidence, and a practical fix. A checklist alone cannot establish security.
