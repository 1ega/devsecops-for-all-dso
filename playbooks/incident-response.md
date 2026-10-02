# Incident response starter plan

Keep a private copy with real names, phone numbers, alternate channels and
service-provider contacts. Review it every 90 days and after each incident.

| Role | Responsibility | Named person / backup |
| --- | --- | --- |
| Incident lead | Declares severity, coordinates decisions and timeline | Fill privately |
| Technical lead | Investigates, contains and preserves evidence | Fill privately |
| Service owner | Assesses customer and business impact | Fill privately |
| Communications/legal | Handles required internal and external notices | Fill privately |

## First response

1. Record who reported the event, when it started, affected assets and the
   current business impact. Open a private incident record.
2. Assign an incident lead and a severity. Use a separate communication channel
   if the normal identity or email system may be compromised.
3. Preserve relevant logs and snapshots with timestamps and controlled access.
   Record every containment action before making changes when practical.
4. Contain active access: disable compromised credentials, isolate affected
   systems or block exposed paths. Have the service owner assess downtime risk.
5. Investigate scope and cause. Check neighboring accounts, services and data
   stores before declaring containment complete.
6. Restore from a known-good state, monitor for recurrence and verify critical
   business flows. Track data loss and recovery time.
7. Let the designated communications/legal owner determine notification duties
   from applicable contracts and law. Record decisions and timestamps.
8. Hold a short review, assign corrective actions and update this plan. Link
   the exercise or incident record to `IR-01` and, when applicable, `IR-02`.

## Severity starter guide

- **Critical:** active compromise of a production service or sensitive data,
  widespread outage, or attacker control of privileged identity.
- **High:** credible compromise with limited scope, or a critical exposed
  weakness with active exploitation evidence.
- **Medium:** suspicious event requiring investigation, with no confirmed
  production impact yet.

The incident lead may raise severity based on customer impact, uncertainty or
the time needed to contain the event.
