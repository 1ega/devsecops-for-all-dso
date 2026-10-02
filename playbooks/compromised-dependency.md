# Compromised dependency, action or image

**Trigger:** credible malicious/hijacked package, action, base image or registry
artifact used in builds or releases. **Owner:** release owner and incident lead.

1. Record affected ecosystem, exact version/digest, upstream advisory, first/last
   use and source of evidence. Identify consumers through lockfiles, SBOMs,
   workflows and deployed release manifests; name each asset owner.
2. Stop affected builds/releases and restrict the artifact's use. Preserve build
   logs, runner/image snapshots and artifact provenance in controlled storage.
   Treat potentially executed build code as an identity/runner compromise.
3. Determine reachable secrets, signing keys, cloud tokens and developer/runner
   identities. Revoke/rotate exposed credentials and review their use. Inventory
   persistent/self-hosted runners; rebuild compromised runners from known-good
   images rather than trusting cache cleanup alone.
4. Replace/pin a reviewed version or remove the component. Rebuild affected
   artifacts in a clean environment, generate new SBOM/provenance and verify
   approved signing identity before deployment. Investigate deployed instances.
5. Retest business flows, code/dependency/image scans and release verification.
   Resume releases through the service owner's recovery decision.
6. Record scope, downstream consumers, notification decisions and corrective
   actions under [incident response](incident-response.md). Close only after
   deployed digests and revoked credential behavior have been verified.
