# API authorization tests

Use staging tenants and synthetic data. Build an endpoint matrix for anonymous,
owner, other user, tenant admin, other tenant, service and revoked identities.
Include exports, search, batches, nested objects, downloads and asynchronous jobs.

| Case | Expected result |
| :--- | :--- |
| Owner requests their object | Documented success with allowed fields |
| User changes object ID to someone else's | Denied; no data or side effect |
| Tenant A requests tenant B's export/job/object | Denied across nested/batch routes |
| Reader calls admin/write route | Denied; state unchanged |
| Client supplies role/tenant/owner/is_admin | Unauthorized changes rejected or ignored |
| Revoked token requests protected route | Denied within the recorded revocation window |
| Denied request changes method/content type | Same authorization decision |

Assert content and resulting state, not only HTTP status. Ensure masked errors
do not disclose object existence beyond the threat model. Unauthenticated
ZAP/nuclei scans do not prove object authorization. Implement these checks in the
application's test framework and run them for relevant changes; attach matrix,
commit, test output, owner and environment to `DEV-05`.

Sources: [OWASP authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
and [test matrices](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Testing_Automation_Cheat_Sheet.html).
