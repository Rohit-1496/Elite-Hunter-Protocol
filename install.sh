#!/usr/bin/env bash
# ================================================================
#  ELITE HUNTER PROTOCOL — AUTO INSTALLER
#  Installs OpenCode + embeds all brain & skill files.
#  One command. Ready to hunt.
# ================================================================

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/opencode"
BRAIN_DIR="$HOME"

banner() {
cat << "BANNER"

 ██████╗  ██████╗ ██╗  ██╗██╗  ██╗███████╗    ███████╗██╗      █████╗ ██╗   ██╗███████╗
 ██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗██╔╝██╔════╝    ██╔════╝██║     ██╔══██╗██║   ██║██╔════╝
 ██████╔╝██║   ██║ ╚███╔╝  ╚███╔╝ ███████╗    ███████╗██║     ███████║██║   ██║█████╗
 ██╔══██╗██║   ██║ ██╔██╗  ██╔██╗ ╚════██║    ╚════██║██║     ██╔══██║╚██╗ ██╔╝██╔══╝
 ██║  ██║╚██████╔╝██╔╝ ██╗██╔╝ ██╗███████║    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗
 ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝

                  LOCKED. LOADED. UNCHAINED.
           Installing OpenCode + Embedding all skills...

BANNER
}

log()     { echo -e "${GREEN}[+]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
section() { echo -e "\n${CYAN}${BOLD}══════════════════════════════════════${NC}"; \
            echo -e "${CYAN}${BOLD}  $1${NC}"; \
            echo -e "${CYAN}${BOLD}══════════════════════════════════════${NC}"; }

# ── STEP 1: Install OpenCode ───────────────────────────────────
install_opencode() {
    section "STEP 1/3 — INSTALLING OPENCODE"

    # Need Node.js for npm
    if ! command -v node &>/dev/null; then
        warn "Node.js not found — installing..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install node 2>/dev/null || { warn "Install Node.js from https://nodejs.org then re-run."; exit 1; }
        else
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - 2>/dev/null
            sudo apt-get install -y nodejs 2>/dev/null || \
            sudo yum install -y nodejs 2>/dev/null || \
            { warn "Install Node.js from https://nodejs.org then re-run."; exit 1; }
        fi
    fi

    log "Node.js found: $(node -v)"

    if command -v opencode &>/dev/null; then
        log "OpenCode already installed — updating to latest..."
        npm update -g opencode-ai 2>/dev/null || true
    else
        log "Installing OpenCode AI..."
        npm install -g opencode-ai 2>/dev/null || \
        sudo npm install -g opencode-ai 2>/dev/null
    fi

    log "OpenCode installed: $(opencode --version 2>/dev/null || echo 'ready') ✅"
}

# ── STEP 2: Embed All Brain & Skill Files ─────────────────────
embed_skills() {
    section "STEP 2/3 — EMBEDDING BRAIN & SKILLS"

    mkdir -p "$CONFIG_DIR"

    # Copy brain files to home (where config references them)
    log "Embedding brain files..."
    cp "$SCRIPT_DIR/brain/CLAUDE.md"  "$BRAIN_DIR/CLAUDE.md"
    cp "$SCRIPT_DIR/brain/CLAUDE1.md" "$BRAIN_DIR/CLAUDE1.md"
    cp "$SCRIPT_DIR/brain/OC.md"      "$BRAIN_DIR/OC.md"
    log "  ✅ CLAUDE.md    — Primary hunting methodology"
    log "  ✅ CLAUDE1.md   — Advanced chains & devil payloads"
    log "  ✅ OC.md        — Autonomous kill directives"

    # Copy all skill files to opencode config dir
    log "Embedding skill files..."
    cp "$SCRIPT_DIR/skills/CAVEMAN_SKILL.md"            "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/DEVIL_CHAINS.md"             "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/DEVIL_PAYLOADS_ADVANCED.md"  "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/DEVIL_PAYLOADS_AUTH_SSRF.md" "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/DEVIL_PAYLOADS_INJECTION.md" "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/DEVIL_PAYLOADS_XSS.md"       "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/DEVIL_TACTICS.md"            "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/DEVIL_UNIQUE.md"             "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/AGENTS.md"                   "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/CONFIRMATION_PROTOCOL.md"    "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/REPORTING_PROTOCOL.md"       "$CONFIG_DIR/"
    cp "$SCRIPT_DIR/skills/RECON_PROTOCOL.md"         "$CONFIG_DIR/"
    log "  ✅ CAVEMAN_SKILL          — Credit-saving intelligence"
    log "  ✅ DEVIL_CHAINS           — Pre-built P1 exploit chains"
    log "  ✅ DEVIL_PAYLOADS_XSS     — XSS arsenal"
    log "  ✅ DEVIL_PAYLOADS_INJECTION — SQLi, CMDi, XXE"
    log "  ✅ DEVIL_PAYLOADS_AUTH_SSRF — Auth bypass + SSRF"
    log "  ✅ DEVIL_PAYLOADS_ADVANCED  — Advanced payload lib"
    log "  ✅ DEVIL_TACTICS           — Hunting patterns"
    log "  ✅ DEVIL_UNIQUE            — Rare attack vectors"
}

# ── STEP 3: Write OpenCode Config ─────────────────────────────
write_config() {
    section "STEP 3/3 — WRITING CONFIG"

    cat > "$CONFIG_DIR/opencode.jsonc" << CONFIG
{
  "\$schema": "https://opencode.ai/config.json",

  // ██████╗  ██████╗ ██╗  ██╗██╗  ██╗███████╗    ███████╗██╗      █████╗ ██╗   ██╗███████╗
  // ELITE HUNTER PROTOCOL — DEVIL MODE v10.0
  // 90% Mind. 10% Tools. 0% Mercy. 100% Domination.

  "username": "ROXX",

  // Set your model after install by running: opencode
  // Then type: /connect   to add your API key (Gemini FREE or Anthropic)

  // BRAIN STACK — All loaded automatically
  "instructions": [
    "${CONFIG_DIR}/CONFIRMATION_PROTOCOL.md",
    "${CONFIG_DIR}/REPORTING_PROTOCOL.md",
    "${CONFIG_DIR}/RECON_PROTOCOL.md",
    "${BRAIN_DIR}/OC.md",
    "${BRAIN_DIR}/CLAUDE.md",
    "${BRAIN_DIR}/CLAUDE1.md"
  ],

  // SILENT HUNTER MODE — Zero interruptions
  "autoapprove": true,
  "permission": "allow",

  "mcp": {},
  "command": {}
}
CONFIG

    log "opencode.jsonc written to $CONFIG_DIR ✅"
    log "Brain stack linked ✅"
}

# ── DONE ──────────────────────────────────────────────────────
print_done() {
    section "INSTALLATION COMPLETE"
cat << "DONE"

  ██████╗  ██████╗ ███╗   ██╗███████╗██╗
  ██╔══██╗██╔═══██╗████╗  ██║██╔════╝██║
  ██║  ██║██║   ██║██╔██╗ ██║█████╗  ██║
  ██║  ██║██║   ██║██║╚██╗██║██╔══╝  ╚═╝
  ██████╔╝╚██████╔╝██║ ╚████║███████╗██╗
  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝

DONE
    echo -e "${GREEN}  ELITE HUNTER PROTOCOL is armed and ready.${NC}"
    echo ""
    echo -e "  ${BOLD}Next step — connect your API key (FREE):${NC}"
    echo -e "  ${CYAN}  opencode${NC}    ← launch it"
    echo -e "  ${CYAN}  /connect${NC}    ← type this inside OpenCode to add API key"
    echo ""
    echo -e "  ${BOLD}Free API key:${NC} ${CYAN}https://aistudio.google.com/apikey${NC} (Google Gemini - no card)"
    echo ""
    echo -e "  ${BOLD}Start hunting:${NC}"
    echo -e "  ${CYAN}  cd /your/target && opencode${NC}"
    echo ""
}

# ── MAIN ──────────────────────────────────────────────────────
banner
install_opencode
embed_skills
write_config
print_done
