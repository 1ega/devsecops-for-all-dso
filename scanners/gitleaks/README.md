# gitleaks

A `.gitleaks.toml` that extends the default rules (`[extend] useDefault = true`) with patterns generic rules often miss, especially in mobile projects:

- Firebase and Google API keys in `google-services.json` and `GoogleService-Info.plist`
- Keystores and signing properties (`*.jks`, `keystore.properties`)
- React Native `.env` files and Expo configuration
- Fastlane credentials (`fastlane/Appfile`, `Matchfile`)

Includes an allowlist for synthetic test fixtures. What to do after a leak belongs in [playbooks](../../playbooks/README.md).

Research candidates: [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks), [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) (live verification), [Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) (baseline approach). Related skill: [kingfisher](../../skills/secrets-management/kingfisher/SKILL.md).

Imported reference material:

- [gitleaks-default](../../rules/secrets/gitleaks-default/SOURCE.md) — the upstream default `gitleaks.toml` (MIT), to read before extending it.
- [secrets-patterns-db](../../rules/secrets/secrets-patterns-db/SOURCE.md) — over a thousand open secret patterns (CC-BY-SA-4.0), raw material for custom rules.

**Status:** Reference content imported; our extended configuration is not published yet.
