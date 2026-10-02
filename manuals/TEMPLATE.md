# <Tool name>

**Version covered:** x.y.z
**Upstream:** <link to project and documentation>
**License:** <SPDX identifier>

## What it is for

One paragraph: what the tool finds or enforces, and where it fits in the pipeline.

## Install

Pinned installation for local use and for CI (package, container image with digest, or release binary with checksum).

## Run locally

The smallest useful command, then the common variants.

## Run in CI

GitHub Actions and GitLab CI examples. Link to the template in [`integrations/`](../integrations/README.md) when one exists.

## Configuration

Where configuration lives, the options that matter, and the repository configuration in [`scanners/`](../scanners/README.md) or [`policies/`](../policies/README.md).

## Output and triage

Output formats (SARIF, JSON), how severity maps to [the normalized scale](../reporting/severity-and-metadata.md), and how to tell real findings from noise.

## Tuning

Suppressions, baselines, and allowlists — always with a justification and an expiry.

## Pitfalls

Known limitations, false positives, and performance issues.
