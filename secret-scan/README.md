# secret-scan

A one-time (or repeatable) sweep for secrets committed anywhere in the **history**
of the IN-CORE GitHub repositories.

## Why this exists

GitHub's own secret scanning is already enabled on the public IN-CORE repos, and
when you turn it on it backfills — it scans every commit on every branch, not just
new pushes. That coverage is real, but it has two gaps this script fills:

1. **Private repos aren't covered.** The org is on the free plan, and secret
   scanning for private repositories requires the paid GitHub Secret Protection
   add-on. At the time of writing that is 9 of the org's 29 repos.
2. **Only partner patterns are matched.** GitHub detects roughly 200 credential
   formats with recognisable shapes (AWS keys, GitHub PATs, Slack tokens). It will
   not flag a hardcoded database password, a Keycloak client secret, a connection
   string with inline credentials, or a `.pem` committed into a config directory —
   which is where a platform like ours is most likely to leak something.

So a clean bill of health from GitHub is necessary but not sufficient. This script
runs two independent scanners over full history to cover the rest.

## What it runs

| tool | what it is good at |
|---|---|
| [gitleaks](https://github.com/gitleaks/gitleaks) | regex + entropy rules; catches the generic stuff (passwords, connection strings, private keys) |
| [trufflehog](https://github.com/trufflesecurity/trufflehog) | detector-based, and can **verify** a credential by calling the provider's API to see if it still works |

Both are run over `--all --full-history`, across every ref, including commits only
reachable from deleted branches.

## Requirements

```bash
brew install gitleaks trufflehog    # also needs git, python3, and gh for --clone
```

On Intel macOS, trufflehog has no prebuilt bottle and will compile from source
(pulls the Go toolchain; budget 10-15 minutes). gitleaks installs from a bottle.

## How to run

```bash
./scan-secrets.sh --clone      # mirror every IN-CORE repo into ./sweep, then scan
./scan-secrets.sh              # scan the mirrors already in ./sweep
```

`--clone` skips repos already present, so it is safe to re-run. Cloning uses
`--mirror` deliberately: a normal clone would miss commits that are only reachable
from deleted branches, which is exactly where forgotten secrets tend to survive.

Expect roughly 1.2 GB of mirrors and about 10 minutes for a full pass.

### Verification mode

```bash
VERIFY=1 ./scan-secrets.sh
```

Off by default. When **off**, trufflehog runs fully offline and reports every
candidate — nothing leaves your machine, but you hand-triage a larger pile.

When **on**, trufflehog calls each provider's API to check whether a credential is
still live. This is what turns hundreds of candidates into a short actionable list,
and it is genuinely useful — but understand what it does first: any real key found
in history gets exercised against AWS/GitHub/Slack/etc. from the machine running
the scan, and a live hit may appear in that provider's audit log. Turn it on
deliberately, not by habit.

## How to read the report

Each run writes a timestamped directory:

```
reports/<YYYYmmdd-HHMMSS>/
├── report.md     compiled summary — start here
├── scan.log      full transcript, and the live progress view while a scan runs
└── raw/          per-repo gitleaks JSON and trufflehog JSONL, unredacted
```

`report.md` has a summary table of every repo sorted with verified-live findings
first, then a per-repo detail table giving tool, rule/detector, file, commit, date,
author, and the secret **redacted** to first/last four characters. That means the
report is safe to attach to an issue or paste into a ticket. Full values stay in
`raw/` — treat that directory as sensitive and do not commit it.

`report.md` is only written once every repo has finished. While a scan is running,
tail `scan.log` to watch progress.

### Triage

**Raw counts are not findings.** Both tools are tuned to over-report, and most hits
are UUIDs, git SHAs, lockfile integrity digests, and test fixtures. Read the report
before acting on a number. A previous run flagged two "API keys" in a Playbook repo
that turned out to be DataWolf workflow parameter UUIDs.

When something is a genuine leak:

1. **Rotate the credential first.** This is the actual fix.
2. **Then decide about history.** Rewriting with `git filter-repo` or BFG breaks
   every existing clone and fork, and GitHub keeps the old commits reachable by SHA
   until you ask Support to garbage-collect them. A secret that was ever pushed to a
   public repo should be treated as permanently compromised no matter what you do to
   the history — which is why rotation is the fix and the rewrite is cleanup.

## Ongoing scanning

This script is for auditing history. To stop new secrets going in, use GitHub push
protection (already enabled on the public repos) plus a gitleaks pre-commit hook or
CI job, which also covers the private repos and the non-partner patterns GitHub
does not match.
