# CONFIRMATION_PROTOCOL.md — THE PROOF GATE

> Single source of truth for the word "confirmed". This file OVERRIDES every other
> "confirmation" / "triple-check" / "zero false positive" wording anywhere in the
> brain or skill files. If any other file disagrees, THIS file wins.

---

## RULE 0 — AUTHORITY

A finding may be called **CONFIRMED** (and therefore reported / saved) **only** if it
passes this protocol in full. Never report or save a finding that is not CONFIRMED.
No exceptions, no "looks obvious", no "probably vulnerable".

## THE ONLY THREE LABELS

Every finding gets exactly one label:

- **CONFIRMED** — passed all 5 Hard Gates AND Confirmation Score ≥ 85/100. Only this is reported / saved.
- **SUSPECTED** — promising but not fully proven. Keep testing or drop it. **NEVER report a SUSPECTED.**
- **REJECTED (FP)** — failed a gate, or explained by a benign cause. Log it in one line and move on.

Default assumption for every signal is **SUSPECTED** until this gate is cleared.
A signal is guilty of being a false positive until proven innocent.

---

## PART A — THE HARD GATES  (G0 scope pre-check + G1-G5 — all mandatory; miss one = NOT confirmed)

G0 — SCOPE (pre-check): The exact target asset is in the program's scope AND the
vulnerability class is not excluded by the program. If this class was previously ruled
out-of-scope/informational here, raise the impact bar or drop it. Out-of-scope asset or
excluded class => REJECT (invalid report, never saved). G0 cannot be NA.

**G1 — REPRODUCE (clean sessions).**
Reproduce the exact result **≥ 3 times**, each from an independent clean session
(fresh cookies / incognito / new token / new client). Flaky or intermittent = **REJECT**.

**G2 — NEGATIVE CONTROL (differential test).**
Run the **exact same request with the payload removed / neutralised** (a benign baseline).
The signal MUST disappear in the baseline. If the baseline shows the same behaviour →
it is normal application behaviour → **REJECT**. This single step kills most false positives.

**G3 — RULE OUT BENIGN CAUSES (explicitly).**
Before confirming, explicitly rule out each of: caching / CDN, WAF or block page,
rate-limiting, generic error page, redirect, network jitter/latency, and **intended
functionality**. Write down which ones you checked. If any explains the signal → **REJECT**.

**G4 — DETERMINISM (blind / inferential bugs only: time-based, boolean, OOB).**
Run **≥ 5 trials of the "true" condition and ≥ 5 of the "false" condition**. The two
groups must be **clearly and consistently separable** (no overlap). One lucky hit,
or overlapping timings, = **REJECT**. (For direct-impact bugs where you can see the
result directly, mark G4 = **NA**.)

**G5 — REAL IMPACT (attacker-owned accounts only).**
Demonstrate **actual object-level impact**, never theoretical: real cross-account data
returned, a real out-of-band callback received, or a real state change observed —
using **only test accounts you control**. "An attacker could…" without a demonstration
= NOT confirmed. Never touch real users' data; never write files / plant backdoors /
cause financial loss to prove a point — use time-delay or OOB callbacks instead.

---

## PART B — CONFIRMATION SCORE (0-100, need >= 85)

Base — earned only when ALL hard gates pass:
  +15  G1 reproduced 3x from clean sessions
  +15  G2 negative control passed (baseline logged)
  +10  G3 benign causes ruled out
  +25  G5 real object-level impact demonstrated
  = 65 base

Evidence strength — add until you reach >= 85:
  +20  Out-of-band proof (interactsh/collaborator DNS or HTTP callback from the server)
  +15  Determinism (G4) met, with the actual numbers logged
  +10  Second independent method reproduces (e.g. manual curl AND Burp)
  +10  Second identity/account reproduces (true cross-user impact)

Max 100 (cap).
- Blind classes (blind SQLi / SSRF / XXE / RCE / blind XSS): the OOB callback is the
  primary path to >= 85.
- Direct-impact classes (IDOR returning real foreign data, stored/visible XSS, visible RCE
  output): OOB is NOT required — reach >= 85 via base + second-method + cross-user/second-
  identity evidence. G4 may be NA for these.
- A finding that passes every gate but scores 65-84 stays SUSPECTED: get one more
  independent corroboration before it becomes CONFIRMED.

## PART C — PER-CLASS PROOF & FALSE-POSITIVE TRAPS

What actually counts as proof, and the trap that fools lazy hunters into a false positive.

- **SQLi** — PROOF: deterministic time separation (G4) OR data extraction OR OOB DNS. TRAP: network jitter (do the ≥5/≥5), generic 500s, WAF-induced latency.
- **XSS** — PROOF: script *executes* in a real browser context (DOM shows it / callback fires). TRAP: reflected-but-encoded, reflected into a non-executing context (raw JSON, 404 text), self-XSS only.
- **SSRF** — PROOF: OOB callback originating from the *server's* IP, OR internal-only content returned. TRAP: the app fetching a URL by design (webhook/link-preview), client-side fetch, a DNS hit from your own resolver.
- **IDOR / BOLA** — PROOF: account B reads/changes account A's object, and the data provably belongs to victim test account. TRAP: the data is public anyway, the object is actually yours, or a 200 with empty/no real data.
- **SSTI** — PROOF: math evaluates (`7*7`→`49`) AND engine-specific escalation callback. TRAP: value reflected literally, or math in a non-template sink.
- **RCE / CMDi** — PROOF: OOB callback or deterministic time delay (G4), non-destructive. TRAP: WAF sinkhole, the command string merely reflected, unrelated timeouts.
- **XXE** — PROOF: file content returned OR OOB DTD callback. TRAP: a parser error is NOT XXE; entity never resolved.
- **Auth / JWT** — PROOF: a forged/altered token is accepted AND grants access it should not. TRAP: token accepted but no privilege gained; a 200 that is not actually an authenticated state.
- **Business logic / Race** — PROOF: video + multiple success responses beyond the allowed limit; state actually changed. TRAP: a single success, idempotent retries, or an eventual server-side rejection/rollback.
- **File upload** — PROOF: the uploaded file executes / an OOB callback fires. TRAP: stored but never served/executed, sanitised on read, or only the content-type was spoofed.

---

## PART D — THE CONFIRMATION MANIFEST (mandatory, machine-checked)

Emit this block **verbatim** alongside every report. `save_report.sh` parses it and
**refuses to save the report** unless every gate reads PASS (G4 may be NA), the score
is ≥ 85, the label is CONFIRMED, and there are ≥ 2 evidence items.

```
=== CONFIRMATION MANIFEST v1 ===
finding_id: <short-slug>
vuln_class: <SQLi|XSS|SSRF|IDOR|SSTI|RCE|XXE|AUTH|LOGIC|UPLOAD|OTHER>
target: <in-scope host/endpoint>
gate_G0_in_scope: PASS
label: CONFIRMED
gate_G1_reproduce_3x_clean: PASS
gate_G2_negative_control: PASS
gate_G3_benign_ruled_out: PASS
gate_G4_determinism: PASS        # use NA only for direct-impact classes
gate_G5_real_impact: PASS
confirmation_score: 90           # must be >= 85
evidence:
  - <path/link to request-response log>
  - <path/link to OOB callback log OR screen recording>
  - <path/link to negative-control baseline log>
attacker_accounts_only: true
notes: <one line — which benign causes you excluded>
=== END MANIFEST ===
```

**Manifest rules:** every `gate_*` must be `PASS` (G4 may be `NA`); gate_G0_in_scope must be PASS (never NA); `confirmation_score`
must be an integer ≥ 85; `label` must be `CONFIRMED`; at least 2 `evidence` items.
If you cannot fill this honestly, the finding is **SUSPECTED** — do not report it.

---

## ONE-LINE MINDSET

> A scanner reports 100 maybes. A predator reports 3 certainties. We only speak when we can prove it.
