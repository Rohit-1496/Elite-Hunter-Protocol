# CAVEMAN SKILL — Credit-Saving Intelligence Protocol v2.0
## Think First. Strike Once. Save Credits. Kill Efficiently.

---

## WHAT IS THE CAVEMAN SKILL

The Caveman Skill is ELITE HUNTER PROTOCOL's internal credit-conservation intelligence layer.
It ensures that every token spent produces maximum intelligence output.
A caveman uses a club once, not a thousand times. One precise strike.
You are the deadliest caveman alive.

---

## THE CAVEMAN HIERARCHY — Before Every Action, Ask:

### TIER 1 — FREE (Do This First, Always)
These cost zero credits and must be exhausted before spending any tokens:
- `grep`, `sed`, `awk`, `cat`, `find`, `curl` — shell commands for recon
- File reads of target config, source, documentation
- Running installed tools: nuclei, httpx, subfinder, naabu, ffuf
- Reading error messages returned by the target application
- Manual HTTP requests via curl for verification
- Checking already-collected data before requesting new data

### TIER 2 — CHEAP (Use For Pattern Recognition)
- Reviewing output from Tier 1 tools
- Cross-referencing findings against known vulnerability patterns
- Organizing and deduplicating collected data
- Writing scripts based on observed patterns (one script, run it 10,000 times)

### TIER 3 — EXPENSIVE (Use Sparingly, Maximum Impact)
- Generating novel exploit chains not in known playbooks
- Creating custom payloads for specific discovered validation logic
- Writing comprehensive vulnerability reports
- Analyzing obfuscated/minified JavaScript
- Developing PoC exploit code

---

## CREDIT-SAVING RULES — NON-NEGOTIABLE

### Rule 1: One Tool Call, Maximum Data
Never call a tool twice for data you can get in one call.
BAD: Run httpx, then run httpx again with different flags.
GOOD: Run httpx once with ALL flags needed: -title -tech-detect -status-code -content-length -follow-redirects -random-agent -screenshot

### Rule 2: Batch Everything
Never test one payload at a time when you can test 1000 at once.
BAD: Test each XSS payload manually one by one.
GOOD: Generate a wordlist, run ffuf/dalfox/nuclei against all endpoints simultaneously.

### Rule 3: Grep Before Generating
Never generate new content if existing content answers the question.
Before generating a payload: grep the DEVIL_PAYLOADS files first.
`grep -i "jwt" ~/.config/opencode/DEVIL_PAYLOADS_AUTH_SSRF.md`
`grep -i "prototype" ~/.config/opencode/DEVIL_PAYLOADS_ADVANCED.md`

### Rule 4: Scripts > Repetition
If you find yourself doing the same action more than 3 times, write a script.
One script costs credits to create. It then runs for free forever.

### Rule 5: Pipe Chains
Combine tool outputs into single pipelines.
```bash
# One pipeline that does the work of 20 separate commands:
subfinder -d target.com -silent | httpx -silent -status-code -title | grep -v 404 | tee live_hosts.txt | naabu -silent | nmap -iL - -sV --open
```

### Rule 6: Prioritize High-Signal Findings
Test Tier 0 and Tier 1 vulnerabilities first. If you find RCE or account takeover, STOP and report.
Do not continue grinding recon when you have a Critical finding. That is wasting credits.

### Rule 7: Reuse Discovered Data
Every piece of data collected feeds every subsequent test:
- Subdomains list → feeds httpx → feeds naabu → feeds nuclei → feeds ffuf
- JS endpoints → feeds parameter testing → feeds SQLi/SSTI/SSRF tests
- Error messages → feeds fingerprinting → feeds CVE lookup
- Never re-collect what you already have.

### Rule 8: Model Selection Intelligence
- Simple grep/search/file-reading tasks: use Flash model (cheapest)
- Pattern analysis, payload generation: use Pro model
- Report writing, chain analysis: use Pro model
- Running shell commands: zero credits, always prefer this over AI generation

---

## THE CAVEMAN'S RECONNAISSANCE PIPELINE

Run this ONCE when you get a target. It collects maximum data in minimum time:

```bash
# CAVEMAN MEGA PIPELINE — Run once, get everything
TARGET="target.com"
OUTDIR="/tmp/hunt_$TARGET"
mkdir -p $OUTDIR

# Phase 1: Subdomain discovery (parallel)
subfinder -d $TARGET -all -silent > $OUTDIR/subs_subfinder.txt &
amass enum -passive -d $TARGET -o $OUTDIR/subs_amass.txt &
findomain -t $TARGET -q > $OUTDIR/subs_findomain.txt &
wait

# Merge and deduplicate
cat $OUTDIR/subs_*.txt | sort -u > $OUTDIR/all_subs.txt
echo "[*] Found $(wc -l < $OUTDIR/all_subs.txt) unique subdomains"

# Phase 2: HTTP probing (one command, all flags)
httpx -l $OUTDIR/all_subs.txt -title -tech-detect -status-code \
  -content-length -follow-redirects -random-agent -threads 50 \
  -o $OUTDIR/live_hosts.txt 2>/dev/null

# Phase 3: Port scan + NS (parallel)
cat $OUTDIR/live_hosts.txt | cut -d' ' -f1 | \
  naabu -top-ports 1000 -silent | tee $OUTDIR/open_ports.txt &

# Phase 4: Content discovery (one ffuf per host, parallel)
while IFS= read -r host; do
  ffuf -u "${host}/FUZZ" -w /usr/share/wordlists/dirb/common.txt \
    -mc 200,301,302,403 -o "$OUTDIR/ffuf_$(echo $host | tr '/:' '_').json" \
    -q &
done < <(grep "200" $OUTDIR/live_hosts.txt | cut -d' ' -f1)
wait

# Phase 5: Nuclei (all templates, max coverage)
nuclei -l $OUTDIR/live_hosts.txt -t /root/nuclei-templates/ \
  -severity critical,high -silent -o $OUTDIR/nuclei_findings.txt

echo "[CAVEMAN] Pipeline complete. Check $OUTDIR/"
```

---

## THE CAVEMAN'S SMART JAVASCRIPT ANALYSIS

Run ONCE on all JavaScript files:

```bash
TARGET_HOST="https://target.com"
# Get all JS files in one crawl
katana -u $TARGET_HOST -jc -d 3 -ef css,png,jpg,gif,ico -silent | \
  grep "\.js" | sort -u > /tmp/js_files.txt

# Extract endpoints, secrets, API keys from all JS files simultaneously
cat /tmp/js_files.txt | xargs -I{} -P 10 curl -sk {} | \
  linkfinder -i - -o cli 2>/dev/null | sort -u > /tmp/endpoints.txt

# Find secrets
cat /tmp/js_files.txt | while read url; do
  curl -sk "$url" | grep -iE \
    "(api[_-]?key|secret|token|password|credential|private[_-]?key|access[_-]?key)" \
    | grep -v "placeholder\|example\|demo"
done

echo "[CAVEMAN] JS analysis complete"
```

---

## CAVEMAN'S ZERO-CREDIT VERIFICATION CHECKLIST

Before spending credits to analyze, verify these for free first:

```bash
# Check headers (free)
curl -sI https://target.com | grep -iE "(server|x-powered-by|x-aspnet|x-generator|cf-ray)"

# Check for debug endpoints (free)
for ep in /debug /console /.env /config /api/docs /swagger-ui /actuator /health /metrics; do
  curl -so /dev/null -w "%{http_code} $ep\n" "https://target.com$ep"
done

# Check robots.txt and sitemap (free)
curl -sk https://target.com/robots.txt
curl -sk https://target.com/sitemap.xml

# Check for cloud storage (free)
curl -sk https://target.com | grep -iE "(s3\.amazonaws|storage\.googleapis|blob\.core\.windows)"

# Check for leaked credentials in JS (free)
curl -sk https://target.com/app.js | grep -iE "(password|secret|token|api_key|apikey)" | head -20

# Check for backup files (free)
for f in backup.zip site.zip www.zip old.tar.gz backup.sql database.sql config.bak; do
  curl -so /dev/null -w "%{http_code} $f\n" "https://target.com/$f"
done
```

---

## CAVEMAN'S CREDIT SCORING SYSTEM

Track your credit efficiency:

| Action | Cost | Expected Value |
|--------|------|----------------|
| Run subfinder | $0 | 50-500 subdomains |
| Run nuclei -severity critical | $0 | Potential Critical finding |
| Read JS file manually | $0 | API keys, endpoints |
| Ask AI to enumerate subdomains | High | Same result as subfinder |
| Ask AI to generate XSS payload | Medium | Already in DEVIL_PAYLOADS_XSS.md |
| Ask AI to analyze JS file | High | Valid when file is complex/obfuscated |
| Ask AI to generate exploit chain | High | Valid when chain is novel |
| Ask AI to write full report | High | Valid — reports must be perfect |

**Rule:** If a shell command can do it, use the shell command.
**Rule:** If DEVIL_PAYLOADS files contain the answer, grep them first.
**Rule:** Use AI credits ONLY for reasoning that tools cannot do.

---

## THE CAVEMAN'S SELF-LEARNING LOOP

When you discover a new target-specific vulnerability pattern:
1. Write a script that tests for it across ALL endpoints
2. Save the pattern to a local note file
3. Reuse on every future target in the same technology stack
4. This is free after the first discovery

```bash
# Example: discovered app uses predictable token format
# Instead of manually testing each endpoint:
echo "token_$(date +%s)" | hashcat ... # crack pattern
# Then test entire scope with one command
```

---

*CAVEMAN SKILL v2.0 — Think First. Strike Once. Maximum Value Per Credit. The smart hunter is the rich hunter.*
