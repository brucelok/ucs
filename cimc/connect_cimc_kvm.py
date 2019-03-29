#! /usr/bin/python
'''
Description:
    The script allows your terminal to directly connect to the Imc KVM-Console without launching the CIMC Webgui/Java

Example:
    $ python connect_host.py -i ipaddress/hostname -u user -p password

Author: lok.bruce@gmail.com
'''
import argparse, sys
import socket
import pexpect

def main():

    parser = argparse.ArgumentParser(description='connect Imc KVM console over terminal')
    parser.add_argument('-i', '--host', dest="host", required=True,
                      help="CIMC IP address or hostname")
    parser.add_argument('-u', '--username', dest="username", required=True)
    parser.add_argument('-p', '--password', dest="password", required=True)
    args = parser.parse_args()

    hostname = args.host
    user = args.username
    pw = args.password

    # check if hostname resolvable
    try:
        answers = socket.gethostbyname(hostname)
    except socket.gaierror, err:
        print "cannot resolve hostname: ", hostname, err
        exit(1)

    # try connecting to target CIMC
    try:
        print "connecting to", hostname
        child = pexpect.spawn('ssh %s@%s' % (user, hostname))
        #child.logfile = sys.stdout
        child.timeout = 20
        child.expect('password:')
    except pexpect.TIMEOUT as e:
        print "CIMC unreachable"
        exit(1)

    #try login CIMC
    try:
        child.sendline(pw)
        child.expect('#')
    except pexpect.TIMEOUT:
        print "Login failed"
        exit(1)

    child.sendline('scope kvm')
    child.expect('kvm #')
    child.sendline('connect host')

    # two outputs expected
    i = child.expect(['session', 'CISCO Serial Over LAN disabled*'])

    if i == 0:
        print child.before
        child.interact()

    elif i == 1:
        print "CISCO Serial Over LAN is NOT enabled, exiting CIMC"
        child.sendline('top')
        child.expect('#')
        child.sendline('exit')

if __name__ == '__main__':
    main()
