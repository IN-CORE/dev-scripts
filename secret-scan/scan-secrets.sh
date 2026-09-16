#!/usr/bin/env bash
#
# scan-secrets.sh — one-time secret-history sweep across the IN-CORE org.
#
# Iterates every mirror clone under ./sweep/*.git, runs gitleaks and trufflehog
# over the FULL history of every ref, and compiles a report.
#
# Usage:
#   ./scan-secrets.sh              # scan existing mirrors in ./sweep
#   ./scan-secrets.sh --clone      # (re-)mirror all IN-CORE repos first
#   VERIFY=1 ./scan-secrets.sh     # let trufflehog verify creds against live APIs
#
# VERIFY: off by default. When off, trufflehog runs fully offline and reports
# every candidate (noisier, but nothing leaves this machine). When on, trufflehog
# calls each provider's API to check whether a credential still works — that turns
# hundreds of candidates into a short actionable list, but it exercises any real
# key found against AWS/GitHub/Slack/etc. from this laptop, and live hits may show
# up in that provider's audit log. Turn it on deliberately.

set -uo pipefail

ORG=IN-CORE
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SWEEP="$ROOT/sweep"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$ROOT/reports/$STAMP"
RAW="$OUT/raw"
LOG="$OUT/scan.log"
REPORT="$OUT/report.md"
VERIFY="${VERIFY:-0}"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/incore-sweep-XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT

mkdir -p "$RAW"

log() { printf '%s %s\n' "[$(date +%H:%M:%S)]" "$*" | tee -a "$LOG"; }

for bin in git gitleaks trufflehog python3; do
  command -v "$bin" >/dev/null || { echo "FATAL: '$bin' not found on PATH" >&2; exit 1; }
done

# ---------------------------------------------------------------- clone (opt)
if [[ "${1:-}" == "--clone" ]]; then
  command -v gh >/dev/null || { echo "FATAL: gh required for --clone" >&2; exit 1; }
  log "mirroring $ORG repos into $SWEEP"
  mkdir -p "$SWEEP"
  gh repo list "$ORG" --limit 200 --json name -q '.[].name' \
    | xargs -P4 -I{} sh -c "[ -d '$SWEEP/{}.git' ] || git clone --quiet --mirror https://github.com/$ORG/{}.git '$SWEEP/{}.git'"
fi

shopt -s nullglob dotglob
REPOS=("$SWEEP"/*.git)
shopt -u dotglob
[[ ${#REPOS[@]} -gt 0 ]] || { echo "FATAL: no mirrors found in $SWEEP (run with --clone)" >&2; exit 1; }

log "scanning ${#REPOS[@]} repos   gitleaks=$(gitleaks version)  trufflehog=$(trufflehog --version 2>&1 | head -1)"
log "trufflehog verification: $([[ $VERIFY == 1 ]] && echo 'ON (live API calls)' || echo 'OFF (offline)')"
log "output: $OUT"

TH_FLAGS=(--json --no-update)
[[ "$VERIFY" == 1 ]] || TH_FLAGS+=(--no-verification)

# ---------------------------------------------------------------------- scan
for repo in "${REPOS[@]}"; do
  name="$(basename "$repo" .git)"
  commits=$(git -C "$repo" rev-list --all --count 2>/dev/null || echo 0)
  log "--- $name ($commits commits)"

  gitleaks git "$repo" \
    --report-format json \
    --report-path "$RAW/$name.gitleaks.json" \
    --log-opts="--all --full-history" \
    >>"$LOG" 2>&1
  gl_rc=$?
  [[ -f "$RAW/$name.gitleaks.json" ]] || echo '[]' > "$RAW/$name.gitleaks.json"

  # trufflehog cannot read a bare/mirror repo (it stats for .git and an index),
  # so materialise a temporary --shared working clone: objects are shared via
  # alternates (no history duplication) and refs from every branch stay visible.
  work="$WORKDIR/$name"
  rm -rf "$work"
  if git clone --quiet --shared "$repo" "$work" 2>>"$LOG"; then
    trufflehog git "file://$work" "${TH_FLAGS[@]}" \
      > "$RAW/$name.trufflehog.jsonl" 2>>"$LOG"
    th_rc=$?
  else
    log "    WARN: could not create working clone; skipping trufflehog"
    : > "$RAW/$name.trufflehog.jsonl"
    th_rc=127
  fi
  rm -rf "$work"

  gl_n=$(python3 -c "import json,sys;print(len(json.load(open(sys.argv[1]))))" "$RAW/$name.gitleaks.json" 2>/dev/null || echo 0)
  th_n=$(wc -l < "$RAW/$name.trufflehog.jsonl" 2>/dev/null | tr -d ' ' || echo 0)
  log "    gitleaks=$gl_n (rc=$gl_rc)  trufflehog=$th_n (rc=$th_rc)"
done

# -------------------------------------------------------------------- report
log "compiling report"
VERIFY="$VERIFY" OUT="$OUT" RAW="$RAW" REPORT="$REPORT" STAMP="$STAMP" python3 <<'PY'
import json, os, glob, collections

RAW, REPORT, STAMP = os.environ['RAW'], os.environ['REPORT'], os.environ['STAMP']
VERIFY = os.environ['VERIFY'] == '1'

def redact(s, keep=4):
    s = (s or '').strip()
    if len(s) <= keep * 2: return '*' * len(s)
    return f"{s[:keep]}...{s[-keep:]} (len {len(s)})"

rows, detail = [], collections.OrderedDict()

# NB: glob.glob() skips dotfiles, which would silently drop dot-named repos
# such as the org's `.github` repo from the report. Enumerate the dir instead.
gl_files = sorted(os.path.join(RAW, x) for x in os.listdir(RAW)
                  if x.endswith('.gitleaks.json'))
for f in gl_files:
    name = os.path.basename(f)[:-len('.gitleaks.json')]
    try: gl = json.load(open(f))
    except Exception: gl = []

    th, thfile = [], f'{RAW}/{name}.trufflehog.jsonl'
    if os.path.exists(thfile):
        for line in open(thfile):
            line = line.strip()
            if not line: continue
            try:
                o = json.loads(line)
                if o.get('SourceMetadata'): th.append(o)
            except Exception: pass

    verified = [o for o in th if o.get('Verified')]
    rows.append((name, len(gl), len(th), len(verified)))

    items = []
    for x in gl:
        items.append(dict(tool='gitleaks', rule=x.get('RuleID',''), file=x.get('File',''),
                          commit=(x.get('Commit') or '')[:10], date=x.get('Date',''),
                          author=x.get('Author',''), verified=None,
                          secret=redact(x.get('Secret',''))))
    for o in th:
        g = (o.get('SourceMetadata',{}).get('Data',{}).get('Git',{}) or {})
        items.append(dict(tool='trufflehog',
                          rule=f"{o.get('DetectorName','')}", file=g.get('file',''),
                          commit=(g.get('commit') or '')[:10], date=g.get('timestamp',''),
                          author=g.get('email',''), verified=bool(o.get('Verified')),
                          secret=redact(o.get('Raw',''))))
    if items: detail[name] = items

rows.sort(key=lambda r: (-r[3], -(r[1]+r[2]), r[0]))
tot = [sum(r[i] for r in rows) for i in (1,2,3)]

with open(REPORT,'w') as fh:
    w = fh.write
    w(f"# IN-CORE secret-history sweep\n\n")
    w(f"- Run: `{STAMP}`\n- Repos scanned: **{len(rows)}**\n")
    w(f"- TruffleHog verification: **{'ON' if VERIFY else 'OFF (offline — Verified column not meaningful)'}**\n")
    w(f"- Raw findings: gitleaks **{tot[0]}**, trufflehog **{tot[1]}**"
      + (f", of which **verified live: {tot[2]}**\n\n" if VERIFY else "\n\n"))
    w("> Raw counts are pre-triage and include false positives (UUIDs, hashes,\n"
      "> test fixtures, lockfile digests). Triage before acting. Secrets below are\n"
      "> redacted; full values are in `raw/`.\n\n")

    w("## Summary\n\n| repo | gitleaks | trufflehog | verified |\n|---|---:|---:|---:|\n")
    for n,g,t,v in rows:
        w(f"| {n} | {g} | {t} | {v if VERIFY else '–'} |\n")
    w(f"| **total** | **{tot[0]}** | **{tot[1]}** | **{tot[2] if VERIFY else '–'}** |\n\n")

    w("## Findings by repo\n\n")
    if not detail: w("_No findings._\n")
    for name, items in detail.items():
        w(f"### {name} ({len(items)})\n\n")
        w("| tool | rule/detector | file | commit | date | verified | secret |\n|---|---|---|---|---|---|---|\n")
        for i in sorted(items, key=lambda x: (x['verified'] is not True, x['file'])):
            v = '**LIVE**' if i['verified'] else ('no' if i['verified'] is False else '–')
            w(f"| {i['tool']} | {i['rule']} | `{i['file']}` | `{i['commit']}` | {i['date'][:10]} | {v} | `{i['secret']}` |\n")
        w("\n")

print(f"repos={len(rows)} gitleaks={tot[0]} trufflehog={tot[1]} verified={tot[2]}")
PY

log "report written: $REPORT"
echo
echo "===================================================================="
echo " report : $REPORT"
echo " raw    : $RAW"
echo " log    : $LOG"
echo "===================================================================="
