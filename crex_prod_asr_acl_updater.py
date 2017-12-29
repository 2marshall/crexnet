from ciscoconfparse import CiscoConfParse
import re
from crexlibs import NodeSetup
from crexlibs import diff_data

#
# ACL Updater will Update the OUTSIDE_ACL on both LEVEL3 and COX ASR's
#

#
# --- New Features to Add ---
#
# 1. Ability to remove ACL's
# 2.

PERMIT_SEQUENCE_NUM = 100000
SEQUENCE_SKIP = 10
COMMAND = 'show access-list OUTSIDE_ACL'
OS_TYPE = 'Cisco_IOS'
NODE_LIST = ['192.168.40.10', '192.168.40.11']


def acl_updater():

    """
    Primary Script Being Called by crexnet.py which will add either a host or subnet as the next ACL in the COMMAND
    :return:
    """

    # come up with way to integrate both subnets and hosts on a single line

    # Global Variables

    print("")
    print("\t========= Prod ASR ACL UPDATER =========")
    print("")
    print("Are you Adding SUBNETS or HOSTS to the ACL?")
    subnets_or_hosts = input(">>> ")
    print(subnets_or_hosts)
    while subnets_or_hosts.lower() != 'hosts' and subnets_or_hosts.lower() != 'subnets':
        print("Type either SUBNETS or HOSTS")
        subnets_or_hosts = input(">>> ")
    if subnets_or_hosts.lower() == 'hosts':
        while True:     # while true is basically always true until we manually break out of loop
            host_issues = 0
            print("")
            print("Enter a space after each IP (99.11.33.11 11.22.33.44 56.11.123.56)")
            denied_hosts = input('>>> ').split()
            print("")
            for host in denied_hosts:
                if not re.match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", host):  # if there is a match and regex works great we pass to go onto the next subnet
                    host_issues = 1
                    break
            if host_issues == 0:
                print("")
                break

    elif subnets_or_hosts.lower() == 'subnets':
        while True:      # while true is basically always true until we manually break out of loop
            subnet_issues = 0
            print("")
            print("Enter each subnet in CIDR Notation with a Space after each: 185.16.0.0/16 56.16.101.0/24 98.103.104.128/25")
            denied_subnets = input('>>> ').split()
            for subnet in denied_subnets:
                if not re.match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\/\d+$", subnet):  # if there is a match and regex works great we pass to go onto the next subnet
                    subnet_issues = 1
                    break
            if subnet_issues == 0:
                print("")
                break

    # Initiating the class to setup the connection to the remote nodes

    node_setup = NodeSetup(NODE_LIST, OS_TYPE)

    for node in node_setup.node_list:

        node_connect = node_setup.initiate_connection(node, OS_TYPE)
        node_connect.enable()  # entering enable mode
        command_output_before = node_connect.send_command(COMMAND).split('\n')    # sending command to node

        # sending command through ciscoconfparse so we can begin iterating over the seq. numbers

        config_parsed = CiscoConfParse(command_output_before, syntax='ios')

        prior_sequence_num = int()

        for object in config_parsed.find_objects(r'^Extended'):  # Finding objects beginning with Extended and begin parsing children. there is only one because we were specific on the access-list being displayed
            for child in object.children:  # beginning loop of each sequence number within extended ACL
                working_sequence_num = int(re.search(r'^\s+\d+', child.text).group(0))

                if working_sequence_num != PERMIT_SEQUENCE_NUM:

                    prior_sequence_num = working_sequence_num   # this will track with the working_sequence_num variable so we will be ready to use the prior_sequence_num variable later

                else:   # if final_sequence_num finally equals PERMIT_SEQUENCE_NUM we have reached the end of the ACL and can find the next seq. number

                    final_sequence_num = prior_sequence_num + SEQUENCE_SKIP  # here we want to take the prior sequence number and add 10. this will give us the next sequence number in the ACL series

                    if final_sequence_num == PERMIT_SEQUENCE_NUM:   # if final_sequence_num is equal to PERMIT_SEQUENCE_NUM we need to increase the PERMIT sequence num because we have reached reached a SEQ which is SEQUENCE_SKIP before PERMIT_SEQUENCE_NUM

                        print("")
                        print("**** ERROR: PERMIT SEQUENCE NUM REACHED on {}. PLEASE INCREASE PERMIT SEQ NUMBER ****".format(node))
                        print("")

                        for output_line in command_output_before:
                            print(output_line)

                        continue

                    elif subnets_or_hosts == 'hosts':

                        for host in denied_hosts:

                            commands = ['ip access-list extended OUTSIDE_ACL', '{} deny ip host {} any'.format(final_sequence_num, host)]
                            node_connect.send_config_set(commands)
                            final_sequence_num += SEQUENCE_SKIP

                    elif subnets_or_hosts == 'subnets':

                        for subnet in denied_subnets:

                            subnet_and_wildcard_mask = re.search(r'(.*(?=\/))\/(\d+)', subnet)

                            if subnet_and_wildcard_mask.group(2) == '16':
                                wildcard_mask = '0.0.255.255'

                            elif subnet_and_wildcard_mask.group(2) == '17':
                                wildcard_mask = '0.0.127.255'

                            elif subnet_and_wildcard_mask.group(2) == '18':
                                wildcard_mask = '0.0.63.255'

                            elif subnet_and_wildcard_mask.group(2) == '19':
                                wildcard_mask = '0.0.31.255'

                            elif subnet_and_wildcard_mask.group(2) == '20':
                                wildcard_mask = '0.0.15.255'

                            elif subnet_and_wildcard_mask.group(2) == '21':
                                wildcard_mask = '0.0.7.255'

                            elif subnet_and_wildcard_mask.group(2) == '22':
                                wildcard_mask = '0.0.3.255'

                            elif subnet_and_wildcard_mask.group(2) == '23':
                                wildcard_mask = '0.0.1.255'

                            elif subnet_and_wildcard_mask.group(2) == '24':
                                wildcard_mask = '0.0.0.255'

                            elif subnet_and_wildcard_mask.group(2) == '25':
                                wildcard_mask = '0.0.0.127'

                            elif subnet_and_wildcard_mask.group(2) == '26':
                                wildcard_mask = '0.0.0.63'

                            elif subnet_and_wildcard_mask.group(2) == '27':
                                wildcard_mask = '0.0.0.31'

                            elif subnet_and_wildcard_mask.group(2) == '28':
                                wildcard_mask = '0.0.0.15'

                            elif subnet_and_wildcard_mask.group(2) == '29':
                                wildcard_mask = '0.0.0.7'

                            elif subnet_and_wildcard_mask.group(2) == '30':
                                wildcard_mask = '0.0.0.3'

                            elif subnet_and_wildcard_mask.group(2) == '31':
                                wildcard_mask = '0.0.0.1'

                            else:
                                wildcard_mask = None
                                print("MASK NOT CORRECTLY SPECIFICED")

                            commands = ['ip access-list extended OUTSIDE_ACL', '{} deny ip {} {} any'.format(final_sequence_num, subnet_and_wildcard_mask.group(1), wildcard_mask)]
                            node_connect.send_config_set(commands)
                            final_sequence_num += SEQUENCE_SKIP

        # writing config to ASR

        device_write = node_connect.send_command('wr')

        # grabbing post output config and performing DIFF here of command_output before and after

        command_output_after = node_connect.send_command(COMMAND).split('\n')  # sending command to node

        # performing diff on ACL before and after

        diff_data(command_output_before, command_output_after, node)

        # sending write output to user

        print("\t========= CHANGE WRITE EVIDENCE {} =========".format(node))
        print("")
        print(device_write)
        print("")
        print("")




