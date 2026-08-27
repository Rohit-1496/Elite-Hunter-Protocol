#!/usr/bin/env python3
"""
hunt.py — ELITE HUNTER PROTOCOL Orchestrator
Single script: recon → JS deep dive → extract → vuln hunt → report
Modes: DEVIL (default), GHOST, REAPER, SOVEREIGN, SHADOW
"""
import asyncio, json, os, re, sys, hashlib, subprocess, shutil, time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set
import aiohttp

BASE = Path.home() / "hunts"
SOURCE_MAP_CMD = ["npx", "source-map-explorer", "--no-border-checks"]  # fallback

# ─── MODE ──────────────────────────────────────────────────────────────
def get_mode() -> str:
    mode_file = Path("/tmp/.devil_mode")
    if mode_file.exists():
        return mode_file.read_text().strip().upper()
    return "DEVIL MODE"

MODE = get_mode()

# ─── CONFIG PER MODE ───────────────────────────────────────────────────
MODE_CONFIG = {
    "DEVIL MODE":   {"aggressive": True, "parallel": True, "rate": 50, "tiers": [1,2,3,4,5,6], "secrets_only": False, "auto_report": True},
    "GHOST MODE":   {"aggressive": False, "parallel": False, "rate": 5, "tiers": [1,2], "secrets_only": False, "auto_report": False},
    "REAPER MODE":  {"aggressive": True, "parallel": True, "rate": 100, "tiers": [1,3], "secrets_only": True, "auto_report": True},
    "SOVEREIGN MODE": {"aggressive": False, "parallel": False, "rate": 10, "tiers": [], "secrets_only": False, "auto_report": False},
    "SHADOW MODE":  {"aggressive": False, "parallel": False, "rate": 10, "tiers": [5], "secrets_only": False, "auto_report": False},
}
CFG = MODE_CONFIG.get(MODE, MODE_CONFIG["DEVIL MODE"])

# ─── STATE ─────────────────────────────────────────────────────────────
@dataclass
class TargetState:
    target: str
    scope: Path
    recon: Path
    js_raw: Path
    js_src: Path
    maps: Path
    extraction: Path
    vuln: Path
    cleared: Path

    @classmethod
    def create(cls, target: str) -> "TargetState":
        base = BASE / target
        dirs = {
            "scope": base / "scope",
            "recon": base / "recon",
            "js_raw": base / "js" / "js_raw",
            "js_src": base / "js" / "js_src",
            "maps": base / "js" / "maps",
            "extraction": base / "js" / "extraction",
            "vuln": base / "vuln",
        }
        for d in dirs.values():
            d.mkdir(parents=True, exist_ok=True)
        return cls(
            target=target,
            scope=dirs["scope"],
            recon=dirs["recon"],
            js_raw=dirs["js_raw"],
            js_src=dirs["js_src"],
            maps=dirs["maps"],
            extraction=dirs["extraction"],
            vuln=dirs["vuln"],
            cleared=base / "cleared.txt",
        )

# ─── UTIL ──────────────────────────────────────────────────────────────
async def run(cmd: List[str], cwd: Path = None, timeout: int = 120) -> tuple[int, str, str]:
    try:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd)
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode, out.decode(errors="ignore"), err.decode(errors="ignore")
    except asyncio.TimeoutError:
        return -1, "", f"timeout after {timeout}s"
    except Exception as e:
        return -1, "", str(e)

async def download(session: aiohttp.ClientSession, url: str, dest: Path, retries: int = 3) -> bool:
    for i in range(retries):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    dest.write_bytes(data)
                    return True
        except Exception:
            await asyncio.sleep(1 * (i + 1))
    return False

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]

# ─── PHASE 1: RECON ────────────────────────────────────────────────────
async def phase_recon(state: TargetState):
    print(f"[{MODE}] Phase 1: Recon on {state.target}")
    # Passive subdomain enum
    tasks = [
        run(["subfinder", "-d", state.target, "-o", str(state.recon / "subs_subfinder.txt"), "-silent"], timeout=60),
        run(["assetfinder", "--subs-only", state.target], cwd=state.recon, timeout=30),
        run(["findomain", "-t", state.target, "-q", "-o", str(state.recon / "subs_findomain.txt")], timeout=60),
    ]
    await asyncio.gather(*tasks, return_exceptions=True)
    # Merge
    all_subs = set()
    for f in state.recon.glob("subs_*.txt"):
        all_subs.update(f.read_text().splitlines())
    (state.recon / "hosts.txt").write_text("\n".join(sorted(all_subs)))
    # Live check
    await run(["httpx", "-l", str(state.recon / "hosts.txt"), "-title", "-tech-detect", "-status-code", "-server", "-location", "-csp-probe", "-silent", "-o", str(state.recon / "live.txt")], timeout=120)
    live_file = state.recon / "live.txt"
    live = live_file.read_text().splitlines() if live_file.exists() else []
    (state.recon / "live_hosts.txt").write_text("\n".join(l.split()[0] for l in live if l.strip()))
    print(f"  Live hosts: {len(live)}")
    if not live:
        print("  No live hosts found, skipping JS deep dive")
        return

# ─── PHASE 2: JS DEEP DIVE ─────────────────────────────────────────────
JS_CRAWLERS = ["katana", "gospider", "hakrawler", "subjs", "getJS"]
MAP_PATHS = ["/static/js/", "/webpack/", "/assets/", "/build/", "/dist/", "/js/", "/static/"]

async def phase_js_deep_dive(state: TargetState):
    print(f"[{MODE}] Phase 2: JS/SourceMap Deep Dive")
    live_hosts = (state.recon / "live_hosts.txt").read_text().splitlines()
    all_js_urls: Set[str] = set()
    all_map_urls: Set[str] = set()

    # Crawl for JS
    async with aiohttp.ClientSession() as session:
        for host in live_hosts:
            safe = host.replace('://','_').replace('/','_')
            await run(["katana", "-u", host, "-js-crawl", "-d", "3", "-silent", "-o", str(state.recon / f"katana_{safe}.txt")], timeout=120)
            await run(["gospider", "-s", host, "-d", "2", "-o", str(state.recon / f"gospider_{safe}")], timeout=120)
            await run(["hakrawler", "-url", host, "-depth", "3", "-insecure", "-o", str(state.recon / f"hakrawler_{safe}.txt")], timeout=120)

        # Collect JS URLs
        for f in state.recon.glob("*.txt"):
            content = f.read_text(errors="ignore")
            for url in re.findall(r'https?://[^\s"\'<>]+\.js(?:\?[^\s"\'<>]*)?', content):
                all_js_urls.add(url)
            # Find .map references in JS
            for js_url in list(all_js_urls):
                try:
                    async with session.get(js_url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                        if r.status == 200:
                            js_text = await r.text()
                            for m in re.findall(r'//#\s*sourceMappingURL=([^\s\n]+)', js_text):
                                map_url = m if m.startswith("http") else js_url.rsplit("/",1)[0] + "/" + m
                                all_map_urls.add(map_url)
                except:
                    pass

        # Bruteforce common .map paths
        for host in live_hosts:
            for mp in MAP_PATHS:
                for ext in [".js.map", ".min.js.map"]:
                    all_map_urls.add(host.rstrip("/") + mp + "*" + ext)

        # Download JS
        print(f"  Downloading {len(all_js_urls)} JS files...")
        sem = asyncio.Semaphore(20 if CFG["parallel"] else 5)
        async def dl_js(url):
            async with sem:
                fname = url.split("/")[-1].split("?")[0]
                dest = state.js_raw / fname
                if not dest.exists():
                    await download(session, url, dest)
        await asyncio.gather(*[dl_js(u) for u in list(all_js_urls)[:50]], return_exceptions=True)

        # Download .map
        print(f"  Downloading {len(all_map_urls)} source maps...")
        async def dl_map(url):
            async with sem:
                fname = url.split("/")[-1].split("?")[0]
                dest = state.maps / fname
                if not dest.exists():
                    await download(session, url, dest)
        await asyncio.gather(*[dl_map(u) for u in list(all_map_urls)[:20]], return_exceptions=True)

    # Recover source from .map
    print("  Recovering source from .map files...")
    for map_file in state.maps.glob("*.map"):
        js_name = map_file.stem.replace(".map", "")
        out_dir = state.js_src / js_name
        out_dir.mkdir(exist_ok=True)
        # Use source-map library via node
        await run(["node", "-e", f"""
const fs = require('fs');
const sourceMap = require('source-map');
const raw = fs.readFileSync('{map_file}', 'utf8');
const smc = JSON.parse(raw);
const consumer = await new sourceMap.SourceMapConsumer(smc);
consumer.eachMapping(m => {{
  if (m.originalLine && m.name) {{
    console.log(JSON.stringify({{line: m.originalLine, col: m.originalColumn, name: m.name, source: m.source}}));
  }}
}});
"""], cwd=state.maps, timeout=30)
        # Fallback: source-map-explorer
        await run(SOURCE_MAP_CMD + [str(map_file), "--output", str(out_dir)], timeout=60)

    # Deobfuscate minified JS
    print("  Deobfuscating minified JS...")
    for js_file in state.js_raw.glob("*.js"):
        out_file = state.js_src / js_file.name
        if not out_file.exists():
            await run(["npx", "prettier", "--write", "--parser", "babel", str(js_file), "--output", str(out_file)], timeout=60)

    # Inventory
    inv = []
    for f in state.js_raw.glob("*.js"):
        src = state.js_src / f.name
        has_map = (state.maps / (f.stem + ".map")).exists()
        inv.append(f"{f.name}|{f.stat().st_size}|minified|map:{has_map}|src:{src.exists()}")
    (state.js_raw.parent / "js_inventory.md").write_text("\n".join(inv))

# ─── PHASE 3: EXTRACTION ───────────────────────────────────────────────
SECRET_PATTERNS = [
    (r'(?i)(aws_access_key_id|aws_secret_access_key)\s*[:=]\s*["\']?([A-Z0-9/+=]{20,})', "AWS_KEY"),
    (r'(?i)(google|gcp)_?api_?key\s*[:=]\s*["\']?([A-Za-z0-9_-]{30,})', "GCP_KEY"),
    (r'(?i)azure_?(client_?id|client_?secret|tenant_?id)\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})', "AZURE_CREDS"),
    (r'(?i)(jwt_?secret|secret_?key|api_?secret|private_?key)\s*[:=]\s*["\']?([A-Za-z0-9/+=_-]{20,})', "JWT_SECRET"),
    (r'(?i)(database_?url|db_?connection|mongodb_?uri|postgres_?url)\s*[:=]\s*["\']?([^\s"\']{20,})', "DB_URL"),
    (r'(?i)(firebase_?config|apiKey|authDomain|projectId|storageBucket|messagingSenderId|appId)\s*[:=]', "FIREBASE_CONFIG"),
    (r'(?i)cognito_?(user_?pool|client_?id|identity_?pool)\s*[:=]\s*["\']?([A-Za-z0-9_-]{10,})', "COGNITO_CONFIG"),
]

ENDPOINT_PATTERNS = [
    r'/api/v\d+/[^\s"\'<>]{3,}',
    r'/graphql',
    r'/webhook',
    r'/internal/[^\s"\'<>]{3,}',
    r'/admin/[^\s"\'<>]{3,}',
    r'/debug/[^\s"\'<>]{3,}',
    r'/actuator/[^\s"\'<>]{3,}',
    r'/\.well-known/[^\s"\'<>]{3,}',
    r'/ws/[^\s"\'<>]{3,}',
]

SINK_PATTERNS = [
    (r'\.innerHTML\s*=', "innerHTML"),
    (r'\.outerHTML\s*=', "outerHTML"),
    (r'eval\s*\(', "eval"),
    (r'Function\s*\(', "Function"),
    (r'postMessage\s*\(', "postMessage"),
    (r'fetch\s*\(', "fetch"),
    (r'axios\s*\.(get|post|put|delete|patch)\s*\(', "axios"),
    (r'dangerouslySetInnerHTML', "dangerouslySetInnerHTML"),
    (r'v-html\s*=', "v-html"),
]

XSS_SOURCE_PATTERNS = [
    (r'location\.(hash|search|href|pathname)', "location"),
    (r'document\.referrer', "referrer"),
    (r'window\.name', "window.name"),
    (r'URLSearchParams', "URLSearchParams"),
    (r'postMessage\s*\(', "postMessage"),
]

PROTO_POLLUTION_PATTERNS = [
    (r'__proto__\s*[\[.=]', "__proto__"),
    (r'constructor\.prototype\s*[\[.=]', "constructor.prototype"),
    (r'Object\.assign\s*\(', "Object.assign"),
    (r'\$\.extend\s*\(', "$.extend"),
]

def extract_from_file(js_path: Path) -> Dict:
    text = js_path.read_text(errors="ignore")
    lines = text.splitlines()
    findings = {"secrets": [], "endpoints": [], "sinks": [], "xss_sources": [], "proto_pollution": []}
    for i, line in enumerate(lines, 1):
        for pat, label in SECRET_PATTERNS:
            for m in re.finditer(pat, line):
                findings["secrets"].append({"line": i, "type": label, "match": m.group(0)[:100]})
        for pat in ENDPOINT_PATTERNS:
            for m in re.finditer(pat, line):
                findings["endpoints"].append({"line": i, "url": m.group(0)})
        for pat, label in SINK_PATTERNS:
            if re.search(pat, line):
                findings["sinks"].append({"line": i, "type": label, "context": line.strip()[:120]})
        for pat, label in XSS_SOURCE_PATTERNS:
            if re.search(pat, line):
                findings["xss_sources"].append({"line": i, "type": label, "context": line.strip()[:120]})
        for pat, label in PROTO_POLLUTION_PATTERNS:
            if re.search(pat, line):
                findings["proto_pollution"].append({"line": i, "type": label, "context": line.strip()[:120]})
    # Priority
    pri = "LOW"
    if findings["secrets"]: pri = "CRITICAL"
    elif findings["sinks"] and findings["xss_sources"]: pri = "HIGH"
    elif findings["endpoints"]: pri = "MEDIUM"
    findings["priority"] = pri
    return findings

async def phase_extract(state: TargetState):
    print(f"[{MODE}] Phase 3: Extraction")
    all_js = list(state.js_raw.glob("*.js")) + list(state.js_src.rglob("*.js"))
    for js_file in all_js:
        rel = js_file.relative_to(state.js_raw) if js_file.is_relative_to(state.js_raw) else js_file.relative_to(state.js_src)
        findings = extract_from_file(js_file)
        # Write per-file report
        report = state.extraction / f"{rel.stem}_report.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# JS Analysis: {rel}", f"- Source: {js_file}", f"- Size: {js_file.stat().st_size} bytes", f"- Priority: {findings['priority']}", ""]
        for cat in ["secrets", "endpoints", "sinks", "xss_sources", "proto_pollution"]:
            if findings[cat]:
                lines.append(f"## {cat.title().replace('_', ' ')}")
                for f in findings[cat]:
                    lines.append(f"- Line {f['line']}: {f.get('type', '')} {f.get('match', f.get('url', f.get('context', '')))}")
                lines.append("")
        lines.append("## Next Tests")
        if findings["endpoints"]:
            for ep in findings["endpoints"][:5]:
                lines.append(f"- IDOR/SSRF on {ep['url']}")
        if findings["sinks"] and findings["xss_sources"]:
            lines.append("- XSS: source → sink chain")
        if findings["secrets"]:
            lines.append("- Validate secret usage in auth/SSRF")
        report.write_text("\n".join(lines))

# ─── PHASE 4: VULN HUNT (simplified - calls external tools) ────────────
async def phase_hunt(state: TargetState):
    print(f"[{MODE}] Phase 4: Vuln Hunt (tiers {CFG['tiers']})")
    # This is a placeholder - real implementation calls nuclei, dalfox, sqlmap, etc.
    # For now, create hypotheses file
    hyp = state.vuln / "hypotheses.md"
    hyp.write_text("\n".join([
        "# Hypotheses",
        "1. JWT alg:none on /api/auth endpoints",
        "2. IDOR on /api/v2/users/{id} - test cross-account access",
        "3. SSRF on /webhook endpoint - test cloud metadata",
        "4. XSS in admin panel via stored payload in JS sink",
        "5. Race condition on /api/coupon/apply - 50 parallel requests",
    ]))

# ─── MAIN ──────────────────────────────────────────────────────────────
async def main():
    if len(sys.argv) < 3:
        print("Usage: hunt.py <target> <recon|extract|hunt|all>")
        return
    target, phase = sys.argv[1], sys.argv[2]
    state = TargetState.create(target)

    if phase in ("recon", "all"):
        await phase_recon(state)
    if phase in ("js", "all"):
        await phase_js_deep_dive(state)
    if phase in ("extract", "all"):
        await phase_extract(state)
    if phase in ("hunt", "all"):
        await phase_hunt(state)
    print(f"[{MODE}] Done. State at {BASE/target}")

if __name__ == "__main__":
    asyncio.run(main())