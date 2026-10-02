# Critical service restore drill

**Owner:** service owner and operations owner. **Frequency:** at least every
180 days for a critical service, and after a major backup architecture change.

1. Choose one production-like service and define the recovery point and time
   objectives before the exercise.
2. Restore a recent backup into an isolated environment. Never overwrite the
   live service during a drill.
3. Confirm data integrity, application startup and one business-critical flow.
4. Record backup age, actual restore time, missing dependencies and any data
   loss. Open tickets for failures and assign owners and deadlines.
5. Link the dated result to `BKP-02` in the private assessment. A successful
   backup job alone does not satisfy this control.
