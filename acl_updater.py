from ciscoconfparse import CiscoConfParse
import re
import getpass
from netmiko import ConnectHandler
# from easysnmp import Session
import difflib

#
# ACL Updater will Grab the OUTSIDE_ACL on both ASR's
#


def netmiko_device_data(node_ip, username, password, enable_secret):

    netmiko_device_data = {
        'device_type': 'cisco_ios',
        'ip': node_ip,
        'username': username,
        'password': password,
        'secret': enable_secret,
        'port': 22,
        # 'verbose': True,
    }

    return netmiko_device_data


# def netmiko_node_os_type(node):
#     """
#     :param node: device name
#     :return:
#     """
#
#     session = Session(hostname=node, community='OJ3yEgsBQ7', version=2)
#
#     try:
#
#         device_data = str(session.get('.1.3.6.1.2.1.1.1.0'))
#
#         if "Juniper" in device_data:
#             netmiko_node_os_type = 'juniper'
#         elif "Cisco" in device_data:
#             netmiko_node_os_type = 'cisco_ios'
#         elif "Arista" in device_data:
#             netmiko_node_os_type = 'arista_eos'
#         elif "Aruba" in device_data:
#             netmiko_node_os_type = 'aruba_os'
#
#         return netmiko_node_os_type  # Returns the value derived from the chosen node_type variable above. so if it's Junper the string value is juniper. if it's Cisco the assignement is to cisco_ios. Arista it's arista_eos
#         # This value can than be referenced using the get_device_type function.
#         # return to set variables to be a value from a function
#
#     except:
#
#         # The above SNMP get string is invalid so defaulting to a linux_ssh node type
#
#         netmiko_node_os_type = 'linux_ssh'
#         return netmiko_node_os_type


def netmiko_get_username():
    netmiko_get_username = input("Username: ")
    return netmiko_get_username


def netmiko_get_password():
    netmiko_get_password = getpass.getpass()
    return netmiko_get_password

def netmiko_get_enable_pass():
    netmiko_get_enable_password = getpass.getpass('Enable Password: ')
    return netmiko_get_enable_password


def node_connection(node, username, password, enable_pass):
    """
    Setting up and connecting to remote Node via ssh
    :return:
    """

    # os_type, ciscoconfparse_node_type = netmiko_node_os_type(node)
    device_data = netmiko_device_data(node, username, password, enable_pass)
    device_connection = ConnectHandler(**device_data)

    return device_connection


def node_list():
    node_list = ['192.168.40.10', '192.168.40.11']
    # node_list = ['lab1-1-cc01']
    # node_list_cleaned = []
    # for node in node_list:
    #     node_clean = node.strip()
    #     node_list_cleaned.append(node_clean)

    return node_list


def node_credential_setup():
    """
    Joining All Device Login Functions into a Single Function Call. Username, Password, Node List, Show Commands
    :return:
    """

    username = netmiko_get_username()
    password = netmiko_get_password()
    enable_pass = netmiko_get_enable_pass()
    nodes = node_list()

    return username, password, enable_pass, nodes


def diff_data(data_before, data_after, node):

    """ checks pre and post files and builds diff results file. data_before and data_after need to be lists
    :return:
    """

    diff_library = difflib.Differ()
    diff = diff_library.compare(data_before, data_after)    # data_before and data_after must be lists

    print("")
    print("\t========= CHANGES BELOW {} =========".format(node))
    print("")
    print('\n'.join(diff))
    print("")


def acl_updater():

    """
    Primary Script Being Called by crexnet.py which will add either a host or subnet as the next ACL in the COMMAND
    :return:
    """

    # come up with way to integrate both subnets and hosts on a single line

    # Global Variables

    PERMIT_SEQUENCE_NUM = 100000
    SEQUENCE_SKIP = 10
    COMMAND = 'show access-list OUTSIDE_ACL'

    print("\t========= ACL UPDATER =========")
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

    username, password, enable_pass, nodes = node_credential_setup()    # grabbing user credentials for login

    for node in nodes:

        device_connection = node_connection(node, username, password, enable_pass)   # creating device connection
        device_connection.enable()  # entering enable mode
        command_output_before = device_connection.send_command(COMMAND).split('\n')    # sending command to node

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
                            device_connection.send_config_set(commands)
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
                            device_connection.send_config_set(commands)
                            final_sequence_num += SEQUENCE_SKIP

        # writing config to ASR

        device_write = device_connection.send_command('wr')

        # grabbing post output config and performing DIFF here of command_output before and after

        command_output_after = device_connection.send_command(COMMAND).split('\n')  # sending command to node

        # performing diff on ACL before and after

        diff_data(command_output_before, command_output_after, node)

        # sending write output to user

        print("\t========= CHANGE WRITE EVIDENCE {} =========".format(node))
        print("")
        print(device_write)
        print("")
        print("")




