#! /usr/bin/python
'''
script to check, set on/off locator LED
the script tested to work on both CIMC 2.0(9f) and 3.0(3a)
eg: python set_locatorled.py -i ip -u admin -p xxxxxxx -a {check|on|off}
Author: lok.bruce@gmail.com
'''
from imcsdk import *
from imcsdk.imchandle import ImcHandle
import argparse

def setLocatorLed(handle, action):
    led = handle.query_dn('sys/rack-unit-1/locator-led')
    if action == 'check':
        print "LED = %s  " % led.oper_state,
    elif action == 'on':
        print "LED > ON"
        led.admin_state = 'on'
        handle.set_mo(led)
    elif action == 'off':
        print "LED > OFF"
        led.admin_state = 'off'
        handle.set_mo(led)

def main(args):
    handle = ImcHandle(args.host,args.username,args.password)
    action = args.action
    try:
        handle.login()
        print "login_ok %s  " % args.host,
    except Exception, err:
        print "Exception:", str(err)
        exit(1)
    setLocatorLed(handle, action)
    handle.logout()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='to check the server info, model, sn, cards')
    parser.add_argument('-i', '--host',dest="host", required=True,
                      help="[Mandatory] IMC IP Address")
    parser.add_argument('-u', '--username',dest="username", required=True,
                      help="[Mandatory] Account Username for IMC Login")
    parser.add_argument('-p', '--password',dest="password", required=True,
                      help="[Mandatory] Account Password for IMC Login")
    parser.add_argument('-a', choices=['on','off','check'],dest="action", required=True,
                      help="[Mandatory] users desired LED locator state")
    args = parser.parse_args()
    main(args)
