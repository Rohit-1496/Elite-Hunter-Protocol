#!/usr/bin/env bash
# ================================================================
#  ROXX'S SLAVE — AUTO INSTALLER
#  One command. Everything set up. Ready to hunt.
#  Supports: Kali Linux, Ubuntu/Debian, macOS, Parrot OS
# ================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

INSTALL_DIR="$HOME/.config/opencode"
BRAIN_DIR="$HOME"

banner() {
cat << "BANNER"
 ██████╗  ██████╗ ██╗  ██╗██╗  ██╗███████╗    ███████╗██╗      █████╗ ██╗   ██╗███████╗
 ██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗██╔╝██╔════╝    ██╔════╝██║     ██╔══██╗██║   ██║██╔════╝
 ██████╔╝██║   ██║ ╚███╔╝  ╚███╔╝ ███████╗    ███████╗██║     ███████║██║   ██║█████╗
 ██╔══██╗██║   ██║ ██╔██╗  ██╔██╗ ╚════██║    ╚════██║██║     ██╔══██║╚██╗ ██╔╝██╔══╝
 ██║  ██║╚██████╔╝██╔╝ ██╗██╔╝ ██╗███████║    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗
 ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝
                   AUTONOMOUS BUG BOUNTY INTELLIGENCE — AUTO INSTALLER
BANNER
echo ""
}

log()     { echo -e "${GREEN}[+]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
error()   { echo -e "${RED}[✗]${NC} $1"; exit 1; }
section() { echo -e "\n${CYAN}${BOLD}══════════════════════════════════════${NC}"; echo -e "${CYAN}${BOLD}  $1${NC}"; echo -e "${CYAN}${BOLD}══════════════════════════════════════${NC}"; }

detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif grep -qi kali /etc/os-release 2>/dev/null || grep -qi parrot /etc/os-release 2>/dev/null; then
        OS="kali"
    elif grep -qi ubuntu /etc/os-release 2>/dev/null || grep -qi debian /etc/os-release 2>/dev/null; then
        OS="debian"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
        error "Windows detected. Please use WSL2 with Ubuntu or Kali. See README for Windows setup."
    else
        OS="linux"
    fi
    log "Detected OS: $OS"
}

install_system_deps() {
    section "INSTALLING SYSTEM DEPENDENCIES"
    case $OS in
        macos)
            if ! command -v brew &>/dev/null; then
                warn "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install git curl wget jq nmap sqlmap hydra nikto gobuster node go python3 2>/dev/null || true
            ;;
        kali|debian)
            sudo apt-get update -qq
            sudo apt-get install -y git curl wget jq nmap sqlmap hydra nikto gobuster \
                python3 python3-pip nodejs npm golang-go unzip build-essential 2>/dev/null || true
            ;;
        linux)
            sudo apt-get update -qq 2>/dev/null || sudo yum update -q 2>/dev/null || true
            sudo apt-get install -y git curl wget jq nmap python3 python3-pip nodejs npm golang-go unzip 2>/dev/null || \
            sudo yum install -y git curl wget jq nmap python3 python3-pip nodejs npm golang unzip 2>/dev/null || true
            ;;
    esac
    log "System dependencies installed ✅"
}

install_go_tools() {
    section "INSTALLING GO-BASED SECURITY TOOLS"

    export GOPATH="$HOME/go"
    export PATH="$PATH:$GOPATH/bin"

    GO_TOOLS=(
        "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
        "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
        "github.com/projectdiscovery/httpx/cmd/httpx@latest"
        "github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
        "github.com/projectdiscovery/katana/cmd/katana@latest"
        "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
        "github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest"
        "github.com/projectdiscovery/notify/cmd/notify@latest"
        "github.com/ffuf/ffuf/v2@latest"
        "github.com/OJ/gobuster/v3@latest"
        "github.com/owasp-amass/amass/v4/...@master"
        "github.com/tomnomnom/waybackurls@latest"
        "github.com/tomnomnom/anew@latest"
        "github.com/tomnomnom/gf@latest"
        "github.com/lc/gau/v2/cmd/gau@latest"
        "github.com/hakluke/hakrawler@latest"
        "github.com/003random/getJS@latest"
    )

    for tool in "${GO_TOOLS[@]}"; do
        tool_name=$(basename ${tool%@*})
        if command -v "$tool_name" &>/dev/null; then
            log "$tool_name already installed — skipping"
        else
            warn "Installing $tool_name..."
            go install "$tool" 2>/dev/null && log "$tool_name ✅" || warn "$tool_name failed — skipping"
        fi
    done

    # Add GOPATH/bin to shell profile
    SHELL_RC="$HOME/.bashrc"
    [[ "$OSTYPE" == "darwin"* ]] && SHELL_RC="$HOME/.zshrc"
    if ! grep -q "GOPATH/bin" "$SHELL_RC" 2>/dev/null; then
        echo 'export PATH="$PATH:$HOME/go/bin"' >> "$SHELL_RC"
    fi

    log "Go tools installed ✅"
}

install_opencode() {
    section "INSTALLING OPENCODE"
    if command -v opencode &>/dev/null; then
        log "OpenCode already installed — updating..."
    fi
    npm install -g opencode-ai@latest 2>/dev/null || \
        npx opencode-ai@latest --version 2>/dev/null || \
        warn "OpenCode install issue — try: npm install -g opencode-ai manually"
    log "OpenCode installed ✅"
}

install_python_deps() {
    section "INSTALLING PYTHON DEPENDENCIES"
    pip3 install requests urllib3 colorama rich python-dotenv --quiet --break-system-packages 2>/dev/null || \
    pip3 install requests urllib3 colorama rich python-dotenv --quiet 2>/dev/null || \
    pip install requests urllib3 colorama rich python-dotenv --quiet 2>/dev/null
    log "Python packages installed ✅"
}

setup_config() {
    section "SETTING UP ROXX'S SLAVE CONFIGURATION"

    mkdir -p "$INSTALL_DIR"
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Copy skill files
    log "Copying skill files to $INSTALL_DIR..."
    cp "$SCRIPT_DIR/skills/"*.md "$INSTALL_DIR/" 2>/dev/null && log "Skill files copied ✅"

    # Copy brain files
    log "Copying brain files to $BRAIN_DIR..."
    cp "$SCRIPT_DIR/brain/CLAUDE.md"  "$BRAIN_DIR/"
    cp "$SCRIPT_DIR/brain/CLAUDE1.md" "$BRAIN_DIR/"
    cp "$SCRIPT_DIR/brain/OC.md"      "$BRAIN_DIR/"
    log "Brain files copied ✅"

    # Write opencode.jsonc
    log "Writing OpenCode config..."
    cat > "$INSTALL_DIR/opencode.jsonc" << CONFIG
{
  "\$schema": "https://opencode.ai/config.json",

  // ROXX'S SLAVE — DEVIL MODE
  // 90% Mind. 10% Tools. 0% Mercy. 100% Domination.

  "username": "ROXX",
  "model": "anthropic/claude-sonnet-4-5",

  "instructions": [
    "$BRAIN_DIR/OC.md",
    "$BRAIN_DIR/CLAUDE.md",
    "$BRAIN_DIR/CLAUDE1.md"
  ],

  "autoapprove": true,
  "permission": "allow",
  "mcp": {},
  "command": {}
}
CONFIG
    log "OpenCode config written ✅"
}

setup_api_key() {
    section "API KEY SETUP"
    echo ""
    echo -e "${YELLOW}You need an Anthropic API key to run ROXX'S SLAVE.${NC}"
    echo -e "Get one free at: ${CYAN}https://console.anthropic.com${NC}"
    echo ""
    read -p "$(echo -e ${BOLD}Enter your Anthropic API key \(or press Enter to skip\): ${NC})" API_KEY
    if [[ -n "$API_KEY" ]]; then
        SHELL_RC="$HOME/.bashrc"
        [[ "$OSTYPE" == "darwin"* ]] && SHELL_RC="$HOME/.zshrc"
        echo "export ANTHROPIC_API_KEY=\"$API_KEY\"" >> "$SHELL_RC"
        export ANTHROPIC_API_KEY="$API_KEY"
        log "API key saved to $SHELL_RC ✅"
    else
        warn "Skipped — run: export ANTHROPIC_API_KEY=your_key_here"
    fi
}

print_success() {
    section "INSTALLATION COMPLETE"
    cat << "SUCCESS"

  ██████╗  ██████╗ ███╗   ██╗███████╗██╗
  ██╔══██╗██╔═══██╗████╗  ██║██╔════╝██║
  ██║  ██║██║   ██║██╔██╗ ██║█████╗  ██║
  ██║  ██║██║   ██║██║╚██╗██║██╔══╝  ╚═╝
  ██████╔╝╚██████╔╝██║ ╚████║███████╗██╗
  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝

SUCCESS
    echo -e "${GREEN}ROXX'S SLAVE is locked, loaded and ready to hunt.${NC}"
    echo ""
    echo -e "  ${BOLD}To start hunting:${NC}"
    echo -e "  ${CYAN}  cd /your/target/directory${NC}"
    echo -e "  ${CYAN}  opencode${NC}"
    echo ""
    echo -e "  ${BOLD}Reload your shell first:${NC}"
    echo -e "  ${CYAN}  source ~/.bashrc   # Linux/Kali"
    echo -e "  ${CYAN}  source ~/.zshrc    # macOS"
    echo ""
}

# ── MAIN ───────────────────────────────────────────────────────
banner
detect_os
install_system_deps
install_go_tools
install_opencode
install_python_deps
setup_config
setup_api_key
print_success
