#! /usr/bin/python
import argparse
from imcsdk import *
from imcsdk.imchandle import ImcHandle

'''
the example script is to get the pxeboot-enabled Mac address from Cisco VIC card in Cisco IMC
and pass it to cobbler for pxebooting
auther: lok.bruce@gmail.com
'''

def get_mac(handle, slot):
    macaddr = ''
    vic = handle.query_classid("adaptorUnit")

    if len(vic)== 0:
        # this is for a server with no VIC card insalled
        print "No VIC card, checking other NIC"

        # check if other NIC existed
        nics = handle.query_classid("networkAdapterEthIf")

        if len(nics) == 0:
            print "No more NIC found"
            return false
        else:
            for nic in nics:
                if 'network-adapter-1/eth-1' in nic.dn:
                    macaddr = nic.mac

    else:
        # this typical for most nodes with VIC card installed
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

    # usually VIC card is installed on slot-2 in C240
    # whereas it will be slot-1 in C220
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


