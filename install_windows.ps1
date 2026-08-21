# ================================================================
#  ROXX'S SLAVE — WINDOWS INSTALLER (PowerShell)
#  Run in PowerShell as Administrator inside WSL2 or native
# ================================================================

Write-Host @"
 ██████╗  ██████╗ ██╗  ██╗██╗  ██╗███████╗    ███████╗██╗      █████╗ ██╗   ██╗███████╗
 ROXX'S SLAVE — WINDOWS INSTALLER
"@ -ForegroundColor Red

Write-Host "[!] Windows users: Install WSL2 first for best experience." -ForegroundColor Yellow
Write-Host "    Run in PowerShell (Admin): wsl --install -d kali-linux" -ForegroundColor Cyan
Write-Host "    Then run install.sh inside WSL2." -ForegroundColor Cyan
Write-Host ""

# Check if Chocolatey is installed
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "[+] Installing Chocolatey..." -ForegroundColor Green
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

Write-Host "[+] Installing dependencies via Chocolatey..." -ForegroundColor Green
choco install -y git nodejs golang python nmap curl wget jq

Write-Host "[+] Installing Go tools..." -ForegroundColor Green
$env:GOPATH = "$HOME\go"
$env:PATH += ";$env:GOPATH\bin"

$goTools = @(
    "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "github.com/ffuf/ffuf/v2@latest",
    "github.com/tomnomnom/waybackurls@latest",
    "github.com/tomnomnom/anew@latest",
    "github.com/lc/gau/v2/cmd/gau@latest"
)

foreach ($tool in $goTools) {
    $name = ($tool -split "/")[-1] -replace "@.*",""
    Write-Host "[+] Installing $name..." -ForegroundColor Green
    go install $tool 2>$null
}

Write-Host "[+] Installing OpenCode..." -ForegroundColor Green
npm install -g opencode-ai

Write-Host "[+] Copying config files..." -ForegroundColor Green
$configDir = "$HOME\.config\opencode"
New-Item -ItemType Directory -Force -Path $configDir | Out-Null
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Copy-Item "$scriptDir\skills\*.md" $configDir -Force
Copy-Item "$scriptDir\brain\CLAUDE.md" $HOME -Force
Copy-Item "$scriptDir\brain\CLAUDE1.md" $HOME -Force
Copy-Item "$scriptDir\brain\OC.md" $HOME -Force

# Write config
$config = @"
{
  "`$schema": "https://opencode.ai/config.json",
  "username": "ROXX",
  "model": "anthropic/claude-sonnet-4-5",
  "instructions": [
    "$HOME\OC.md",
    "$HOME\CLAUDE.md",
    "$HOME\CLAUDE1.md"
  ],
  "autoapprove": true,
  "permission": "allow",
  "mcp": {},
  "command": {}
}
"@
$config | Out-File -FilePath "$configDir\opencode.jsonc" -Encoding UTF8

$apiKey = Read-Host "[?] Enter your Anthropic API key (get one at console.anthropic.com)"
if ($apiKey) {
    [System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $apiKey, "User")
    Write-Host "[+] API key saved to environment variables ✅" -ForegroundColor Green
}

Write-Host ""
Write-Host "[✅] ROXX'S SLAVE installed! Run 'opencode' in any target directory." -ForegroundColor Green
