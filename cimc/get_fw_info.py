#! /usr/bin/python
'''
check the firmware version of major components eg: CIMC,BIOS,VIC,LSI
works on both CIMC 2.0(9f) and 3.0(3a)
Author: lok.bruce@gmail.com
'''
from imcsdk import *
from imcsdk.imchandle import ImcHandle
import argparse

def checkServerModel(handle):
    mgmt = handle.query_dn('sys/rack-unit-1/mgmt/if-1')
    return mgmt.hostname

def checkCimcFw(handle):
    cimc = handle.query_dn('sys/rack-unit-1/mgmt/fw-system')
    return cimc.version

def checkBios(handle):
    bios = handle.query_dn('sys/rack-unit-1/bios/fw-boot-loader')
    return bios.version

def pciEquipment(handle):
    pci_list = []
    pci = handle.query_classid("pciEquipSlot")
    for slot in pci:
        slot = slot.model, slot.version
        pci_list.append(slot)
    return pci_list

def main(args):
    handle = ImcHandle(args.host,args.username,args.password)
    try:
        handle.login()
    except Exception, err:
        print "Exception:", str(err)
        exit(1)

    hostname = checkServerModel(handle)
    cimc = checkCimcFw(handle)
    bios = checkBios(handle)
    pci = pciEquipment(handle)

    print hostname,
    print cimc,
    print bios,
    for i in pci:
        print i[1],

    handle.logout()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='check the firmware version')
    parser.add_argument('-i', '--host',dest="host", required=True,
                      help="[Mandatory] IMC IP Address")
    parser.add_argument('-u', '--username',dest="username", required=True,
                      help="[Mandatory] Account Username for IMC Login")
    parser.add_argument('-p', '--password',dest="password", required=True,
                      help="[Mandatory] Account Password for IMC Login")
    args = parser.parse_args()
    main(args)
