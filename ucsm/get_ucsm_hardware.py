#! /usr/bin/python
'''
description: get hardware details of each server from a single UCSM Pod
syntax: python get_ucsm_hardware.py -H uscm_pod_ip -u admin -p xxxxx
Author: lok.bruce@gmail.com
'''
import argparse
from ucsmsdk.ucshandle import UcsHandle

def checkBasic(handle):
    top = handle.query_dn("sys")
    print "UCSM name:%s  Mode:%s  VIP:%s" %(top.name, top.mode, top.address)

def getFI(handle):
    fi_list = []
    fis = handle.query_classid("NetworkElement")
    for fi in fis:
        fi = fi.dn, fi.model, fi.serial, fi.oob_if_ip, fi.operability
        fi_list.append(fi)
    return fi_list

def getFiFwVersion(handle):
    fws_list = []
    fws = handle.query_classid("FirmwareStatus")
    #{FirmwareStatus.DN:"sys/fw-status"}
    for fw in fws:
        #if "sys/fw-status" in fw.Dn or "sys/switch" in fw.Dn:
            fw = fw.dn[:-10], fw.package_version
            fws_list.append(fw)
    return fws_list

def getComputeRackUnit(handle):
    rack_list = []
    rackunits = handle.query_classid("ComputeRackUnit")
    for rackunit in rackunits:
        rackunit = rackunit.dn, rackunit.rn, rackunit.assigned_to_dn[12:], rackunit.model, rackunit.serial, rackunit.num_of_cpus, rackunit.total_memory
        rack_list.append(rackunit)
    return rack_list

def getBladeDetail(handle):
    chassis_list = []
    chassisitems = handle.query_classid("EquipmentChassis")
    for chassisitem in chassisitems:
        chassisitem = chassisitem.dn, chassisitem.model, chassisitem.serial
        chassis_list.append(chassisitem)

    blade_list = []
    bladeservers = handle.query_classid("ComputeBlade")
    for bladeserver in bladeservers:
        bladeserver = bladeserver.dn, bladeserver.rn, bladeserver.assigned_to_dn[12:], bladeserver.model, bladeserver.serial, bladeserver.num_of_cpus, bladeserver.total_memory
        blade_list.append(bladeserver)
    return chassis_list, blade_list

def getAdaptorUnit(handle):
    adaptor_list = []
    adaptorunits = handle.query_classid("AdaptorUnit")
    for adaptorunit in adaptorunits:
        adaptorunit = adaptorunit.dn[:-10], adaptorunit.rn, adaptorunit.blade_id, adaptorunit.chassis_id, adaptorunit.pci_slot, adaptorunit.model, adaptorunit.serial
        adaptor_list.append(adaptorunit)
    return adaptor_list

def getVnic(handle):
    vnic_list = []
    vnics = handle.query_classid("AdaptorHostEthIf")
    for vnic in vnics:
        print "dn:%s  name:%s  mac:%s" %(vnic.dn, vnic.name, vnic.mac)

def getStorageCtr(handle):
    hba_list = []
    hbas = handle.query_classid("StorageController")
    for hba in hbas:
        hba = hba.dn[:-20], hba.rn, hba.pci_slot, hba.model, hba.serial, hba.vendor
        hba_list.append(hba)
    return hba_list

def getDisk(handle):
    disk_list = []
    disks = handle.query_classid("StorageLocalDisk")
    for disk in disks:
        if int(disk.id) > 9:
            disk = disk.dn[:-28], disk.rn, disk.id, disk.size, disk.model, disk.serial
        else:
            disk = disk.dn[:-27], disk.rn, disk.id, disk.size, disk.model, disk.serial
        disk_list.append(disk)
    return disk_list


def main(args):
    handle = UcsHandle(args.host, args.username, args.password)

    try:
        handle.login()
    except Exception, err:
        print "Exception:", str(err)
        exit(1)

    basic = checkBasic(handle)
    fi_model = getFI(handle)
    fws_ver = getFiFwVersion(handle)
    chassis_model, blade_model = getBladeDetail(handle)
    rack_model = getComputeRackUnit(handle)
    adaptor_model = getAdaptorUnit(handle)
    disk_model = getDisk(handle)
    hba_model = getStorageCtr(handle)

    print "------ Fabric Interconnects ------"
    for i in fi_model:
        print '%s  Model:%s  SN:%s  IP:%s  ' % (i[0][4:], i[1], i[2], i[3]),
        for j in fws_ver:
            if i[0] == j[0]:
                print 'FW:%s' % j[1]

    print "------ Chassis ------"
    for i in chassis_model:
        print '%s  Model:%s  SN:%s  ' % (i[0], i[1], i[2])

    print "\n------ Blade Server Details ------"
    for i in blade_model:
        print 'DN:%s  SP:%s  Model:%s  SN:%s  CPU:%s  MEM:%sMB  ' % (i[0][4:],i[2],i[3],i[4],i[5],i[6]),
        for a in fws_ver:
            if i[0] == a[0]:
                print 'FW:%s' % a[1]
        for j in adaptor_model:
            if i[0] == j[0]:
                #print ", ".join(j)
                print 'VIC Card - %s  Model:%s  SN:%s' % (j[1],j[5],j[6])
        for k in hba_model:
            if i[0] == k[0]:
                #print ", ".join(k)
                print 'Storage Card - Model:%s  SN:%s  Vendir:%s ' % (k[3],k[4],k[5])
        for m in disk_model:
            if i[0] == m[0]:
                #print ", ".join(map(str,m))
                print '%s  Size:%s  Model:%s  SN:%s' % (m[1],m[3],m[4],m[5])
        print "\n-------------------------------"

    print "\n------ Rack Server Details ------"
    for a in rack_model:
        print 'DN:%s  SP:%s  Model:%s  SN:%s  CPU:%s  MEM:%sMB  ' % (a[0][4:],a[2],a[3],a[4],a[5],a[6]),
        for j in fws_ver:
            if a[0] == j[0]:
                print 'FW:%s' % j[1]
        for b in adaptor_model:
            if a[0] == b[0]:
                #print ", ".join(b)
                print 'VIC Card - PciSlot:%s  Model:%s  SN:%s' % (b[4],b[5],b[6])
        for c in hba_model:
            if a[0] == c[0]:
                #print ", ".join(c)
                print 'Storage Card - PciSlot:%s  Model:%s  SN:%s  Vendir:%s ' % (c[2],c[3],c[4],c[5])
        for d in disk_model:
            if a[0] == d[0]:
                #print ", ".join(map(str,d))
                print '%s  Size:%s  Model:%s  SN:%s' % (d[1],d[3],d[4],d[5])
        print "\n-------------------------------"

    handle.logout()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='to check UCS manager login')
    parser.add_argument('-i', '--host', dest="host", required=True)
    parser.add_argument('-u', '--username', dest="username", required=True)
    parser.add_argument('-p', '--password', dest="password", required=True)
    args = parser.parse_args()
    main(args)
