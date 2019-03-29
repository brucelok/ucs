#! /usr/bin/python
'''
simply get the fault details from standalone C-series server
works on both CIMC 2.0(9f) and 3.0(3a)
Author: lok.bruce@gmail.com
'''
from imcsdk import *
from imcsdk.imchandle import ImcHandle
import argparse

def checkServerModel(handle):
    mgmt = handle.query_dn('sys/rack-unit-1/mgmt/if-1')
    return mgmt.hostname

def getFault(handle):
    fault_list = []
    fault = handle.query_classid("FaultInst")
    for f in fault:
        fault_list.append(f)
    return fault_list

def main(args):
    handle = ImcHandle(args.host,args.username,args.password)
    try:
        handle.login()
    except Exception, err:
        print "Exception:", str(err)
        exit(1)

    hostname = checkServerModel(handle)
    fault = getFault(handle)

    print "Hostname: %s" % hostname
    if len(fault) == 0:
        print "no fault found"
    else:
        for i in fault:
            print i

    handle.logout()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='check server faults')
    parser.add_argument('-i', '--host',dest="host", required=True,
                      help="[Mandatory] IMC IP Address")
    parser.add_argument('-u', '--username',dest="username", required=True,
                      help="[Mandatory] Account Username for IMC Login")
    parser.add_argument('-p', '--password',dest="password", required=True,
                      help="[Mandatory] Account Password for IMC Login")
    args = parser.parse_args()
    main(args)
