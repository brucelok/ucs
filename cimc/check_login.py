#! /usr/bin/python
# the script tested to works on both CIMC 2.0(9f) and 3.0(3a)

from imcsdk import *
from imcsdk.imchandle import ImcHandle
import argparse

def main(args):
    handle = ImcHandle(args.host,args.username,args.password)
    if handle.login():
        print "login_ok %s" %(args.host)
    handle.logout()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='to check the server info, model, sn, cards')
    parser.add_argument('-i', '--host',dest="host", required=True,
                      help="[Mandatory] IMC IP Address")
    parser.add_argument('-u', '--username',dest="username", required=True,
                      help="[Mandatory] Account Username for IMC Login")
    parser.add_argument('-p', '--password',dest="password", required=True,
                      help="[Mandatory] Account Password for IMC Login")
    args = parser.parse_args()
    main(args)
