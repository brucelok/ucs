#! /usr/bin/python
'''
demo - retireve UCSM inventory by using get_inventory() module
       output data into html format
author: lok.bruce@gmail.com
'''
import argparse
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.utils.inventory import *


def main(args):
    handle = UcsHandle(args.host, args.username, args.password)

    try:
        handle.login()
    except Exception, err:
        print "Exception:", str(err)
        exit(1)

    get_inventory(handle,
                  component="all",
                  file_format="html",
                  file_name="output.html",
                  spec=inventory_spec)

    handle.logout()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='to check UCS manager login')
    parser.add_argument('-i', '--host', dest="host", required=True)
    parser.add_argument('-u', '--username', dest="username", required=True)
    parser.add_argument('-p', '--password', dest="password", required=True)

    args = parser.parse_args()
    main(args)
