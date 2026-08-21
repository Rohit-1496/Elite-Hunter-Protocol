<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0d0d0d,40:1a0000,100:8B0000&height=200&section=header&text=ROXX'S%20SLAVE&fontSize=60&fontColor=FF6600&animation=fadeIn&fontAlignY=40&stroke=FF4400&strokeWidth=2&desc=Autonomous%20Bug%20Bounty%20Hunting%20Intelligence&descAlignY=65&descSize=16&descColor=ff9966"/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=900&size=16&duration=1800&pause=500&color=FF6600&background=0D0D0D&center=true&vCenter=true&width=800&lines=90%25+Mind.+10%25+Tools.+0%25+Mercy.+100%25+Domination.;LOCKED.+LOADED.+UNCHAINED.;One+command.+Everything+set+up.+Ready+to+hunt.;Built+by+Mihir+Shishulkar+%E2%80%94+Microsoft+MSRC+%7C+HackerOne+Top+10%25" alt="Typing"/>

<br/>

<img src="https://img.shields.io/badge/Built_by-Mihir_Shishulkar-FF6600?style=for-the-badge&labelColor=0d0d0d"/>
<img src="https://img.shields.io/badge/Powered_by-OpenCode_AI-494649?style=for-the-badge&labelColor=0d0d0d"/>
<img src="https://img.shields.io/badge/Mode-DEVIL-8B0000?style=for-the-badge&labelColor=0d0d0d"/>
<img src="https://img.shields.io/badge/Status-HUNTING-FF0000?style=for-the-badge&labelColor=0d0d0d"/>

<br/><br/>

<img src="https://img.shields.io/badge/Kali_Linux-557C94?style=for-the-badge&logo=kalilinux&logoColor=white"/>
<img src="https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white"/>
<img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white"/>
<img src="https://img.shields.io/badge/Windows_WSL2-0078D4?style=for-the-badge&logo=windows&logoColor=white"/>
<img src="https://img.shields.io/badge/Parrot_OS-15E0ED?style=for-the-badge&logoColor=black"/>

</div>

---

## ⚡ One Command Install

```bash
git clone https://github.com/mihirshishulkar-SCOPEX/roxxs-slave.git && cd roxxs-slave && chmod +x install.sh && ./install.sh
```

> That's it. Everything installs automatically. API key prompt at the end. Done.

---

## 🧠 What Is This

```
+===========================================================+
|  ROXX'S SLAVE is an autonomous bug bounty hunting        |
|  intelligence layer built on top of OpenCode AI.          |
|                                                           |
|  It loads a battle-tested brain stack of methodology,     |
|  payload libraries, exploit chains and hunting tactics    |
|  directly into your AI coding assistant — turning it      |
|  into a relentless, autonomous vulnerability hunter.      |
|                                                           |
|  Built by Mihir Shishulkar — Microsoft MSRC recognized,  |
|  HackerOne Top 10%, ICAI Critical RCE discovered.         |
+===========================================================+
```

---

## 📂 What's Inside

```
roxxs-slave/
├── install.sh                      ← Linux / Kali / macOS auto-installer
├── install_windows.ps1             ← Windows (PowerShell) installer
├── requirements.txt                ← Full dependency list
│
├── brain/                          ← The AI's core intelligence
│   ├── CLAUDE.md                   ← Primary hunting methodology
│   ├── CLAUDE1.md                  ← Advanced chains & payloads
│   └── OC.md                       ← OpenCode-specific directives
│
└── skills/                         ← Modular skill files
    ├── CAVEMAN_SKILL.md            ← Credit-saving intelligence protocol
    ├── DEVIL_CHAINS.md             ← Pre-built exploit chains (P1 bounties)
    ├── DEVIL_PAYLOADS_ADVANCED.md  ← Advanced payload library
    ├── DEVIL_PAYLOADS_AUTH_SSRF.md ← Auth bypass + SSRF payloads
    ├── DEVIL_PAYLOADS_INJECTION.md ← Injection payloads (SQLi, CMDi, etc.)
    ├── DEVIL_PAYLOADS_XSS.md       ← XSS payload arsenal
    ├── DEVIL_TACTICS.md            ← Hunting tactics & recon patterns
    └── DEVIL_UNIQUE.md             ← Unique attack vectors
```

---

## 🛠️ Installation Guide

### ✅ Kali Linux / Parrot OS / Ubuntu / Debian

```bash
# 1. Clone the repo
git clone https://github.com/mihirshishulkar-SCOPEX/roxxs-slave.git
cd roxxs-slave

# 2. Run installer
chmod +x install.sh
./install.sh

# 3. Reload shell
source ~/.bashrc

# 4. Launch
cd /your/target/recon/folder
opencode
```

### 🍎 macOS

```bash
# 1. Clone the repo
git clone https://github.com/mihirshishulkar-SCOPEX/roxxs-slave.git
cd roxxs-slave

# 2. Run installer (installs Homebrew if not present)
chmod +x install.sh
./install.sh

# 3. Reload shell
source ~/.zshrc

# 4. Launch
cd /your/target/recon/folder
opencode
```

### 🪟 Windows (WSL2 — Recommended)

```powershell
# Step 1: Install WSL2 with Kali (PowerShell Admin)
wsl --install -d kali-linux

# Step 2: Open Kali terminal, then run:
git clone https://github.com/mihirshishulkar-SCOPEX/roxxs-slave.git
cd roxxs-slave
chmod +x install.sh
./install.sh
```

**OR native Windows (PowerShell Admin):**
```powershell
# 1. Clone the repo
git clone https://github.com/mihirshishulkar-SCOPEX/roxxs-slave.git
cd roxxs-slave

# 2. Run Windows installer
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install_windows.ps1
```

---

## 🔑 API Key Setup

You need an **Anthropic API key** (Claude). The installer will prompt you, or set it manually:

```bash
# Linux / macOS / Kali
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.bashrc

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-your-key-here", "User")
```

Get your key at: **[console.anthropic.com](https://console.anthropic.com)**

---

## 📦 What Gets Installed

<div align="center">

| Category | Tools |
|:---|:---|
| **Recon** | Subfinder, Amass, DNSx, Katana, GAU, Waybackurls, Hakrawler |
| **Fuzzing** | ffuf, Gobuster, Naabu, Dirsearch |
| **Scanning** | Nuclei, Nikto, Nmap, OpenVAS |
| **Exploitation** | SQLMap, Hydra, Commix, Interactsh |
| **Monitoring** | Notify, Anew |
| **Proxy** | Burp Suite (manual), Caido |
| **Runtime** | Node.js, Go, Python3, npm |
| **AI Layer** | OpenCode AI + ROXX'S SLAVE brain stack |

</div>

---

## ▶️ How to Use

```bash
# 1. Navigate to your target's recon folder
mkdir -p ~/hunts/target.com && cd ~/hunts/target.com

# 2. Launch ROXX'S SLAVE
opencode

# 3. Give it a target and let it hunt
# Example prompts:
# "Enumerate all subdomains of target.com and find open ports"
# "Run nuclei on these hosts and report criticals"
# "Find IDOR vulnerabilities in this API spec"
# "Generate a full bug bounty report for this finding"
```

---

## 🧠 The Brain Stack

```
OC.md        ← OpenCode directives + autonomous kill mode
CLAUDE.md    ← Primary methodology: recon → exploit → report
CLAUDE1.md   ← Devil mind: deep chains, advanced payloads

CAVEMAN_SKILL     ← Think before spending tokens. Strike once.
DEVIL_CHAINS      ← XSS→ATO, SSRF→RCE, SQLi→Admin — pre-built P1 chains
DEVIL_TACTICS     ← Where to look, what to hit, how to chain
DEVIL_PAYLOADS_*  ← 500+ payloads across all injection categories
DEVIL_UNIQUE      ← Rare vectors most hunters never check
```

---

## ⚠️ Legal Disclaimer

```
This tool is for AUTHORIZED security research and bug bounty hunting ONLY.
Only use against targets you have explicit written permission to test.
The author (Mihir Shishulkar) is not responsible for any misuse.
All findings must be disclosed responsibly.
```

---

## 👤 Built By

<div align="center">

**Mihir Shishulkar** — Elite Vulnerability Researcher

[![LinkedIn](https://img.shields.io/badge/LinkedIn-HOF_Microsoft_MSRC-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/mihir-shishulkar-hof-microsoft-msrc-259978239/)
[![HackerOne](https://img.shields.io/badge/HackerOne-mihir1011-494649?style=for-the-badge&logo=hackerone)](https://hackerone.com/mihir1011)
[![Bugcrowd](https://img.shields.io/badge/Bugcrowd-mihir2004-F26822?style=for-the-badge&logo=bugcrowd)](https://bugcrowd.com/h/mihir2004)
[![MSRC](https://img.shields.io/badge/Microsoft_MSRC-Special_Mention_2026-0078D4?style=for-the-badge&logo=microsoft)](https://msrc.microsoft.com/special-mention)
[![ScopeX](https://img.shields.io/badge/ScopeX-Portfolio-FF6600?style=for-the-badge)](https://mihirshishulkar.lovable.app/)

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=900&size=14&duration=3000&pause=2000&color=FF6600&background=0D0D0D&center=true&vCenter=true&width=600&lines=%22Find.+Exploit.+Report.+Make+it+safer.%22;Microsoft+MSRC+%7C+HackerOne+Top+10%25+%7C+ICAI+RCE" alt="Quote"/>

</div>

---

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:8B0000,40:1a0000,100:0d0d0d&height=100&section=footer&animation=fadeIn&reversal=false"/>
