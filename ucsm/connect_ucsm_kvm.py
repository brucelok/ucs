#! /usr/bin/python
'''
Description:
    The script allows your terminal to directly connect to the KVM-Console without launching UCS manager
Sytnax:
    connect_ucsm_kvm.py -i [UCSM VIP/Pod name] -u [user] -p [password] -n [service profile name]
Example:
    $ python connect_ucsm_kvm.py -i rtp1-dcm02n-ucs07 -u $USER -p $PASS -n rtp1-osc-nova1-001

Author: lok.bruce@gmail.com

TO DO:
    use ssh paramiko instead of expect for ssh
'''
import argparse, socket, sys
from ucsmsdk.ucshandle import UcsHandle

def find_sp_dn(handle, sp_name):
    '''
    description: return the full DN path of target service profile name
    args:
        handle(UcsHandle)
        sp_name: Service Profile name (hostname)
    returns:
        sp_dn: full DN path of target service profile
        eg: 'org-root/org-SJC/org-SJC05-DCI05N/org-ENG-BM/org-SJC-DCI05N-UCS22/ls-sjc5-cfc-c-nova01-005'
            'org-root/ls-rtp10-2-csl-a-nova1-012'
    '''
    sp_dn = None
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
        if sp_name in x:
            sp_dn = x
            break

    if sp_dn is None:
        print "service profile %s is not found" %sp_dn
        return False
    else:
        print "service profile full DN: %s" %sp_dn
        return sp_dn


def get_kvm_ip(handle, sp_dn):
    '''
    description: return the management IP of physical server
        example sp_dn:  org-root/ls-rtp10-2-csl-a-nova1-012
        example pn_dn:  sys/chassis-2/blade-8
        example /mgmt/if-1 dn:  sys/chassis-2/blade-8/mgmt/if-1
    args:
        handle(UcsHandle)
        sp_dn: Service Profile full dn
    returns:
        ip: IP address
    '''
    pn = None
    ip = None

    # get physical 'dn' from service profile 'dn'
    pn = handle.query_dn(sp_dn).pn_dn
    print "physical server full DN: %s" %pn

    # parse pn to get mgmt IP
    ip = handle.query_dn(pn + '/mgmt/if-1').ext_ip

    if ip is None or ip == '0.0.0.0':
        print "Managment IP is not configured"
        return False
    else:
        return ip

def ssh_kvm(ip, username, password):
    '''
    description: ssh to KVM console
    args:
        ip: the KVM IP address returned from get_kvm_ip()
        username: UCSM login username parsed from args.username
        password: UCSM login password parsed from args.password
    returns:
        interaction KVM console TTY
    '''
    import pexpect

    # connecting to target KVM IP

    print "ssh to KVM console:", ip
    child = pexpect.spawn('ssh %s@%s' % (username, ip))
    child.logfile = sys.stdout
    child.timeout = 20
    try:
        i = child.expect(['password:', 'continue connecting (yes/no)?'])
        if i == 0:
            child.sendline(password)
        elif i == 1:
            child.sendline('yes')
            child.expect('password:')
            child.sendline(password)
    except pexpect.TIMEOUT:
        print "TIMEOUT"

    # two outputs expected
    i = child.expect(['session', 'Exit', 'CISCO Serial Over LAN disabled*'])

    if (i == 0 or i == 1 ):
        print child.before
        child.interact()

    elif i == 2:
        print "CISCO Serial Over LAN is NOT enabled, exiting"
        child.close()
        exit(1)

def main():
    parser = argparse.ArgumentParser(description='connect UCSM-managed server KVM console over terminal')
    parser.add_argument('-i', '--host', dest="host", required=True,
                        help="UCSM VIP address or Pod name")
    parser.add_argument('-u', '--username', dest="username", required=True)
    parser.add_argument('-p', '--password', dest="password", required=True)
    parser.add_argument('-n', '--name', dest="name", required=True,
                        help="service profile name")
    args = parser.parse_args()

    try:
        socket.gethostbyname(args.host)
    except socket.gaierror, err:
        print "cannot resolve hostname: ", args.host, err
        exit(1)

    handle = UcsHandle(args.host, args.username, args.password)
    sp_name = args.name

    try:
        handle.login()
    except Exception, err:
        print "Exception:", str(err)
        exit(1)

    sp_dn = find_sp_dn(handle, sp_name)
    kvm_ip = get_kvm_ip(handle, sp_dn)
    handle.logout()
    print "connecting to %s" %kvm_ip
    ssh_kvm(kvm_ip, args.username, args.password)

if __name__ == '__main__':
    main()
