# ================================================================
#  ROXX'S SLAVE — WINDOWS INSTALLER (PowerShell Admin)
#  Installs OpenCode + embeds all brain & skill files.
# ================================================================

Write-Host @"
 ROXX'S SLAVE — WINDOWS INSTALLER
 LOCKED. LOADED. UNCHAINED.
 Installing OpenCode + Embedding all skills...
"@ -ForegroundColor Red

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigDir = "$HOME\.config\opencode"
$BrainDir  = $HOME

# ── STEP 1: Install Node.js if missing ──────────────────────
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Node.js not found. Installing via winget..." -ForegroundColor Yellow
    winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
}
Write-Host "[+] Node.js: $(node -v)" -ForegroundColor Green

# ── STEP 2: Install OpenCode ────────────────────────────────
Write-Host "[+] Installing OpenCode AI..." -ForegroundColor Green
npm install -g opencode-ai
Write-Host "[+] OpenCode installed ✅" -ForegroundColor Green

# ── STEP 3: Embed Brain + Skills ────────────────────────────
Write-Host "[+] Embedding brain files..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null

Copy-Item "$ScriptDir\brain\CLAUDE.md"  "$BrainDir\CLAUDE.md"  -Force
Copy-Item "$ScriptDir\brain\CLAUDE1.md" "$BrainDir\CLAUDE1.md" -Force
Copy-Item "$ScriptDir\brain\OC.md"      "$BrainDir\OC.md"      -Force

Write-Host "[+] Embedding skill files..." -ForegroundColor Green
Get-ChildItem "$ScriptDir\skills\*.md" | ForEach-Object {
    Copy-Item $_.FullName $ConfigDir -Force
    Write-Host "    ✅ $($_.Name)" -ForegroundColor Green
}

# ── STEP 4: Write Config ────────────────────────────────────
Write-Host "[+] Writing OpenCode config..." -ForegroundColor Green
$config = @"
{
  "`$schema": "https://opencode.ai/config.json",
  "username": "ROXX",
  "model": "anthropic/claude-sonnet-4-5",
  "instructions": [
    "$BrainDir\\OC.md",
    "$BrainDir\\CLAUDE.md",
    "$BrainDir\\CLAUDE1.md"
  ],
  "autoapprove": true,
  "permission": "allow",
  "mcp": {},
  "command": {}
}
"@
$config | Out-File -FilePath "$ConfigDir\opencode.jsonc" -Encoding UTF8
Write-Host "[+] Config written ✅" -ForegroundColor Green

# ── DONE ────────────────────────────────────────────────────
Write-Host ""
Write-Host "══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ROXX'S SLAVE — INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Next: Launch OpenCode and connect your API key" -ForegroundColor White
Write-Host "  Run:  opencode" -ForegroundColor Cyan
Write-Host "  Then: /connect   (inside OpenCode)" -ForegroundColor Cyan
Write-Host ""
Write-Host "  FREE API key: https://aistudio.google.com/apikey" -ForegroundColor Yellow
Write-Host ""
