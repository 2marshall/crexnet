import getpass
from netmiko import ConnectHandler
import difflib
import subprocess
import re
import math
from ciscoconfparse import CiscoConfParse


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    power = math.pow(1024, i)
    size = round(size_bytes / power, 2)
    return "{} {}".format(size, size_name[i])


class NetAutomationTasks:

    """
    Variables User must provide node, os_type, config_date, config_time when initiating the object.
    Purpose: Provide a connect handler to the node with all the required configuration to perform an ssh connection to the node
    :param username - username str()
    :param password - password for login to node
    :param enable_pass - enable password for login to node
    :param node - node ip str()
    :param os_type - a string matching the Netmiko OS type. Here are choices.  juniper, cisco_ios, cisco_asa, cisco_xe
    :param config_date - passed in date str(datetime.today().strftime('%m%d%Y'))
    :param config_time - passed in time str(datetime.today().strftime('%I%M%S%p'))
    """

    def __init__(self, os_type):

        self.username = None
        self.password = None
        self.enable_pass = None
        self.os_type = os_type
        self.connection = None
        self.working_username = None
        self.working_password = None
        self.working_enable_pass = None
        self.bypass_username_pass_check = False
        self.final_ace_list = None
        self.existing_ace_list = None
        self.added_removed_aces = None

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
        self.connection = ConnectHandler(**node_data)

    # Passing in the run_function method with the name of the function being executed along with unique variables used in functions below.
    # This allows for any call within this class to be executed

    def ios_acl_updater(self, node_list, node_names):
        """
        Updates outside ACL on Crexendo's Production ASR's
        :return:
        """

        PERMIT_SEQUENCE_NUM = 100000
        SEQUENCE_SKIP = 10
        COMMAND = 'show access-list OUTSIDE_ACL'

        print("")
        print("\t========= Prod ASR ACL UPDATER =========")
        print("")
        print("Are you Adding(A) or Removing(R) to the ACL?")
        add_or_remove_acl = input("A or R >>> ")
        while add_or_remove_acl.lower() != 'a' and add_or_remove_acl.lower() != 'r':
            print("Type either A for ADD or R for REMOVE")
            add_or_remove_acl = input("A or R >>> ")
        if 'a' in add_or_remove_acl.lower():
            add_or_remove_acl = 'add'
        else:
            add_or_remove_acl = 'remove'
        print("Are these SUBNETS or HOSTS Being {} the ACL?".format(add_or_remove_acl))
        subnets_or_hosts = input(">>> ")
        while subnets_or_hosts.lower() != 'hosts' and subnets_or_hosts.lower() != 'subnets':
            print("Type either SUBNETS or HOSTS")
            subnets_or_hosts = input(">>> ")
        if subnets_or_hosts.lower() == 'hosts':
            while True:  # while true is basically always true until we manually break out of loop
                host_issues = 0
                print("")
                print("Enter a space after each IP (99.11.33.11 11.22.33.44 56.11.123.56)")
                denied_hosts = input('>>> ').split()
                print("")
                for host in denied_hosts:
                    if not re.match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", host):  # if there is a match and regex works great we pass to go onto the next subnet
                        host_issues = 1
                        print("One of HOSTS Entered was not in the correct format: {}".format(host))
                        break
                if host_issues == 0:
                    print("")
                    break

        elif subnets_or_hosts.lower() == 'subnets':
            while True:  # while true is basically always true until we manually break out of loop
                subnet_issues = 0
                print("")
                print("Enter each subnet in CIDR Notation with a Space after each: 185.16.0.0/16 56.16.101.0/24 98.103.104.128/25")
                denied_subnets = input('>>> ').split()
                for subnet in denied_subnets:
                    if not re.match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\/\d{1,2}$", subnet):  # if there is a match and regex works great we pass to go onto the next subnet
                        subnet_issues = 1
                        print("One of SUBNETS Entered was not in the correct format: {}".format(subnet))
                        break
                if subnet_issues == 0:  # if all subnets are accurately typed break out of loop and move forward
                    print("")
                    break

        # Initiate Connection to devices
        for node, node_name in zip(node_list, node_names):
            self.final_ace_list = list()
            self.existing_ace_list = list()
            self.added_removed_aces = list()
            if not self.bypass_username_pass_check:
                self.username = input('Username: ')
                self.password = getpass.getpass('Password: ')
                self.enable_pass = getpass.getpass('Enable Password: ')
                while True:
                    try:
                        self.initiate_connection(node)
                        self.connection.enable()
                        self.bypass_username_pass_check = True
                        break
                    except Exception as err:
                        if 'enable mode' in str(err):
                            self.enable_pass = getpass.getpass('Enable Password Wrong Try Again: ')
                        elif 'Authentication failure' in str(err):
                            self.password = getpass.getpass('Password Wrong Try Again: ')
                        pass
            else:
                self.initiate_connection(node)
                self.connection.enable()
            print("")
            print("\t========= Working on {} .... =========".format(node_name))
            print("")
            command_output_before = self.connection.send_command(COMMAND).split('\n')  # sending command to node
            # sending command through ciscoconfparse so we can begin iterating over the seq. numbers
            config_parsed = CiscoConfParse(command_output_before, syntax='ios')
            prior_sequence_num = int()
            #  7400 deny ip host 46.166.187.4 any
            #  7410 deny ip host 185.107.94.42 any
            #  7420 deny ip host 167.114.65.187 any (10315 matches)
            #  7430 deny ip host 167.114.64.3 any (10675 matches)
            #  7450 deny ip host 192.99.100.235 any (10343 matches)
            #  7460 deny ip host 102.165.38.146 any (65 matches)
            #  7470 deny ip host 167.114.65.206 any (3380 matches)
            #  7490 deny ip host 147.135.79.52 any (10425 matches)
            #  7500 deny ip host 51.75.88.121 any (6250 matches)
            #  7520 deny ip host 104.222.153.8 any
            #  7530 deny ip host 216.244.65.106 any (100 matches)
            #  7540 deny ip host 172.245.249.36 any
            #  7550 deny ip host 209.126.105.145 any
            #  7560 deny ip host 75.127.6.10 any
            #  7570 deny ip host 195.154.173.208 any
            #  7580 deny ip host 185.217.69.173 any
            #  7590 deny ip host 147.135.54.83 any
            #  7600 deny ip host 102.165.33.46 any (18 matches)
            #  100000 permit ip any any (3160903558 matches)

            #  62.138.7.200
            #  188.138.33.79
            #  -     6840 deny ip 185.53.91.0 0.0.0.255 any (1034 matches)
            if subnets_or_hosts.lower() == 'hosts':
                for line in command_output_before:
                    for host in denied_hosts:
                        if host in line:
                            self.existing_ace_list.append(host)
                # Compare existing_ace_list to denied_hosts and apply to final ace list we send to devices
                self.final_ace_list = set(denied_hosts) - set(self.existing_ace_list)
            elif subnets_or_hosts.lower() == 'subnets':
                for line in command_output_before:
                    for subnet in denied_subnets:
                        subnet = subnet.split('/')[0]
                        if subnet in line:
                            self.existing_ace_list.append(subnet)
                # Compare existing_ace_list to denied_hosts and apply to final ace list we send to devices
                self.final_ace_list = set(denied_subnets) - set(self.existing_ace_list)
            # If final_ace_list contains no new host entries continue to next node and spit out message to user
            # Find the differences from the
            # Removing HOSTS/SUBNETS here
            if add_or_remove_acl.lower() == 'remove':
                for object in config_parsed.find_objects(r'^Extended'):  # Finding objects beginning with Extended and begin parsing children. there is only one because we were specific on the access-list being displayed
                    for child in object.children:  # beginning loop of each sequence number within extended ACL
                        if subnets_or_hosts.lower() == 'hosts':
                            acl_host_ip = child.text.split()[4] # 7500 deny ip host 51.75.88.121 any
                            acl_entry = child.text.strip()
                            acl_entry_seq_num = child.text.split()[0]
                            for denied_host in denied_hosts:
                                if denied_host == acl_host_ip: # if host is equal to the acl host entry we are on
                                    print("Host {} ACE Found!!! Do you want to Remove?".format(denied_host))
                                    print("ACE Entry to Remove : {}".format(acl_entry))
                                    remove_ace_entry = input("y/n >>> ")
                                    if 'y' in remove_ace_entry.lower():
                                        # connect and remove the ACE entry
                                        commands = ['ip access-list extended OUTSIDE_ACL',
                                                    'no {}'.format(acl_entry_seq_num)]
                                        self.connection.send_config_set(commands)
                                        self.added_removed_aces.append(acl_entry)
                        elif subnets_or_hosts.lower() == 'subnets':
                            if 'host' in child.text.split()[3] or 'any' in child.text.split()[3]:
                                continue
                            acl_subnet = child.text.split()[3] # 6810 deny ip 37.49.224.0 0.0.7.255 any (962 matches)
                            wildcard_mask = child.text.split()[4]  # 6810 deny ip 37.49.224.0 0.0.7.255 any (962 matches)
                            acl_entry = child.text.strip()
                            acl_entry_seq_num = child.text.split()[0]
                            # convert from wildcard to cidr notation
                            for denied_subnet in denied_subnets:
                                # subnet_and_wildcard_mask = re.search(r'(.*(?=\/))\/(\d+)', acl_mask)
                                if wildcard_mask == '0.0.255.255':
                                    cidr_mask = '16'
                                elif wildcard_mask == '0.0.127.255':
                                    cidr_mask = '17'
                                elif wildcard_mask == '0.0.63.255':
                                    cidr_mask = '18'
                                elif wildcard_mask == '0.0.31.255':
                                    cidr_mask = '19'
                                elif wildcard_mask == '0.0.15.255':
                                    cidr_mask = '20'
                                elif wildcard_mask == '0.0.7.255':
                                    cidr_mask = '21'
                                elif wildcard_mask == '0.0.3.255':
                                    cidr_mask = '22'
                                elif wildcard_mask == '0.0.1.255':
                                    cidr_mask = '23'
                                elif wildcard_mask == '0.0.0.255':
                                    cidr_mask = '24'
                                elif wildcard_mask == '0.0.0.127':
                                    cidr_mask = '25'
                                elif wildcard_mask == '0.0.0.63':
                                    wildcard_mask = '26'
                                elif wildcard_mask == '0.0.0.31':
                                    wildcard_mask = '27'
                                elif wildcard_mask == '0.0.0.15':
                                    wildcard_mask = '28'
                                elif wildcard_mask == '0.0.0.7':
                                    wildcard_mask = '29'
                                elif wildcard_mask == '0.0.0.3':
                                    wildcard_mask = '30'
                                elif wildcard_mask == '0.0.0.1':
                                    wildcard_mask = '31'
                                else:
                                    wildcard_mask = None
                                    print("WILDCARD MASK TO CIDR CONVERSION FAILED. NO MATCH FOUND:  {}".format(acl_entry))
                                    exit(0)
                                acl_subnet_plus_mask = '{}/{}'.format(acl_subnet, cidr_mask)
                                if denied_subnet == acl_subnet_plus_mask: # if subnet is equal to the acl subnet entry we enter
                                    print("SUBNET {} ACE Found!!! Do you want to Remove?".format(denied_subnet))
                                    print("ACE Entry to Remove : {}".format(acl_entry))
                                    remove_ace_entry = input("y/n >>> ")
                                    if 'y' in remove_ace_entry.lower():
                                        # connect and remove the ACE entry
                                        commands = ['ip access-list extended OUTSIDE_ACL',
                                                    'no {}'.format(acl_entry_seq_num)]
                                        self.connection.send_config_set(commands)
                                        self.added_removed_aces.append(acl_entry)
            if add_or_remove_acl.lower() == 'add':
                if not self.final_ace_list:
                    if subnets_or_hosts.lower() == 'hosts':
                        print("All {} ACE's Found in ACL - NO Changes to Make".format(subnets_or_hosts))
                        continue
                    elif subnets_or_hosts.lower() == 'subnets':
                        print("All {} ACE's Found in ACL - NO Changes to Make".format(subnets_or_hosts))
                        continue
                # Adding HOSTS/SUBNETS here
                for object in config_parsed.find_objects(r'^Extended'):  # Finding objects beginning with Extended and begin parsing children. there is only one because we were specific on the access-list being displayed
                    for child in object.children:  # beginning loop of each sequence number within extended ACL
                        working_sequence_num = int(re.search(r'^\s+\d+', child.text).group(0)) # assigned to the sequence number in loop 7590 deny ip host 147.135.54.83 any
                        if working_sequence_num != PERMIT_SEQUENCE_NUM:
                            prior_sequence_num = working_sequence_num  # this will track with the working_sequence_num variable so we will be ready to use the prior_sequence_num variable later
                        else:  # if working_sequence_num finally equals PERMIT_SEQUENCE_NUM we have reached the end of the ACL and can find the next seq. number
                            final_sequence_num = prior_sequence_num + SEQUENCE_SKIP  # here we want to take the prior sequence number and add 10. this will give us the next sequence number in the ACL series
                            if final_sequence_num == PERMIT_SEQUENCE_NUM:  # if final_sequence_num is equal to PERMIT_SEQUENCE_NUM we need to increase the PERMIT sequence num because we have reached reached a SEQ which is SEQUENCE_SKIP before PERMIT_SEQUENCE_NUM
                                print("")
                                print("**** ERROR: PERMIT SEQUENCE NUM REACHED on {}. PLEASE INCREASE PERMIT SEQ NUMBER ****".format(node))
                                print("")
                                for output_line in command_output_before:
                                    print(output_line)
                                continue
                            elif subnets_or_hosts == 'hosts':
                                # Add/Remove host entries to ACL Here
                                for host in self.final_ace_list:
                                    commands = ['ip access-list extended OUTSIDE_ACL', '{} deny ip host {} any'.format(final_sequence_num, host)]
                                    self.connection.send_config_set(commands)
                                    final_sequence_num += SEQUENCE_SKIP
                                    self.added_removed_aces.append('{} deny ip host {} any'.format(final_sequence_num, host))
                            elif subnets_or_hosts == 'subnets':
                                if 'host' in child.text.split()[3]:
                                    continue
                                for subnet in self.final_ace_list:

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
                                    self.connection.send_config_set(commands)
                                    final_sequence_num += SEQUENCE_SKIP
                                    self.added_removed_aces.append('{} deny ip {} {} any'.format(final_sequence_num, subnet_and_wildcard_mask.group(1), wildcard_mask))

            # writing config to ASR

            device_write = self.connection.send_command('wr')

            # grabbing post output config and performing DIFF here of command_output before and after

            command_output_after = self.connection.send_command(COMMAND).split('\n')  # sending command to node

            # performing diff on ACL before and after

            self.diff_data(command_output_before, command_output_after, node)

            # sending write output to user

            print("\t========= CHANGE WRITE EVIDENCE {} =========".format(node))
            print("")
            print(device_write)
            print("")
            print("")
            if add_or_remove_acl.lower() == 'add':
                # Tell user which hosts/subnets were added and which were not
                print("=== List of {} which found existing match in ACL so NOT Added to ACL".format(subnets_or_hosts))
                if self.existing_ace_list:
                    for line in self.existing_ace_list:
                        print(line)
                else:
                    print('NONE')
                print("")
            print("=== List of {} which were {} to ACL".format(subnets_or_hosts, add_or_remove_acl))
            if self.added_removed_aces:
                for line in self.added_removed_aces:
                    print(line)
            else:
                print('NONE')
            print("")
            print("")

    def diff_data(self, data_before, data_after, node_name):

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
        print("\t========= CHANGES BELOW {} =========".format(node_name))
        print("")
        print('\n'.join(diff))
        print("")

    def asa_top_50_top_talkers_bytes(self, node_list, config_date, config_time):

        """
        This provides you with the top 50 hosts who have consumed the most data through the ASA
        :param node_list:
        :param config_date:
        :param config_time:
        :return:
        """

        # show conn - save to local file
        # grab output and sort by top 50 hosts
        # cat /tmp/ASA_show_conn_ouput  |awk '{print $9, $1, $3, $5}' |sort -nr | head -50

        self.username = input('Username: ')
        self.password = getpass.getpass('Password: ')
        self.enable_pass = getpass.getpass('Enable Password: ')
        self.initiate_connection(node_list)
        self.connection.enable()
        print("")
        print("")
        print("\t========= {} Top 25 Top-Talkers by Bytes =========".format(node_list))
        print("")
        print("")
        print("\tPreparing Output.......")
        print("")
        filename = ('sh-conn-{}-{}-{}.log'.format(node_list, config_date, config_time))
        host_connections_output = self.connection.send_command_timing('sh conn', delay_factor=4)
        with open('asa_top_talkers_logs/{}'.format(filename), 'w') as file:
            file.write(host_connections_output)

        # outputting the top 50 host connections by byte count on the prod asa

        top_50_talkers = subprocess.check_output(["cat asa_top_talkers_logs/%s | awk '{print $9, $1, $3, $5}' | sort -nr | tail -n +1 | head -25" % filename], shell=True, stderr=subprocess.STDOUT).decode('utf-8').split('\n')

        # iterating over each host and converting bytes to MB

        for host in top_50_talkers:
            try:
                host_traffic_total = convert_size(int(host.split()[0].replace(',', '')))
                host1_connection_output = host.split()[2]
                host2_connection_output = host.split()[3].replace(',', '')
                print("{} {} {}".format(host_traffic_total, host1_connection_output, host2_connection_output))
            except Exception:
                pass
            # If the host has accumulated more than 50MB of data perform nslookup because this is most likely our culprit.

            # if single_host_check:
            #
            #     if host_kbytes_to_mbytes_int >= 1:
            #
            #         trouble_ip = re.search(r'(?<=[U,T][D,C]P\s).*(?=:\d{5})', host_connection_output).group(0)
            #         nslookup_trouble_ip = subprocess.check_output(["nslookup %s" % trouble_ip], shell=True, stderr=subprocess.STDOUT).decode('utf-8')
            #         nslookup_trouble_ip_parse = re.search(r'(?<=Non-authoritative answer:\n).*(?=\n)', nslookup_trouble_ip).group(0)
            #         print("{} MB {}".format(host_kbytes_to_mbytes_str, host_connection_output))
            #         print("")
            #         print("NSLOOKUP on {} = {}".format(trouble_ip, nslookup_trouble_ip_parse))
            #         print("")

            #     else:
            #
            #         print("{} MB {}".format(host_kbytes_to_mbytes_str, host_connection_output))
            #
        print("")
        print("--- removing asa conn logs")
        print("")
        print("")
        subprocess.call(["rm -rvf asa_top_talkers_logs/%s" % filename], shell=True)
        print("")
        print("")

        return

    # def asa_top_50_host_embryonic_conns(node_connect, asa_node, config_date, config_time, single_host_check):
    #
    #     embryonic_host_found = False
    #
    #     host_embryonic_conn_output = node_connect.send_command('show local-host | in host|embryonic').split('\n')
    #     config_parsed = CiscoConfParse(host_embryonic_conn_output, syntax='ios')
    #
    #     for parent in config_parsed.find_objects(r'^local'):  # Finding objects beginning with Extended and begin parsing children. there is only one because we were specific on the access-list being displayed
    #
    #         # Grab Host IP from Object
    #
    #         host_ip = re.search(r'(?<=<).*(?=>)', parent.text).group(0)
    #
    #         for child in parent.children:
    #             # Grab Total Host Embryonic Connections
    #
    #             embryonic_conn_count = int(re.search(r'(?<=\s=\s).*', child.text).group(0))
    #
    #         # perform If statement on embryonic connection count so we only display hosts with more than 100 half open connections
    #
    #         if embryonic_conn_count >= 100:
    #
    #             embryonic_host_found = True
    #
    #             print("Host IP: {} Half-Open Connections: {}".format(host_ip, embryonic_conn_count))
    #
    #             asa_top_50_top_talkers_bytes(node_connect, config_date, config_time, host_ip, single_host_check=host_ip)
    #
    #     if not embryonic_host_found:
    #
    #         print("")
    #         print("\t *** GOOD NEWS NO HOSTS W/OVER 100 HALF-OPEN CONNECTIONS ***")
    #         print("")
    #
    #     return


