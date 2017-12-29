from crexlibs import NodeSetup
from datetime import datetime
import os
import re


CONFIG_DATE = str(datetime.today().strftime('%m%d%Y'))
CONFIG_TIME = str(datetime.today().strftime('%I%M%S%p'))
NODE_LIST = ['192.168.41.1']
OS_TYPE = 'cisco_asa'


def top_talkers():
    """
    Performs a "sh conn" on either prod or corp ASA and provides top 50 talkers to user
    :return:
    """

    # show conn - save to local file
    # grab output and sort by top 50 hosts
    # cat /tmp/ASA_show_conn_ouput  |awk '{print $9, $1, $3, $5}' |sort -nr | head -50

    print("")
    print("\t========= Prod ASA 50 Top Talkers by Bytes =========")
    print("")

    node_setup = NodeSetup(NODE_LIST, OS_TYPE)

    print("")
    print("\tPreparing Output.......")
    print("")
    print("")

    for node in node_setup.node_list:

        node_connect = node_setup.initiate_connection(node)
        node_connect.enable()  # entering enable mode
        host_connection_count = re.search(r'^\d+', node_connect.send_command('sh conn count')).group(0)
        print("Total Active Connections: {}".format(host_connection_count))
        print("")
        filename = ('sh-conn-{}-{}-{}.log'.format(node, CONFIG_DATE, CONFIG_TIME))
        host_connections_output = node_connect.send_command('sh conn')
        with open('asa_top_talkers_logs/{]'.format(filename), 'w') as file:
            file.write(host_connections_output)

        # outputting the top 50 host connections by byte count on the prod asa

        os.system("cat asa_top_talkers_logs/{} | awk '{print $9, $1, $3, $5}' | sort -nr | head -50".format(filename))

        print("")
        print("")

