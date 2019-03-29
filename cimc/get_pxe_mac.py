#! /usr/bin/python
import argparse
from imcsdk import *
from imcsdk.imchandle import ImcHandle

'''
the example script is to get the pxeboot-enabled Mac address from CIMC and pass it to Kicker install API
Assume the 1st vnic in slot-1 VIC card in C220 (or slot2 C240) are pxeboot-enabled only
Author: lok.bruce@gmail.com
'''

def get_mac(handle, slot):
    macaddr = ''
    vic = handle.query_classid("adaptorUnit")

    if len(vic)== 0:
        # this is for server node with no VIC card, or use other NIC eg broadcom NIC

        nics = handle.query_classid("networkAdapterEthIf")

        if len(nics) == 0:
            print "No NIC found"
            return false
        else:
            for nic in nics:
                if 'network-adapter-1/eth-1' in nic.dn:
                    macaddr = nic.mac

    else:
        # this typical for most CIMC node with Cisco VIC card
        vnics = handle.query_classid("adaptorHostEthIf")

        for vnic in vnics:
            if (slot in vnic.dn) and ('host-eth-eth0' in vnic.rn) and ('enabled' in vnic.pxe_boot):
                macaddr = vnic.mac

    return macaddr

def main(args):
    slot = ''
    handle = ImcHandle(args.host,args.username,args.password)

    try:
        handle.login()
    except Exception, err:
        print "Exception:", str(err)
        exit(1)

    rack = handle.query_dn("sys/rack-unit-1")

    if 'C240' in rack.model:
        slot = 'adaptor-2'
    elif 'C220' in rack.model:
        slot = 'adaptor-1'
    else:
        print 'unsupported model'
        handle.logout()
        exit(1)

    macaddr = get_mac(handle, slot)

    if macaddr:
        print macaddr
        handle.logout()
    else:
        handle.logout()
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


