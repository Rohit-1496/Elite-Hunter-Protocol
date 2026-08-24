# RECON PROTOCOL v1

Single source of truth for reconnaissance. Goal: full coverage, low credits, no bans.
Run phases 0→5 in order. Do CHEAP + PASSIVE first; run expensive/active steps ONLY on
live, in-scope hosts. One tool per job — add a 2nd only if the first comes back thin.

## GOLDEN RULES
- Scope first, always. Never scan an asset until Phase 0 confirms it is in-scope.
- One tool per job. Escalate to a 2nd tool ONLY if results look thin/incomplete.
- Gate by cost: passive → live-check → active. Never run active scans on dead/out-of-scope hosts.
- Dedup everything into ONE inventory. Never test the same thing twice.
- Log what you cleared (cleared.txt) and what was dead (dead.txt) so you never redo it.
- Be polite: cap the request rate. A ban wastes the whole session.
- If a listed tool is missing, install it, then continue — don't silently skip a recon step.
- Every action must answer: what hypothesis does this confirm or deny? If none — skip it.

## WORKING FILES (keep these updated)
- in_scope.txt / excluded.txt   — from Phase 0
- hosts.txt                     — all discovered → split into live.txt / dead.txt (Phase 2)
- inventory.md                  — host → tech → endpoints → params → auth → OOB candidates
- cleared.txt                   — asset+hypothesis already ruled out (don't retest)
- chain_candidates.txt          — low/med findings that might chain (never dropped)

## PHASE 0 — SCOPE LOCK  (no tools)
1. Read the program scope page + every linked doc + the authorization letter.
2. Read past disclosed reports (known bugs, boundaries, excluded classes).
3. Write in_scope.txt (assets/wildcards) and excluded.txt (assets + excluded vuln classes).
   Everything downstream is filtered against these. Ties to Proof Gate G0.

## PHASE 1 — PASSIVE DISCOVERY  (cheap, no direct load on the target)
4. Subdomains: subfinder + crt.sh (CT logs).
   Escalate: amass (passive) ONLY if the list is thin or scope is a big wildcard.
5. Org expansion: org→ASN lookup + note known acquisitions (catches acquired infra).
6. Merge + dedup all names → hosts.txt.

## PHASE 2 — LIVE VERIFY  (one probe, splits the work)
7. httpx once over hosts.txt: -title -tech-detect -status-code -server -location -csp-probe
   → live.txt (responding) and dead.txt (parked, NOT deleted — avoids missing them later).
8. From here on, active steps run ONLY on hosts in both live.txt AND in_scope.txt.

## PHASE 3 — SURFACE MAPPING  (targeted, per live host)
9.  Tech fingerprint (from httpx) — it decides the wordlists + nuclei tags below.
10. JS harvest: getJS/subjs → linkfinder (endpoints) + jsluice (secrets). High ROI, low noise.
11. Content discovery: ffuf with a tech-matched wordlist, polite rate.
    Escalate: feroxbuster (recursive) ONLY on interesting dirs found.
12. Params: arjun ONLY on endpoints that look dynamic (not every URL).
13. Ports: ONLY if scope includes IPs / non-web. naabu top-ports, then nmap -sV on hits.
    Priority non-standard ports: 6379 9200 9300 27017 5432 3306 5984 11211 2375 2376
    6443 8500 8200 2379 2380 9090 3000 5601 15672 7001 7002 4848 9042 7474 4369
    (masscan only for large IP ranges.)

## PHASE 4 — COMPLETENESS CHECK  (this is how nothing gets missed)
14. Normalize all results into inventory.md (host → tech → endpoints → params → auth → OOB).
15. Tick the COVERAGE CHECKLIST (mark each done or N/A):
    [ ] shadow / undocumented APIs        [ ] multiple API versions (v1, v2, internal)
    [ ] acquired-company infrastructure   [ ] mobile-app / thick-client endpoints
    [ ] staging / dev / uat hosts         [ ] admin / privileged panels
    [ ] auth & session flows              [ ] file-upload endpoints
    [ ] historical assets from CT logs    [ ] websockets / GraphQL
16. nuclei on live hosts: -severity critical,high, tech-tagged, polite rate.
    Keep interactsh configured + running for every SSRF / blind / OOB candidate.

## PHASE 5 — PRIORITISE → HANDOFF
17. Rank targets by ROI: auth/account → object refs (IDOR) → server-side fetch (SSRF)
    → injection sinks → file upload → admin/privileged → payment/business logic.
18. For each candidate: state the hypothesis + the SINGLE cheapest test to confirm it.
19. After a finding, choose the NEXT test in this order:
    a. Chainable to Critical? → test the chain link next.
    b. Else → next highest-ROI candidate on the SAME host (reuse context = save credits).
    c. Escalate object/identity: IDOR → cross-tenant + mass-enum; auth → privilege-escalation.
    d. File CONFIRMED findings immediately. Park chainable low/med in chain_candidates.txt.
20. Confirm every finding via CONFIRMATION_PROTOCOL (Proof Gate). Only CONFIRMED →
    write it up with REPORTING_PROTOCOL.

## CREDIT DISCIPLINE  (all phases)
- Every 5 actions: STOP, report status, reprioritise.
- Dead-path cutoff: 3 empty tests on a hypothesis → write it to cleared.txt → move on.
  EXCEPTION: if it could chain, park it in chain_candidates.txt instead of dropping it.
- Run independent tasks in parallel — but ONE tool per job, no duplicate tools "just in case".

## MINI EXAMPLE
Scope: *.acme.com (in-scope), acme-labs.com (excluded).
P1: subfinder + crt.sh → 42 names → hosts.txt.   P2: httpx → 11 live.
P3: api.acme.com tech=nginx/Node; JS harvest → /v2/users/{id}, /internal/export; arjun → ?debug.
P4: checklist catches a SECOND API version /v1/ still live → added. nuclei high/critical, polite.
P5: /v2/users/{id} = IDOR hypothesis → cheapest test: swap id with a 2nd test account.
    Confirmed cross-tenant read → file via Proof Gate. Next: mass-enum (chain to bulk PII).
