#! /usr/bin/python
import argparse
from imcsdk import *
from imcsdk.imchandle import ImcHandle
'''
The script will enable one-time-boot with "pxe", it will override the existing boot order once.
once machine reboot completed, the boot order will return normal.
Author: lok.bruce@gmail.com
'''
def main(args):

    handle = ImcHandle(args.host,args.username,args.password)

    try:
        handle.login()
        mo = handle.query_dn("sys/rack-unit-1/one-time-precision-boot")
        setattr(mo,'device','pxe')
        handle.set_mo(mo)
        handle.logout()

    except Exception as err:
        print "Exception:", str(err)
        exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='get pxeboot mac address')
    parser.add_argument('-i', '--host',dest="host", required=True,
                      help="[Mandatory] IMC IP Address")
    parser.add_argument('-u', '--username',dest="username", required=True,
                      help="[Mandatory] Account Username for IMC Login")
    parser.add_argument('-p', '--password',dest="password", required=True,
                      help="[Mandatory] Account Password for IMC Login")
    args = parser.parse_args()
    main(args)
