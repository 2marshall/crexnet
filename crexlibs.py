import getpass
from netmiko import ConnectHandler
import difflib
import subprocess
import re
from ciscoconfparse import CiscoConfParse


class NodeSetup(object):

    """
    User must provide node_list list() and os_type str() when instantiating this object
    :param node_list - a list of IP's ['192.168.40.11', '192.168.40.10']
    :param os_type - a string matching the Netmiko OS type. Here are choices.  juniper, cisco_ios, cisco_asa, cisco_xe
    """

    def __init__(self, node_list, os_type):

        self.username = input('Username: ')
        self.password = getpass.getpass('Password: ')
        self.enable_pass = getpass.getpass('Enable Password: ')
        self.node_list = node_list
        self.os_type = os_type

    def initiate_connection(self, node):

        node_data = {
            'device_type': self.os_type,
            'ip': node,
            'username': self.username,
            'password': self.password,
            'secret': self.enable_pass,
            'port': 22,
            # 'verbose': True,
        }

        # performing connection to remote node

        node_connection = ConnectHandler(**node_data)

        return node_connection


def diff_data(data_before, data_after, node):

    """
    checks pre and post files and builds diff results file. data_before and data_after need to be lists
    :param data_before:
    :param data_after:
    :param node:
    :return:
    """

    diff_library = difflib.Differ()
    diff = diff_library.compare(data_before, data_after)    # data_before and data_after must be lists

    print("")
    print("\t========= CHANGES BELOW {} =========".format(node))
    print("")
    print('\n'.join(diff))
    print("")


def asa_top_50_top_talkers_bytes(node_connect, config_date, config_time, asa_node, single_host_check):

    """
    This provides you with the top 50 hosts who have consumed the most data through the ASA
    :param asa_node:
    :param config_date:
    :param config_time:
    :param node_connect:
    :param single_host_check:
    :return:
    """

    # show conn - save to local file
    # grab output and sort by top 50 hosts
    # cat /tmp/ASA_show_conn_ouput  |awk '{print $9, $1, $3, $5}' |sort -nr | head -50

    if single_host_check:

        print("")
        print("")
        print("\t========= {} Top 50 Top-Talkers by Bytes =========".format(single_host_check))
        print("")
        print("")

        filename = ('sh-conn-{}-{}-{}.log'.format(single_host_check, config_date, config_time))
        host_connections_output = node_connect.send_command_timing('sh conn address {}'.format(single_host_check), delay_factor=3)
        with open('asa_top_talkers_logs/{}'.format(filename), 'w') as file:
            file.write(host_connections_output)

    else:

        print("")
        print("")
        print("\t========= {} Top 50 Top-Talkers by Bytes =========".format(asa_node))
        print("")
        print("")
        print("\tPreparing Output.......")
        print("")

        filename = ('sh-conn-{}-{}-{}.log'.format(asa_node, config_date, config_time))
        host_connections_output = node_connect.send_command_timing('sh conn', delay_factor=4)
        with open('asa_top_talkers_logs/{}'.format(filename), 'w') as file:
            file.write(host_connections_output)

    # outputting the top 50 host connections by byte count on the prod asa

    top_50_talkers = subprocess.check_output(["cat asa_top_talkers_logs/%s | awk '{print $9, $1, $3, $5}' | sort -nr | tail -n +1 | head -50" % filename], shell=True, stderr=subprocess.STDOUT).decode('utf-8').split('\n')

    # iterating over each host and converting bytes to MB

    for host in top_50_talkers:

        try:

            host_total_bytes = int(re.search(r'^\d+', host).group(0))
            host_connection_output = re.search(r'(?<=,\s).+', host).group(0)
            host_bytes_to_kbytes = int(host_total_bytes / 1024)
            host_kbytes_to_mbytes_str = str(int(host_bytes_to_kbytes / 1024))
            host_kbytes_to_mbytes_int = host_bytes_to_kbytes / 1024

            # If the host has accumulated more than 50MB of data perform nslookup because this is most likely our culprit.

            if single_host_check:

                if host_kbytes_to_mbytes_int >= 1:

                    trouble_ip = re.search(r'(?<=[U,T][D,C]P\s).*(?=:\d{5})', host_connection_output).group(0)
                    nslookup_trouble_ip = subprocess.check_output(["nslookup %s" % trouble_ip], shell=True, stderr=subprocess.STDOUT).decode('utf-8')
                    nslookup_trouble_ip_parse = re.search(r'(?<=Non-authoritative answer:\n).*(?=\n)', nslookup_trouble_ip).group(0)
                    print("{} MB {}".format(host_kbytes_to_mbytes_str, host_connection_output))
                    print("")
                    print("NSLOOKUP on {} = {}".format(trouble_ip, nslookup_trouble_ip_parse))
                    print("")

                else:

                    print("{} MB {}".format(host_kbytes_to_mbytes_str, host_connection_output))

            else:

                print("{} MB {}".format(host_kbytes_to_mbytes_str, host_connection_output))

        except:

            print("")
            print("")
            subprocess.call(["rm -rvf asa_top_talkers_logs/%s" % filename], shell=True)
            print("")
            print("")

    return


def asa_top_50_host_embryonic_conns(node_connect, config_date, config_time):

    host_embryonic_conn_output = node_connect.send_command('show local-host | in host|embryonic').split('\n')
    config_parsed = CiscoConfParse(host_embryonic_conn_output, syntax='ios')

    for parent in config_parsed.find_objects(r'^local'):  # Finding objects beginning with Extended and begin parsing children. there is only one because we were specific on the access-list being displayed

        # Grab Host IP from Object

        host_ip = re.search(r'(?<=<).*(?=>)', parent.text).group(0)

        for child in parent.children:
            # Grab Total Host Embryonic Connections

            embryonic_conn_count = int(re.search(r'(?<=\s=\s).*', child.text).group(0))

        # perform If statement on embryonic connection count so we only display hosts with more than 100 half open connections

        if embryonic_conn_count >= 100:

            print("Host IP: {} Half-Open Connections: {}".format(host_ip, embryonic_conn_count))

            asa_top_50_top_talkers_bytes(node_connect, config_date, config_time, host_ip, single_host_check=host_ip)

        else:

            print("")
            print("\t *** GOOD NEWS NO HOSTS W/OVER 100 HALF-OPEN CONNECTIONS ***")

    return
