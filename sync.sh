#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════
#  ELITE HUNTER PROTOCOL — SYNC ENGINE
#  Repo = single source of truth. Edit here, run this, done.
#  Usage: ./sync.sh   (from repo root)
# ══════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# dedupe targets (HOME may equal /root)
mapfile -t TARGETS < <(printf '%s\n' "$HOME/.config/opencode" "/root/.config/opencode" | awk '!seen[$0]++')
mapfile -t BRAIN_TARGETS < <(printf '%s\n' "$HOME" "/root" | awk '!seen[$0]++')

log()  { printf "\033[1;32m[SYNC]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[WARN]\033[0m %s\n" "$*"; }

# ── 1. Skills → config dirs ───────────────────────────────────
for cfg in "${TARGETS[@]}"; do
    [ -d "$cfg" ] || { warn "skip $cfg (no dir)"; continue; }
    for f in "$SCRIPT_DIR"/skills/*.md; do
        cp "$f" "$cfg/"
    done
    log "skills -> $cfg ($(ls "$SCRIPT_DIR"/skills/*.md | wc -l) files)"
done

# ── 2. Brain files → home dirs ────────────────────────────────
for home in "${BRAIN_TARGETS[@]}"; do
    [ -d "$home" ] || continue
    for f in CLAUDE.md CLAUDE1.md OC.md; do
        [ -f "$SCRIPT_DIR/brain/$f" ] && cp "$SCRIPT_DIR/brain/$f" "$home/"
    done
    log "brain  -> $home"
done

# ── 3. save_report.sh → PATH ──────────────────────────────────
if [ -f "$SCRIPT_DIR/save_report.sh" ]; then
    if cp "$SCRIPT_DIR/save_report.sh" /usr/local/bin/save_report.sh 2>/dev/null &&
       chmod +x /usr/local/bin/save_report.sh 2>/dev/null; then
        log "save_report.sh -> /usr/local/bin (reporting gate active)"
    else
        cp "$SCRIPT_DIR/save_report.sh" "$HOME/.local/bin/save_report.sh" 2>/dev/null || true
        chmod +x "$HOME/.local/bin/save_report.sh" 2>/dev/null || true
        warn "no root access — save_report.sh -> ~/.local/bin (ensure it's in PATH)"
    fi
fi

# ── 4. Config sanity: every instruction file must exist ───────
for cfg in "${TARGETS[@]}"; do
    j="$cfg/opencode.jsonc"
    [ -f "$j" ] || continue
    missing=$(grep -oE '"/[^"]+\.md"' "$j" | tr -d '"' | while read -r p; do
        [ -f "$p" ] || echo "$p"
    done)
    if [ -n "${missing:-}" ]; then
        warn "opencode.jsonc references missing files in $cfg:"
        echo "$missing" | sed 's/^/       ❌ /'
    else
        log "config OK: $cfg/opencode.jsonc (all instruction files exist)"
    fi
done

log "DONE. Restart opencode sessions to load changes."
