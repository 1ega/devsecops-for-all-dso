# Leaked secret response

**Trigger:** a credential appears in code, a build log, an artifact or a public
location. **Owner:** service owner with the security/incident contact.

1. Identify the credential type, affected systems and likely exposure window.
   Restrict access to the finding and avoid copying the secret into tickets.
2. Revoke or rotate the credential. Update dependent services through the
   approved secret store and confirm the old credential no longer works.
3. Review provider and application logs for use of the exposed credential.
   Escalate signs of misuse through the incident response process.
4. Remove the secret from current code and build outputs. Review git history
   and artifact retention; removing a commit does not replace rotation.
5. Add a regression check, record root cause and link the response ticket to
   `DEV-02` in the private assessment.
