# REPORTING PROTOCOL v1

Write a CONFIRMED finding into ONE clean file. Works for HackerOne, Bugcrowd, Intigriti, YesWeHack.

## RULES
- Only for CONFIRMED findings (passed the Proof Gate: G0–G5 + score ≥ 85). Never write up SUSPECTED.
- One finding = one file, named `<finding_id>_report.md`.
- File layout: the report on top, then the CONFIRMATION MANIFEST block at the very END (save_report.sh reads it).
- In prose, never START a line with a manifest word (`label:`, `target:`, `gate_...:`, `confirmation_score:`, `evidence:`). Write "Severity:" / "Affected asset:" instead.
- Every reproduce step must be copy-pasteable (raw request or curl). Use test accounts: A = attacker, B = victim (both yours).
- Severity = CVSS 3.1 score + full vector. Be honest — no inflation.
- Impact = what the attacker really gets on THIS target. No "could potentially".

## PLATFORM FIELD (fill the one your program uses; always give CVSS 3.1 score + vector)
- HackerOne → Weakness = CWE
- Bugcrowd → VRT category
- Intigriti → Type + endpoint URL
- YesWeHack → CWE + CVSS vector

## TEMPLATE (copy, fill every `<...>`, delete the hints)
```markdown
# <Vuln class> in <feature/param> on <host>

## Summary
<2–3 sentences: what the bug is, where, and the impact.>

## Affected asset
- Target: <in-scope host>
- Endpoint(s): <URL / API route>
- Parameter: <param / header / field>

## Vulnerability details
- Class: <IDOR / XSS / SSRF / SQLi / ...>
- CWE: <CWE-id + name>
- VRT: <category>            (Bugcrowd only)
- Severity: <Critical/High/Medium/Low> — CVSS 3.1 <score> (`<vector>`)

## Steps to reproduce
1. <exact step — raw request or curl>
2. <next step>
3. <result that proves the bug>

## Proof of concept
<the decisive request/response, payload, or OOB callback log a triager can re-run.>

## Impact
<what the attacker concretely achieves on this target, in business terms.>

## Remediation
<specific fix for this bug.>

## References
- <CWE / OWASP link>

=== CONFIRMATION MANIFEST v1 ===
finding_id: <slug>
vuln_class: <SQLi|XSS|SSRF|IDOR|SSTI|RCE|XXE|AUTH|LOGIC|UPLOAD|OTHER>
target: <in-scope host/endpoint>
gate_G0_in_scope: PASS
label: CONFIRMED
gate_G1_reproduce_3x_clean: PASS
gate_G2_negative_control: PASS
gate_G3_benign_ruled_out: PASS
gate_G4_determinism: PASS
gate_G5_real_impact: PASS
confirmation_score: 90
evidence:
  - <path/link>
  - <path/link>
attacker_accounts_only: true
notes: <benign causes excluded>
=== END MANIFEST ===
```

## EXAMPLE (IDOR)
```markdown
# IDOR in invoice API on api.example.com exposes any tenant's invoices

## Summary
GET /v2/invoices/{id} returns records without an object-level auth check. Any user can read
other tenants' invoices (PII + amounts) by changing the id.

## Affected asset
- Target: api.example.com
- Endpoint(s): GET /v2/invoices/{id}
- Parameter: path id

## Vulnerability details
- Class: IDOR (Broken Object-Level Authorization)
- CWE: CWE-639
- VRT: Broken Access Control > IDOR > Read
- Severity: High — CVSS 3.1 7.5 (`CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`)

## Steps to reproduce
1. Log in as Account A (attacker); get its bearer token.
2. Request an id owned by Account B:
   curl -s https://api.example.com/v2/invoices/10433 -H "Authorization: Bearer <A_TOKEN>"
3. Response returns Account B's full invoice — a different tenant. Repeat across ids.

## Proof of concept
Response to A's token for B's invoice 10433:
{ "id":10433, "account_id":"B", "customer":"Jane Roe", "amount":"$4,210.00" }
Logs: evidence/idor_reqresp.log, evidence/idor_crossuser.log

## Impact
Any authenticated tenant can read every other tenant's invoices — cross-tenant PII and
billing exposure across the platform.

## Remediation
Check the invoice's account_id matches the caller before returning it. Prefer UUID ids.

## References
- https://cwe.mitre.org/data/definitions/639.html

=== CONFIRMATION MANIFEST v1 ===
finding_id: idor-invoice-api
vuln_class: IDOR
target: https://api.example.com/v2/invoices/
gate_G0_in_scope: PASS
label: CONFIRMED
gate_G1_reproduce_3x_clean: PASS
gate_G2_negative_control: PASS
gate_G3_benign_ruled_out: PASS
gate_G4_determinism: NA
gate_G5_real_impact: PASS
confirmation_score: 85
evidence:
  - evidence/idor_reqresp.log
  - evidence/idor_crossuser.log
attacker_accounts_only: true
notes: excluded caching/CDN; reproduced from clean sessions
=== END MANIFEST ===
```

## BEFORE SAVE
- No `<...>` left. CVSS vector matches the score.
- Manifest is the LAST block: label CONFIRMED, all gates PASS (G4 may be NA), gate_G0_in_scope PASS, score ≥ 85, ≥ 2 evidence.
- Run `save_report.sh <file>`. If it prints `[REJECT]`, the finding is not ready.
