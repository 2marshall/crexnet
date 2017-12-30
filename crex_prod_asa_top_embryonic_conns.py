from crexlibs import NodeSetup
from datetime import datetime
import re
from ciscoconfparse import CiscoConfParse


CONFIG_DATE = str(datetime.today().strftime('%m%d%Y'))
CONFIG_TIME = str(datetime.today().strftime('%I%M%S%p'))
NODE_LIST = ['192.168.41.1']
OS_TYPE = 'cisco_asa'


def top_embryonic_conns():
    """
    Performs a "sh conn" on either prod or corp ASA and provides top 50 talkers to user
    :return:
    """

    print("")
    print("\t========= Prod ASA Hosts w/Half Open Connections (SYN Attack) =========")
    print("")

    node_setup = NodeSetup(NODE_LIST, OS_TYPE)

    print("")
    print("")

    for node in node_setup.node_list:

        node_connect = node_setup.initiate_connection(node)
        node_connect.enable()  # entering enable mode

        host_embryonic_conn_output = str(node_connect.send_command('show local-host | in host|embryonic')).split('\n')
        config_parsed = CiscoConfParse(host_embryonic_conn_output, syntax='ios')

        for host in config_parsed.find_objects(r'^local'):  # Finding objects beginning with Extended and begin parsing children. there is only one because we were specific on the access-list being displayed

            # Grab Host IP from Object

            host_ip = re.search(r'(?<=<).*(?=>)', host.text).group(0)

            for child in host.children:

                # Grab Total Host Embryonic Connections

                embryonic_conn_count = int(re.search(r'(?<=\s=\s).*', child.text).group(0))

            # perform If statement on embryonic connection count so we only display hosts with more than 100 half open connections

            if embryonic_conn_count >= 100:

                print("Host IP: {} Half-Open Connections: {}".format(host_ip, embryonic_conn_count))

        print("")
        print("")

