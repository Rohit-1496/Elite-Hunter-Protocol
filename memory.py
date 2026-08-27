#!/usr/bin/env python3
"""
HUNTER BRAIN v2 — hippocampus
Persistent long-term memory tooling for the Elite Hunter Protocol.

Brain file : ~/.config/opencode/MEMORY.md   (override: env HUNTER_MEMORY)
Protocol   : ~/.config/opencode/LEARNING_PROTOCOL.md (auto-loaded by opencode)

Sections in brain file (fixed order, do not rename):
  DISTILLED  auto-generated top-wisdom block      (`distill`)
  STATE      current hunt handoff lines           (`state`)
  HOT        live entries                          (ranked recall)
  COLD       stale entries sunk by `compact`       (searchable, ranked lower)

Entry line format (single line, grep-able):
  [ID|YYYY-MM-DD|TYPE|CONF=0.90|TARGET=x|TECH=y|REF=ID|H=hash] free text

Types / id prefixes:
  LESSON L-####   PATTERN P-####   FP F-####   PRED PR-####   PROFILE PF-####

Learning loop:
  pred -> test -> confirm (pattern CONF +0.10, cap 0.95)
              -> reject   (pattern CONF -0.15, floor 0.05)   [anti-overconfidence bias]
"""

import argparse
import hashlib
import os
import re
import sys
from datetime import date, datetime

MEM_PATH = os.environ.get(
    "HUNTER_MEMORY", os.path.expanduser("~/.config/opencode/MEMORY.md")
)

SECTIONS = ["DISTILLED", "STATE", "HOT", "COLD"]
TYPE_PREFIX = {"LESSON": "L", "PATTERN": "P", "FP": "F", "PRED": "PR", "PROFILE": "PF"}
DEFAULT_CONF = {"LESSON": 0.5, "PATTERN": 0.5, "FP": 0.8, "PROFILE": 0.7, "PRED": None}
STALE_DAYS = 60          # age after which low-conf entries sink to COLD
STALE_MIN_CONF = 0.6     # conf below this + old = cold
PRED_STALE_DAYS = 30     # unresolved predictions older than this sink to COLD

HEADER = """# ╔══════════════════════════════════════════════════════╗
# HUNTER BRAIN v2 — GLOBAL LONG-TERM MEMORY
# Managed by memory.py · Governed by LEARNING_PROTOCOL.md
# Sections: DISTILLED | STATE | HOT | COLD  (fixed — do not rename)
# ╚══════════════════════════════════════════════════════╝
"""

ENTRY_RE = re.compile(
    r"^\[(?P<id>[A-Z]{1,2}-\d+)\|(?P<date>\d{4}-\d{2}-\d{2})\|(?P<type>[A-Z]+)"
    r"(?:\|CONF=(?P<conf>[01]\.\d+))?"
    r"(?:\|TARGET=(?P<target>[^\]|]*))?"
    r"(?:\|TECH=(?P<tech>[^\]|]*))?"
    r"(?:\|REF=(?P<ref>[^\]|]*))?"
    r"(?:\|H=(?P<h>[0-9a-f]{8}))?\]\s?(?P<text>.*)$"
)


# ---------------------------------------------------------------- model
def load():
    """Return {section: [(kind, payload), ...]} where kind='raw'|'entry'."""
    data = {s: [] for s in SECTIONS}
    cur = None
    if not os.path.exists(MEM_PATH):
        return data
    with open(MEM_PATH, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            m = re.match(r"^=== (\w+) ===", line.strip())
            if m and m.group(1) in SECTIONS:
                cur = m.group(1)
                continue
            if cur is None:
                continue  # header/comments above first section
            e = parse_entry(line)
            if e:
                data[cur].append(("entry", e))
            elif line.strip() and line.strip() != "(empty)":
                data[cur].append(("raw", line))
    return data


def save(data):
    os.makedirs(os.path.dirname(MEM_PATH), exist_ok=True)
    out = [HEADER]
    for s in SECTIONS:
        out.append(f"=== {s} ===")
        body = data[s]
        if not body:
            out.append("(empty)")
        for kind, item in body:
            out.append(serialize(item) if kind == "entry" else item)
        out.append("")
    with open(MEM_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


def parse_entry(line):
    m = ENTRY_RE.match(line.strip())
    if not m:
        return None
    g = m.groupdict()
    return {
        "id": g["id"],
        "date": g["date"],
        "type": g["type"],
        "conf": float(g["conf"]) if g["conf"] else None,
        "target": g["target"] or "",
        "tech": g["tech"] or "",
        "ref": g["ref"] or "",
        "h": g["h"] or "",
        "text": g["text"].strip(),
    }


def serialize(e):
    parts = [e["id"], e["date"], e["type"]]
    if e["conf"] is not None:
        parts.append(f"CONF={e['conf']:.2f}")
    if e["target"]:
        parts.append(f"TARGET={e['target']}")
    if e["tech"]:
        parts.append(f"TECH={e['tech']}")
    if e["ref"]:
        parts.append(f"REF={e['ref']}")
    if e["h"]:
        parts.append(f"H={e['h']}")
    return f"[{('|'.join(parts))}] {e['text']}"


def all_entries(data):
    for sec in ("HOT", "COLD"):
        for kind, item in data[sec]:
            if kind == "entry":
                yield sec, item


def next_id(data, etype):
    prefix = TYPE_PREFIX[etype]
    used = {e["id"] for _, e in all_entries(data)}
    n = 1
    while f"{prefix}-{n:04d}" in used:
        n += 1
    return f"{prefix}-{n:04d}"


def text_hash(etype, text):
    norm = re.sub(r"\s+", " ", f"{etype}:{text}".lower().strip())
    return hashlib.sha1(norm.encode()).hexdigest()[:8]


def days_old(iso_date):
    try:
        d = datetime.strptime(iso_date, "%Y-%m-%d").date()
    except ValueError:
        return 0
    return max(0, (date.today() - d).days)


def recency(iso_date):
    return 1.0 / (1.0 + days_old(iso_date) / 30.0)


# ---------------------------------------------------------------- commands
def cmd_init(force):
    if os.path.exists(MEM_PATH) and not force:
        sys.exit(f"[ABORT] {MEM_PATH} exists — use --force to reset.")
    seed = {
        "DISTILLED": [("raw", "(empty — regenerates via `memory.py distill`)")],
        "STATE": [("raw", "(no active hunt)")],
        "HOT": [
            (
                "entry",
                {
                    "id": "L-0001",
                    "date": date.today().isoformat(),
                    "type": "LESSON",
                    "conf": 0.95,
                    "target": "",
                    "tech": "",
                    "ref": "",
                    "h": text_hash("LESSON", "brain initialized"),
                    "text": "Hunter Brain v2 operational — every hunt feeds this file.",
                },
            )
        ],
        "COLD": [],
    }
    save(seed)
    print(f"[OK] brain initialized → {MEM_PATH}")


def _add(data, etype, text, target="", tech="", conf=None, ref="", iso=None):
    h = text_hash(etype, text)
    for _, e in all_entries(data):
        if e["h"] == h:
            print(f"[DUP] identical {etype} already stored as {e['id']} — rejected.")
            return False
    entry = {
        "id": next_id(data, etype),
        "date": iso or date.today().isoformat(),
        "type": etype,
        "conf": round(conf, 2) if conf is not None else DEFAULT_CONF[etype],
        "target": target,
        "tech": tech,
        "ref": ref,
        "h": h,
        "text": text.strip(),
    }
    data["HOT"].append(("entry", entry))
    save(data)
    print(f"[OK] {serialize(entry)}")
    return True


def cmd_add(a):
    data = load()
    _add(
        data,
        a.kind.upper(),
        a.text,
        target=a.target,
        tech=a.tech,
        conf=a.conf,
        ref=a.ref,
        iso=a.date,
    )


def cmd_fp(a):
    data = load()
    _add(data, "FP", a.text, target=a.target, iso=a.date)


def cmd_pred(a):
    data = load()
    _add(data, "PRED", a.text, target=a.target, ref=a.ref, iso=a.date)


def _find_entry(data, eid):
    for sec in ("HOT", "COLD"):
        for i, (kind, item) in enumerate(data[sec]):
            if kind == "entry" and item["id"] == eid:
                return sec, i, item
    return None


def _outcome(pred_id, marker, delta, cap_floor):
    data = load()
    hit = _find_entry(data, pred_id)
    if not hit:
        sys.exit(f"[ERR] prediction {pred_id} not found.")
    sec, i, pred = hit
    if "✓" in pred["text"] or "✗" in pred["text"]:
        sys.exit(f"[ABORT] {pred_id} already resolved.")
    pred["text"] += f" {marker}"
    msg = f"[OK] {pred_id} marked {marker}"
    if pred["ref"]:
        ref_hit = _find_entry(data, pred["ref"])
        if ref_hit:
            rsec, ri, pat = ref_hit
            old = pat["conf"] or DEFAULT_CONF.get(pat["type"], 0.5) or 0.5
            new = old + delta
            if cap_floor[1] is not None:
                new = min(cap_floor[1], new)
            if cap_floor[0] is not None:
                new = max(cap_floor[0], new)
            pat["conf"] = round(new, 2)
            msg += f" | {pat['id']} CONF {old:.2f}→{new:.2f}"
        else:
            msg += f" | ref {pred['ref']} not found (skipped)"
    else:
        msg += " | no linked pattern"
    save(data)
    print(msg)


def cmd_confirm(a):
    _outcome(a.pred_id, "✓CONFIRMED", +0.10, (None, 0.95))


def cmd_reject(a):
    _outcome(a.pred_id, "✗REJECTED", -0.15, (0.05, None))


def cmd_recall(a):
    data = load()
    if a.last:
        print("=== STATE ===")
        for kind, item in data["STATE"]:
            print(f"  {item}")
        recent = sorted(all_entries(data), key=lambda t: t[1]["date"], reverse=True)
        print("=== LAST ENTRIES ===")
        for sec, e in recent[:8]:
            print(f"  [{e['id']} {e['date']} {e['type']} c={e['conf']}] ({sec}) {e['text'][:90]}")
        return

    tokens = [t.lower() for arg in a.query for t in arg.split() if t.strip()]
    scored = []
    matched_ids = set()
    for sec, e in all_entries(data):
        hay = " ".join([e["text"], e["target"], e["tech"], e["type"], e["id"]]).lower()
        hits = sum(1 for t in tokens if t in hay)
        if not hits:
            continue
        base = (e["conf"] or 0.5) * recency(e["date"])
        tier = 1.0 if sec == "HOT" else 0.5
        scored.append((base * tier * (1 + 0.2 * (hits - 1)), sec, e))
        matched_ids.add(e["id"])
    scored.sort(key=lambda x: x[0], reverse=True)

    shown = set()
    for score, sec, e in scored[: a.top]:
        conf_s = f"{e['conf']:.2f}" if e["conf"] is not None else "--"
        print(f"{e['id']} [{e['type']} CONF={conf_s} {e['date']} {sec}] "
              f"tgt={e['target'] or '-'} tech={e['tech'] or '-'} :: {e['text']}")
        shown.add(e["id"])

    if a.deep:
        # one hop: entries this entry points to, or entries pointing at it
        wanted = set()
        for _, m in all_entries(data):
            if m["id"] in shown and m["ref"]:
                wanted.update(re.findall(r"[A-Z]{1,2}-\d+", m["ref"]))
            if m["ref"] and re.findall(r"[A-Z]{1,2}-\d+", m["ref"]) and \
               set(re.findall(r"[A-Z]{1,2}-\d+", m["ref"])) & shown:
                wanted.add(m["id"])
        linked = [(recency(e["date"]), sec, e) for sec, e in all_entries(data)
                  if e["id"] in wanted - shown]
        linked.sort(key=lambda x: x[0], reverse=True)
        for _, sec, e in linked[:3]:
            conf_s = f"{e['conf']:.2f}" if e["conf"] is not None else "--"
            print(f"  ↳ linked {e['id']} [{e['type']} CONF={conf_s} {sec}] {e['text'][:80]}")

    if not scored:
        print("[MISS] no memory matches — fresh territory.")


def cmd_state(a):
    data = load()
    if a.set_ is not None:
        data["STATE"] = [("raw", ln) for ln in a.set_.split("\\n") if ln.strip()]
    elif a.add is not None:
        data["STATE"].append(("raw", a.add))
    else:
        for kind, item in data["STATE"]:
            print(item)
        return
    save(data)
    print(f"[OK] STATE updated.")


def cmd_stats(_):
    data = load()
    counts, pats, preds = {}, [], {"c": 0, "r": 0, "open": 0}
    hot = cold = 0
    for sec, e in all_entries(data):
        counts[e["type"]] = counts.get(e["type"], 0) + 1
        hot += sec == "HOT"
        cold += sec == "COLD"
        if e["type"] == "PATTERN":
            pats.append(e["conf"] or 0.5)
        if e["type"] == "PRED":
            if "✓" in e["text"]:
                preds["c"] += 1
            elif "✗" in e["text"]:
                preds["r"] += 1
            else:
                preds["open"] += 1
    total = sum(counts.values())
    avg = sum(pats) / len(pats) if pats else 0
    print(f"entries: {total} (hot={hot}, cold={cold}) | by type: {counts}")
    print(f"patterns avg CONF: {avg:.2f} | predictions: confirmed={preds['c']} "
          f"rejected={preds['r']} open={preds['open']}")
    rate = preds["c"] / max(1, preds["c"] + preds["r"])
    print(f"prediction accuracy: {rate:.0%} | brain size: "
          f"{os.path.getsize(MEM_PATH)} bytes")


def cmd_distill(_):
    data = load()
    pats = [
        ((e["conf"] or 0.5) * recency(e["date"]), sec, e)
        for sec, e in all_entries(data)
        if e["type"] == "PATTERN"
    ]
    pats.sort(key=lambda x: x[0], reverse=True)
    bullets = ["(auto-generated top-wisdom — do not hand-edit)"]
    for score, sec, e in pats[:10]:
        bullets.append(f"- {e['id']} ({e['conf']:.2f}) tgt={e['target'] or '*'} :: {e['text'][:100]}")
    if len(pats) < 10:
        bullets.append("- (fewer than 10 patterns yet — wisdom still forming)")
    data["DISTILLED"] = [("raw", b) for b in bullets]
    save(data)
    print(f"[OK] DISTILLED regenerated from top-{min(10, len(pats))} patterns.")


def cmd_compact(a):
    data = load()
    moved, kept = 0, 0
    hot_items = []
    for kind, item in data["HOT"]:
        keep = True
        if kind == "entry":
            e = item
            if e["type"] == "PRED" and days_old(e["date"]) > PRED_STALE_DAYS \
               and "✓" not in e["text"] and "✗" not in e["text"]:
                keep = False
            elif days_old(e["date"]) > STALE_DAYS and (e["conf"] or 0.5) < STALE_MIN_CONF:
                keep = False
        if keep:
            hot_items.append((kind, item))
            kept += 1
        else:
            data["COLD"].append((kind, item))
            moved += 1
    data["HOT"] = hot_items
    if a.dry_run:
        print(f"[DRY] would sink {moved} stale → COLD, keep {kept} in HOT.")
        return
    save(data)
    print(f"[OK] compacted: {moved} sank to COLD, {kept} stay HOT.")


# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser(prog="memory.py", description="HUNTER BRAIN hippocampus")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="create/reset brain file")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("add", help="add lesson|pattern|profile")
    p.add_argument("kind", choices=["lesson", "pattern", "profile"])
    p.add_argument("text")
    p.add_argument("--target", default="")
    p.add_argument("--tech", default="")
    p.add_argument("--conf", type=float, default=None)
    p.add_argument("--ref", default="")
    p.add_argument("--date", default=None, help="override YYYY-MM-DD (testing)")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("fp", help="register false-positive trap")
    p.add_argument("target")
    p.add_argument("text")
    p.add_argument("--date", default=None)
    p.set_defaults(fn=cmd_fp)

    p = sub.add_parser("pred", help="log prediction/hypothesis")
    p.add_argument("text")
    p.add_argument("--target", default="")
    p.add_argument("--ref", default="", help="link pattern id e.g. P-0001")
    p.add_argument("--date", default=None)
    p.set_defaults(fn=cmd_pred)

    p = sub.add_parser("confirm", help="prediction TRUE (+0.10 to pattern)")
    p.add_argument("pred_id")
    p.set_defaults(fn=cmd_confirm)

    p = sub.add_parser("reject", help="prediction FALSE (-0.15 to pattern)")
    p.add_argument("pred_id")
    p.set_defaults(fn=cmd_reject)

    p = sub.add_parser("recall", help="search memory (ranked)")
    p.add_argument("query", nargs="*", default=[])
    p.add_argument("--deep", action="store_true", help="include REF-linked one hop")
    p.add_argument("--last", action="store_true", help="state + recent entries")
    p.add_argument("--top", type=int, default=5)
    p.set_defaults(fn=cmd_recall)

    p = sub.add_parser("state", help="hunt handoff state")
    p.add_argument("--set", dest="set_", default=None)
    p.add_argument("--add", dest="add", default=None)
    p.set_defaults(fn=cmd_state)

    sub.add_parser("stats", help="brain metrics").set_defaults(fn=cmd_stats)
    sub.add_parser("distill", help="regenerate DISTILLED block").set_defaults(fn=cmd_distill)

    p = sub.add_parser("compact", help="sink stale entries to COLD")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_compact)

    a = ap.parse_args()
    if a.cmd != "init":
        pass
    a.fn(a)


if __name__ == "__main__":
    main()
