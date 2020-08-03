# ucs-tools

The project demonstrates the sample codes and scripts for general use of UCS build automation with Python ImcSdk for CIMC 3.x code release. it's also backward compatible to CIMC 2.x

Author: lok.bruce@gmail.com

## Prerequisites

Environment requirements for CIMC 3.x firmware code:
 - Python >= 2.7.5
 - ImcSdk >= 0.9.3
 - ucsmsdk >=0.9.4
 - OpenSSL >= 1.0.1
 - ruamel.yaml >= 0.10.13
 - ansible >= 2.4.0

## Understand of MO

In order to view/add/modify/delete any desired configuration in UCS, you need to know the basic things of Managed Object :

| MO | Example |
|--- | ---     |
| Class Id |AdaptorEthGenProfile |
| Distinguished Name (DN) | sys/rack-unit-1/adaptor-1/host-eth-eth1/general |
| Attribute Key | vlan |
| Desired Value | 100 |

There are few ways you can find out about the `dn`, `class_id`, and what attribute `key` and `value` that should looks like in UCS:
- view the imcsdk / ucsmsdk source codes at Github
- view the CIMC Visore Utility, eg: https://cimc_ip/visore.html
- verify from Interactive Python Shell, The following are the examples how you can get those information, quering by `dn` or by `class_id`

## CIMC
Let's try on Python IDLE, first login CIMC node
```
[root@~ /]# python
Python 2.7.5 (default, Jul 18 2017, 10:34:42)
...
>>> from imcsdk import *
>>> from imcsdk.imchandle import ImcHandle
>>> handle = ImcHandle('10.123.123.123','admin','mypassword')
>>> handle.login()
True
>>>
```

let's retrieve one of the bios settings from CIMC, by `class id`
```
>>> obj = handle.query_classid('BiosVfIntelVTForDirectedIO')
>>> print obj
[<imcsdk.mometa.bios.BiosVfIntelVTForDirectedIO.
BiosVfIntelVTForDirectedIO object at 0x7fe800710590>, <imcsdk.mometa.bios.
BiosVfIntelVTForDirectedIO.BiosVfIntelVTForDirectedIO object at
0x7fe800710550>]
>>>
>>> print obj[0]
Managed Object : BiosVfIntelVTForDirectedIO
--------------
child_action :None
dn :sys/rack-unit-1/bios/bios-settings/Intel-VT-for-directed-IO
rn :Intel-VT-for-directed-IO
status :None
vp_intel_vt_for_directed_io :enabled
vp_intel_vtd_coherency_support :enabled
vp_intel_vtd_interrupt_remapping:None
vp_intel_vtd_pass_through_dma_support:None
vp_intel_vtdats_support :enabled
>>>
```

Same object but retrieve by `dn`
```
>>> obj = handle.query_dn('sys/rack-unit-1/bios/bios-settings/Intel-VTfor-directed-IO')
>>> print obj
Managed Object : BiosVfIntelVTForDirectedIO
--------------
child_action :None
dn :sys/rack-unit-1/bios/bios-settings
/Intel-VT-for-directed-IO
rn :Intel-VT-for-directed-IO
status :None
vp_intel_vt_for_directed_io :enabled
vp_intel_vtd_coherency_support :disabled
vp_intel_vtd_interrupt_remapping:None
vp_intel_vtd_pass_through_dma_support:None
vp_intel_vtdats_support :enabled
>>>
```
finally remember to close out the session
```
>>> handle.logout()
True
>>>
```

## UCSM
Similar to CIMC, `ucsmsdk` is used to manage UCS manager. The syntax are similar, just the DN in UCSM is more complicated because one
single UCSM pod manage multiple servers

Login your UCSM Pod
```
[root@~ /]# python
...
>>> from ucsmsdk.ucshandle import UcsHandle;
>>> handle = UcsHandle('10.123.124.124', 'admin', 'mypass'); handle.
login()
True
>>>
```
retrieve one of the the blade server by dn
```
>>> obj = handle.query_dn("sys/chassis-2/blade-8")
>>> print obj
Managed Object              : ComputeBlade
--------------
Rn                          :blade-8
AvailableMemory             :393216
Lc                          :undiscovered
Descr                       :
TotalMemory                 :393216
SlotId                      :8
ServerId                    :2/8
NumOfEthHostIfs             :2
PartNumber                  :73-14689-04
AssignedToDn                :org-root/ls-nova1-013
Discovery                   :complete
Dn                          :sys/chassis-2/blade-8
OriginalUuid                :2f541b89-3083-430f-8684-e298cb498361
OperState                   :ok
PolicyLevel                 :0
Vendor                      :Cisco Systems Inc
LocalId                     :
UpgradeScenario             :not-applicable
PolicyOwner                 :local
NumOfCpus                   :2
CheckPoint                  :discovered
LowVoltageMemory            :regular-voltage
UsrLbl                      :
NumOfCores                  :20
LcTs                        :1970-01-01T01:00:00.000
Uuid                        :65508df6-e5a0-11e3-0a1c-1000000000be
Revision                    :0
ManagingInst                :B
Association                 :associated
Operability                 :operable
Status                      :None
Name                        :
ConnStatus                  :A,B
ConnPath                    :A,B
NumOfFcHostIfs              :0
NumOfCoresEnabled           :20
AdminState                  :in-service
Model                       :UCSB-B200-M3
Serial                      :FCHXXXXXXXX
OperQualifier               :
MemorySpeed                 :1333
AdminPower                  :policy
Vid                         :V06
Presence                    :equipped
MfgTime                     :2014-03-19T00:00:00.000
ScaledMode                  :none
ChassisId                   :2
OperPower                   :on
NumOfThreads                :40
NumOfAdaptors               :2
Availability                :unavailable
Ucs                         :hk-pod1-ucs01
>>>
...
```
or you can query a service profile name
```
>>> print handle.query_dn("org-root/ls-ova1-013")
```

The python codes in this repo demonstrate some of my coding works related to operation and automation for Cisco UCS
