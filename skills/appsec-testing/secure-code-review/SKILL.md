---
name: secure-code-review
description: Review code or a pull request for security and quality defects, trace evidence to affected behavior, and propose focused fixes. Use for explicit code review or security review requests.
---

# Secure Code Review

Read the changed code and nearby callers, tests, configuration, and trust boundaries. Focus on behavior that can fail in practice: untrusted input reaching sensitive operations, broken authorization, secret exposure, unsafe defaults, and reliability regressions.

## Workflow

1. Identify entry points, privileged operations, and the assumptions the change makes about data and callers.
2. Trace suspicious paths end to end. Use targeted tests or static analysis when they help validate a specific concern.
3. Check error handling, resource cleanup, dependency behavior, and whether tests cover the important failure cases.
4. Report actionable findings first. For each, give the precise location, trigger, impact, and a small fix. State uncertainty when a precondition is unverified.
5. If no issue is confirmed, say what was reviewed and what remains untested. Keep style preferences separate from defects.

Use the [security review checklist](../../../guides/security-review.md) as a prompt, not as proof that a review is complete.
