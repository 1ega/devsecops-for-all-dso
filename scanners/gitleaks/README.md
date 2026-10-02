# gitleaks

A `.gitleaks.toml` that extends the default rules (`[extend] useDefault = true`) with patterns generic rules often miss, especially in mobile projects:

- Firebase and Google API keys in `google-services.json` and `GoogleService-Info.plist`
- Keystores and signing properties (`*.jks`, `keystore.properties`)
- React Native `.env` files and Expo configuration
- Fastlane credentials (`fastlane/Appfile`, `Matchfile`)

Includes an allowlist for synthetic test fixtures. What to do after a leak belongs in [playbooks](../../playbooks/README.md).

Research candidates: [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks), [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) (live verification), [Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) (baseline approach). Related skill: [kingfisher](../../skills/secrets-management/kingfisher/SKILL.md).

**Status:** Structure only; no configuration is published yet.
