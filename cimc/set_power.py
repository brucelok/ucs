#! /usr/bin/python
'''
the script work on both CIMC 2.0(9f) and 3.0(3a)
description: power on, up or reboot of a CIMC server
Args:
-s, option: on, off, reset, check

Author: lok.bruce@gmail.com

'''
import argparse
from imcsdk.imchandle import ImcHandle
from imcsdk.apis.server.serveractions import *

def set_power_state(handle, state, oper_power):
    if state == oper_power:
        print "the server already %s, no action" % oper_power
        return False
    if state == 'reset':
        print "rebooting the server"
        if oper_power == 'on':
            server_power_cycle(handle)
        elif oper_power == 'off':
            server_power_up(handle)
    elif state == 'on':
        print "powering up the server"
        server_power_up(handle)
    elif state == 'off':
        print "powering down the server"
        server_power_down(handle)
    elif state == 'check':
        print "current power status: %s" % oper_power
    return True

def main(args):
    state = args.state
    handle = ImcHandle(args.host,args.username,args.password)
    try:
        handle.login()
    except Exception, err:
        print "Exception:", str(err)
        exit(1)

    oper_power = server_power_state_get(handle)
    pwr = set_power_state(handle, state, oper_power)
    handle.logout()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='check & set CIMC power status')
    parser.add_argument('-i', '--host',dest="host", required=True,
                      help="[Mandatory] IMC IP Address")
    parser.add_argument('-u', '--username',dest="username", required=True,
                      help="[Mandatory] Account Username for IMC Login")
    parser.add_argument('-p', '--password',dest="password", required=True,
                      help="[Mandatory] Account Password for IMC Login")
    parser.add_argument('-s', choices=['check','on','off','reset'],dest="state", required=True,
                      help="[Mandatory] users desired power state")
    args = parser.parse_args()
    main(args)
