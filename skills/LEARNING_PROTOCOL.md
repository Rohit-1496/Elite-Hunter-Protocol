# LEARNING_PROTOCOL.md — HUNTER BRAIN v2 (THE PREFRONTAL CORTEX)

> Single source of truth for persistent learning. Memory lives on disk; the context
> window is only RAM. A session that does not write memory is a hunt that never
> happened. This file is auto-loaded every session — these rituals are instincts,
> not suggestions.

---

## THE BRAIN FILES

| File | Role | Path |
|------|------|------|
| MEMORY.md | Cortex — all long-term data | `~/.config/opencode/MEMORY.md` |
| memory.py | Hippocampus — write/recall tooling | `<workspace>/memory.py` (run: `python3 <workspace>/memory.py ...`) |
| LEARNING_PROTOCOL.md | This file — enforced rituals | `~/.config/opencode/` (auto-loaded) |

Brain sections: `DISTILLED` (auto top-wisdom) · `STATE` (hunt handoff) · `HOT` (live entries) · `COLD` (stale, ranked 50%).

Entry types: `LESSON` (process learning) · `PATTERN` (technique + confidence) ·
`FP` (trap — never chase again) · `PRED` (logged hypothesis) · `PROFILE` (target intel).

## THE RITUALS

**R1 — SESSION START.** Before anything else:
```
python3 <workspace>/memory.py recall --last
```
Load STATE and recent entries. If an open hunt exists, resume it — never restart from zero.

**R2 — PRE-HYPOTHESIS RECALL (mandatory).** When ANY new attack surface, technology,
or endpoint class appears, BEFORE forming the attack plan:
```
python3 <workspace>/memory.py recall "<tech keywords>" [--deep]
```
Proven patterns get tried first. Registered FP traps get avoided first. Skipping this
ritual is the definition of wasting credits on known answers.

**R3 — LIVE CAPTURE.** The instant a test fails, a trap springs, or an assumption dies:
```
python3 <workspace>/memory.py fp <target> "<what fooled you>"
```
FP capture is mandatory. An unlogged wasted test will be paid for twice.

**R4 — AUTOPSY.** Log WHY something failed at assumption level ("I assumed X without
verifying Y"), not just outcome level ("404"). Assumption-level entries transfer across targets.

**R5 — PREDICTION LOOP (the learning engine).**
1. Promising hypothesis → log it: `pred "<claim>" --ref P-XXXX`
2. After testing → resolve it: `confirm PR-XXXX` or `reject PR-XXXX`
   - confirm: linked pattern CONF **+0.10** (cap 0.95)
   - reject:  linked pattern CONF **−0.15** (floor 0.05) — asymmetric by design: anti-overconfidence.
3. Never end a session with tested-but-unresolved predictions.

**R6 — SESSION END RETROSPECTIVE.** Before closing:
```
add lesson "..."            # durable process learning
add profile <target> "..."  # tech stack, auth flows, quirks
state --set "TARGET: X | STATUS: n% done | NEXT: exact next step"
stats                       # review efficiency trend
distill                     # if many new patterns were added
```

**R7 — SUBAGENT INJECTION.** When dispatching subagents: include relevant recalled
entries in their briefings so workers inherit experience. Workers return raw
observations; the orchestrator distills them into memory via R3–R6. Never let a
subagent's work die unrecorded.

**R8 — HYGIENE.** Run `compact` when HOT exceeds ~200 entries. COLD is searchable
history, not garbage. Never hand-edit CONF values — confidence changes ONLY through
confirm/reject outcomes.

## LAWS

1. **Never fabricate memory.** Only record what actually happened this session.
2. **Signal-only writes.** Durable lessons only; transient session noise stays in STATE.
3. **Recall before reasoning.** If memory wasn't checked, the hypothesis isn't grounded.
4. **Memory serves decisions.** If a recalled entry wouldn't change your next action, don't log its kind of noise next time.
5. **Cross-target transfer is the point.** A pattern proven on target A is a first-class candidate on target B.
6. **The brain outlives models.** Any model reading these files inherits everything.

## COMMAND CHEAT SHEET

```
init [--force]                       create/reset brain
add lesson|pattern|profile TEXT [--target T] [--tech X] [--conf 0.N] [--ref ID]
fp TARGET TEXT                       register false-positive trap
pred TEXT [--target T] [--ref P-ID]  log hypothesis
confirm PR-XXXX | reject PR-XXXX     resolve prediction (updates pattern CONF)
recall KEYWORDS [--deep] [--top N]   ranked search (CONF × recency)
recall --last                        state handoff + latest entries
state --set/--add TEXT               hunt handoff lines
stats                                counts, avg CONF, prediction accuracy
distill                              regenerate DISTILLED block (top-10 patterns)
compact [--dry-run]                  sink stale/low-CONF entries to COLD
```

*Hunter Brain v2 — the model is disposable; the brain is not.*
