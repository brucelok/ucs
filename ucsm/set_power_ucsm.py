#! /usr/bin/python
import argparse
import time
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.mometa.ls.LsPower import LsPowerConsts
from ucsmsdk.mometa.ls.LsPower import LsPower

DOCUMENTATION = '''
---
description: power on, off, cycle a server in UCS manager by service profile name

prerequisite:
  - a physical node with service profile assoicated
  - service profile name is same as Ansible hostname

description:
  - Logs in to a UCS manager
  - check if the service profile exists
  - check the current operation power status
  - perform power on/off or power cycle
  - poll the server and return when the expected operation state is achieved
option:
  state:
    description: action to power on, off or power cycle a server
    choices: ['on', 'off', 'reset']
  name:
    description: service profile name in UCSM, usually same as Linux hostname
    choices: string

requirements:
  ucsmsdk==0.9.3.1

Author: lok.bruce@gmail.com
'''

def find_sp_dn(handle, sp_name):
    '''
    description: return the full DN path of target service profile name
    args:
        handle(UcsHandle)
        sp_name: Service Profile name (hostname)
    returns:
        sp_dn: full DN path of target service profile
        eg: 'org-root/org-SJC/org-SJC05-DCI05N/org-ENG-BM/org-SJC-DCI05N-UCS22/ls-sjc5-cfc-c-nova01-005'
            'org-root/ls-csi-a-nova2-010'
    '''

    sp_dn = ''
    dn_list = []
    bladeservers = handle.query_classid("ComputeBlade")
    rackunits = handle.query_classid("ComputeRackUnit")

    # loop through all blade servers
    for blade in bladeservers:
        dn_list.append(blade.assigned_to_dn)
    # loop through all rack servers
    for rack in rackunits:
        dn_list.append(rack.assigned_to_dn)

    dn_list.sort()
    for x in dn_list:
        #print x
        if sp_name in x:
            sp_dn = x

    return sp_dn

def check_power(handle, sp_dn):
    '''
    description: check if service profile and its assoicated status,
    query the physical node dn and get power status.

    Args:
        handle(UcsHandle)
        sp_dn(str): service profile full dn
    Returns:
        oper_power(str): operation power, eg: 'on', 'off'
        oper_state(str): overall operation status, eg: 'ok', 'power-off', 'restart'
    '''

    mo = handle.query_dn(sp_dn)
    if not mo:
        raise ValueError("SP '%s' not exist" % sp_dn)

    if mo.assoc_state != 'associated':
        raise ValueError("SP '%s' not assoicated" % sp_dn)

    pn = handle.query_dn(mo.pn_dn)

    return pn.oper_power, pn.oper_state

def set_power_state(handle, sp_dn, state, oper_power):
    '''
    description: take action to power on, off, cycle the server,
    and then polls the server overall status.

    Args:
        handle(UcsHandle)
        sp_dn(str): service profile full dn
        state(str): desired power action
        oper_power(str): current power state
    Returns:
        bool
    '''
    mo = handle.query_dn(sp_dn)

    state_dict = {
        "on": LsPowerConsts.STATE_UP,
        "off": LsPowerConsts.STATE_DOWN,
        "reset": LsPowerConsts.STATE_CYCLE_IMMEDIATE
    }

    if state == 'reset':
        if oper_power == 'on':
            LsPower(parent_mo_or_dn=mo, state=state_dict['reset'])
        elif oper_power == 'off':
            LsPower(parent_mo_or_dn=mo, state=state_dict['on'])
    elif state == 'on':
        LsPower(parent_mo_or_dn=mo, state=state_dict['on'])
    elif state == 'off':
        LsPower(parent_mo_or_dn=mo, state=state_dict['off'])

    handle.set_mo(mo)
    handle.commit()
    time.sleep(2)

    # poll untill the server goes to expected operation state
    _wait_for_power_state(handle, sp_dn, state)
    return True

def _wait_for_power_state(handle, sp_dn, state):
    '''
    description:  this is called after power state change has been triggered,
    it will poll the server every 5 sec and return when the expected operation state is achieved

    Args:
        handle(UcsHandle)
        sp_dn(str): service profile full dn
        state(str): desired power action
    Returns:
        bool
    '''
    timeout = 300
    interval = 5
    wait_time = 0

    _, oper_state = check_power(handle, sp_dn)

    if state in ("on", "reset"):
        # when server back online and running, oper_state should be 'ok'
        while oper_state != 'ok':
            print "Now operation state: %s" %oper_state
            if wait_time > timeout:
                raise ValueError('Power {%s} did not complete within {%s} sec' % (state, timeout))
            time.sleep(interval)
            wait_time += interval
            _, oper_state = check_power(handle, sp_dn)
        print "Power {%s} on {%s} succeeded in {%s} sec" %(state, sp_dn, wait_time)

    elif state == "off":
        # when server power-off, oper_state should be 'power-off'
        while oper_state != 'power-off':
            print "Now operation state: %s" %oper_state
            if wait_time > timeout:
                raise ValueError('Power {%s} did not complete within {%s} sec' % (state, timeout))
            time.sleep(interval)
            wait_time += interval
            _, oper_state = check_power(handle, sp_dn)
        print "Power {%s} on {%s} succeeded in {%s} sec" %(state, sp_dn, wait_time)

def main(args):
    handle = UcsHandle(args.host, args.username, args.password)
    state = args.state
    sp_name = args.name

    try:
        handle.login()
    except Exception, err:
        print "Exception:", str(err)
        exit(1)

    sp_dn = find_sp_dn(handle, sp_name)
    print "matched: %s" %sp_dn

    oper_power, _ = check_power(handle, sp_dn)

    if state == 'check':
        print oper_power
    elif oper_power != state:
        # triggers power action
        try:
            set_power_state(handle, sp_dn, state, oper_power)
        except Exception as err:
            print "Exception:", str(err)

    handle.logout()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='action to power on, off, cycle a server in UCSM')
    parser.add_argument('-i', '--host', dest="host", required=True)
    parser.add_argument('-u', '--username', dest="username", required=True)
    parser.add_argument('-p', '--password', dest="password", required=True)
    parser.add_argument('-n', '--name', dest="name", required=True)
    parser.add_argument('-s', '--state', choices=['check', 'on', 'off', 'reset'],
                        dest="state", required=True)
    args = parser.parse_args()
    main(args)
