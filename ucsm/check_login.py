#! /usr/bin/python
'''
Used to test if one can login the UCSM and perform basic query
'''
import argparse
from ucsmsdk.ucshandle import UcsHandle

def checkbasic(handle):
    top = handle.query_classid("TopSystem")
    for t in top:
        print "pod_name:%s  mode:%s  vip:%s" %(t.name, t.mode, t.address)

def getFI(handle):
    fi = handle.query_classid("NetworkElement")
    for f in fi:
        print "model:%s  serial:%s  ip:%s  status:%s" % (f.model, f.serial, f.oob_if_ip, f.operability)

def main(args):
    handle = UcsHandle(args.host, args.username, args.password)

    try:
        handle.login()
    except Exception, err:
        print "Exception:", str(err)
        exit(1)

    checkbasic(handle)
    getFI(handle)
    handle.logout()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='to check UCS manager login')
    parser.add_argument('-i', '--host', dest="host", required=True)
    parser.add_argument('-u', '--username', dest="username", required=True)
    parser.add_argument('-p', '--password', dest="password", required=True)
    args = parser.parse_args()
    main(args)
