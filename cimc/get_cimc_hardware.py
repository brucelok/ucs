#! /usr/bin/python
'''
the script works on both CIMC 2.0(9f) and 3.0(3a)
it will get the details of common & enabled hardware components, & health brief

[ CIMC hostname, Firmware, CPU, MEM, Server Model, Serial number, NIC card, storage controller and physical disks or onbroad SATA disks]

syntax: python get_cimc_hardware.py -H <cimc_hostname/ip> -u admin -p <password> [optional: -a full]

[-a full]: will output the full list of each hardware component

Author: lok.bruce@gmail.com
'''
from imcsdk import *
from imcsdk.imchandle import ImcHandle
import argparse

def checkServerModel(handle):
    mgmtIf = handle.query_dn('sys/rack-unit-1/mgmt/if-1')
    print "Hostname:%s  IP:%s  " % (mgmtIf.hostname, mgmtIf.ext_ip),
    rack = handle.query_dn("sys/rack-unit-1")
    print "Power:%s  Model:%s  SN:%s  CPU:%s  MEM:%s " %(rack.oper_power, rack.model, rack.serial, rack.num_of_cpus, rack.total_memory),

def checkCimcFw(handle):
    fws = handle.query_classid("firmwareRunning")
    for fw in fws:
        if fw.dn == 'sys/rack-unit-1/mgmt/fw-system':
            print "FW:%s " %(fw.version),

''' it will count and get disks details,
if there is no hardware raid controller installed, it will try to get onboard SATA disks (HDD) but it can ONLY be detected if 'Pch-Sata-Mode' in BIOS is enabled with AHCI
else it will get the phyiscal disks(PD) under raid controller '''

def checkPhysicalDrive(handle):
    storageControllers = handle.query_classid("storageController")
    print "HBA:%s "%(len(storageControllers)),
    if (len(storageControllers)) == 0:
        storageLocalDiskSlotEps = handle.query_classid("storageLocalDiskSlotEp")
        count = 0
        for storageLocalDiskSlotEp in storageLocalDiskSlotEps:
            if 'equipped' in storageLocalDiskSlotEp.presence:
                count +=1
        print "HDD:%s " %(count),
    else:
        storageLocalDisks = handle.query_classid("storageLocalDisk")
        print "PD:%s "%(len(storageLocalDisks)),

def checkPhysicalDrive_full(handle):
    print "----- List of Storage Controller Card and Phyiscal Disks -----"
    storageControllers = handle.query_classid("storageController")
    if (len(storageControllers)) == 0:
        hdds = handle.query_classid("biosBootDevPrecision")
        print "No storage Controller -> PCH SATA Local Disks"
        for hdd in hdds:
            if 'PCHSTORAGE' in hdd.type:
                print "%s " %(hdd.descr)
    else:
        storageLocalDisks = handle.query_classid("storageLocalDisk")
        for storageController in storageControllers:
            print "Slot: %s  Model: %s "%(storageController.id, storageController.model)
        for storageLocalDisk in storageLocalDisks:
            print "PD-%s, %s:%s, %s, %s, %s, %s, %s" %(storageLocalDisk.id, storageLocalDisk.interface_type, storageLocalDisk.media_type, storageLocalDisk.coerced_size, storageLocalDisk.vendor, storageLocalDisk.product_id, storageLocalDisk.drive_serial_number, storageLocalDisk.health)

''' count number of NIC, it can be Cisco VIC, Broadcom, or onboard Intel 1G NIC
Broadcom NIC card is usually for Ceph MON & OSD nodes)
if you see onboard Intel 1G NIC, you should disable it because we don't use.'''

def checkNic(handle):
    adaptorUnits = handle.query_classid("adaptorUnit")
    print "VIC:%s "%(len(adaptorUnits)),

    count_brc = 0
    count_nic = 0
    networkAdaptors = handle.query_classid("networkAdapterUnit")
    for networkAdaptor in networkAdaptors:
        if 'Broadcom' in networkAdaptor.model:
            count_brc +=1
        else:
            count_nic +=1
    print "BRC:%s  NIC:%s "%(count_brc, count_nic),

''' get the detail of enabled NIC card, it can be Cisco VIC, Broadcom or onboard Intel 1G NIC '''
def checkNic_full(handle):
    print "----- List of enabled Network Interface Cards -----"
    adaptorUnits = handle.query_classid("adaptorUnit")
    if (len(adaptorUnits)) == 0:
        print "No Cisco VIC card detected"
    else:
        for adaptorUnit in adaptorUnits:
            print "Slot: %s  Model: %s  Serial: %s"%(adaptorUnit.id, adaptorUnit.model, adaptorUnit.serial)

    networkAdaptors = handle.query_classid("networkAdapterUnit")
    if (len(networkAdaptors)==0):
        print "No other NIC card detected"
    else:
        for networkAdaptor in networkAdaptors:
            print "Slot: %s  Model: %s" %(networkAdaptor.slot, networkAdaptor.model)

''' list out all PCI equipment '''
def pciEquipment(handle):
    print "----- List of enabled PCI Equipment -----"
    pciUnits = handle.query_classid("pciEquipSlot")
    for pciUnit in pciUnits:
        print "Slot: %s  Model: %s  Version: %s  " % (pciUnit.id, pciUnit.model, pciUnit.version)

''' list out all Power Supply Unit '''
def psuEquipment(handle):
    print "----- List of Power Supply Unit -----"
    psuUnits = handle.query_classid("equipmentPsu")
    for psuUnit in psuUnits:
        print "Slot: %s  Model: %s  Serial: %s  Presence: %s  " % (psuUnit.id, psuUnit.model, psuUnit.serial, psuUnit.presence)

def cpuEquipment(handle):
    print "----- List of CPU -----"
    cpuUnits = handle.query_classid("processorUnit")
    for cpuUnit in cpuUnits:
        print "Socket: %s  Model: %s  Presence: %s" % (cpuUnit.socket_designation, cpuUnit.model, cpuUnit.presence)

def memoryEquipment(handle):
    print "----- List of Memory -----"
    memUnits = handle.query_classid("memoryUnit")
    for memUnit in memUnits:
        print "Location: %s  Capacity: %s  Model: %s  Serial: %s  Presence: %s" % (memUnit.location, memUnit.capacity, memUnit.model, memUnit.serial, memUnit.presence)

def ledHealth(handle):
    count_fault = 0
    ledUnits = handle.query_classid("equipmentIndicatorLed")
    for ledUnit in ledUnits:
        if ('amber' in ledUnit.color) or ('red' in ledUnit.color):
            count_fault +=1
    if count_fault > 0:
        print "fault:yes"
    else:
        print "fault:no"

def ledHealth_full(handle):
    print "---- Summary of health status -----"
    ledUnits = handle.query_classid("equipmentIndicatorLed")
    for ledUnit in ledUnits:
        print "Name: %s  Color: %s " % (ledUnit.name, ledUnit.color)

def get_mac(handle):
    vnics = handle.query_classid("adaptorHostEthIf")
    for vnic in vnics:
        if 'host-eth-eth0' in vnic.dn:
            print "%s: %s" % (vnic.name, vnic.mac)


def main(args):
    action= args.action
    handle = ImcHandle(args.host,args.username,args.password)
    try:
        handle.login()
    except Exception, err:
        print "Exception:", str(err)
        exit(1)

    checkServerModel(handle)
    checkCimcFw(handle)
    checkNic(handle)
    checkPhysicalDrive(handle)
    ledHealth(handle)
    #get_mac(handle)
    if(action == "full"):
        pciEquipment(handle)
        checkNic_full(handle)
        checkPhysicalDrive_full(handle)
        psuEquipment(handle)
        cpuEquipment(handle)
        memoryEquipment(handle)
        ledHealth_full(handle)
    handle.logout()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='check the Imc 3.x standalone server inventory')
    parser.add_argument('-i', '--host',dest="host", required=True,
                      help="[Mandatory] IMC IP Address")
    parser.add_argument('-u', '--username',dest="username", required=True,
                      help="[Mandatory] Account Username for IMC Login")
    parser.add_argument('-p', '--password',dest="password", required=True,
                      help="[Mandatory] Account Password for IMC Login")
    parser.add_argument('-a', choices=['full'], dest="action", required=False,
                       help="with full, it returns all requipment details")
    args = parser.parse_args()
    main(args)
