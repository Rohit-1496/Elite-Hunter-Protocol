#!/usr/bin/env bash
# =============================================================================
# save_report.sh  —  HARD CONFIRMATION GATE
# -----------------------------------------------------------------------------
# A report only leaves the machine if it carries a valid CONFIRMATION MANIFEST
# (see CONFIRMATION_PROTOCOL.md). Every one of the 5 hard gates must PASS
# (G4 may be NA), the confirmation score must be >= THRESHOLD, the label must be
# CONFIRMED, and there must be >= MIN_EVIDENCE evidence items.
#
# Usage:
#   save_report.sh /path/to/report.md            # manifest embedded in the report
#   save_report.sh /path/to/report.docx          # needs sidecar: report.docx.manifest
#
# Exit codes: 0 saved | 1 bad usage | 2 missing sidecar | 3 no manifest | 10 gate failed
# =============================================================================

set -euo pipefail

# ---- config -----------------------------------------------------------------
THRESHOLD=85
MIN_EVIDENCE=2
DEST="/mnt/c/Users/rohit/Downloads"
# -----------------------------------------------------------------------------

REPORT="${1:-}"
if [[ -z "$REPORT" || ! -f "$REPORT" ]]; then
  echo "[REJECT] report file not found." >&2
  echo "         usage: save_report.sh <report-file>" >&2
  exit 1
fi

# Binary reports (docx/pdf) can't be grepped for the manifest text, so require a
# plain-text sidecar named  <report>.manifest  living next to the report.
MANIFEST_SRC="$REPORT"
if [[ "$REPORT" =~ \.(docx|pdf|xlsx|pptx)$ ]]; then
  if [[ -f "${REPORT}.manifest" ]]; then
    MANIFEST_SRC="${REPORT}.manifest"
  else
    echo "[REJECT] binary report needs a text sidecar manifest: ${REPORT}.manifest" >&2
    exit 2
  fi
fi

# ---- extract the manifest block ---------------------------------------------
BLOCK="$(awk '/=== CONFIRMATION MANIFEST/{f=1} f{print} /=== END MANIFEST/{f=0}' "$MANIFEST_SRC" 2>/dev/null || true)"
if [[ -z "$BLOCK" ]]; then
  echo "[REJECT] no CONFIRMATION MANIFEST found -> finding is NOT confirmed -> NOT saved." >&2
  echo "         (add the manifest block from CONFIRMATION_PROTOCOL.md Part D)" >&2
  exit 3
fi

# pull a single key's value, strip inline '# comments' and surrounding space
get() {
  echo "$BLOCK" | grep -iE "^[[:space:]]*$1[[:space:]]*:" | head -1 \
    | sed -E 's/^[^:]*:[[:space:]]*//' | sed -E 's/[[:space:]]*#.*$//' \
    | tr -d '[:space:]'
}

LABEL="$(get 'label')"
SCORE="$(get 'confirmation_score')"
G0="$(get 'gate_G0_in_scope')"
G1="$(get 'gate_G1_reproduce_3x_clean')"
G2="$(get 'gate_G2_negative_control')"
G3="$(get 'gate_G3_benign_ruled_out')"
G4="$(get 'gate_G4_determinism')"
G5="$(get 'gate_G5_real_impact')"
# count "  - something" evidence lines inside the block
EVID_COUNT="$(echo "$BLOCK" | grep -cE '^[[:space:]]*-[[:space:]]+[^[:space:]]' || true)"

# ---- validate ---------------------------------------------------------------
fail=0
chk() { # chk "human name" "value" "PASS"  (accepts extra allowed values as $4)
  local name="$1" val="$2" want="$3" alt="${4:-}"
  if [[ "$val" == "$want" || ( -n "$alt" && "$val" == "$alt" ) ]]; then return 0; fi
  echo "[REJECT] $name = '${val:-<empty>}' (expected ${want}${alt:+ or $alt})" >&2
  fail=1
}

chk "label"                     "$LABEL" "CONFIRMED"
chk "G0 scope not confirmed"    "$G0"    "PASS"
chk "G1 reproduce-3x-clean"     "$G1"    "PASS"
chk "G2 negative-control"       "$G2"    "PASS"
chk "G3 benign-ruled-out"       "$G3"    "PASS"
chk "G4 determinism"            "$G4"    "PASS" "NA"
chk "G5 real-impact"            "$G5"    "PASS"

if ! [[ "$SCORE" =~ ^[0-9]+$ ]]; then
  echo "[REJECT] confirmation_score is not a number ('${SCORE:-<empty>}')" >&2
  fail=1
elif (( SCORE < THRESHOLD )); then
  echo "[REJECT] confirmation_score $SCORE < threshold $THRESHOLD" >&2
  fail=1
fi

if (( EVID_COUNT < MIN_EVIDENCE )); then
  echo "[REJECT] need >= $MIN_EVIDENCE evidence items (found $EVID_COUNT)" >&2
  fail=1
fi

if (( fail )); then
  echo "[BLOCKED] Report NOT saved. Fix the finding, or keep it as SUSPECTED." >&2
  exit 10
fi

# ---- save -------------------------------------------------------------------
mkdir -p "$DEST"
cp "$REPORT" "$DEST/"
echo "[OK] CONFIRMED (score $SCORE, evidence $EVID_COUNT). Saved -> $DEST/$(basename "$REPORT")"
