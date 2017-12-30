from crexlibs import *
from datetime import datetime


CONFIG_DATE = str(datetime.today().strftime('%m%d%Y'))
CONFIG_TIME = str(datetime.today().strftime('%I%M%S%p'))
NODE_LIST = ['10.3.1.1']
OS_TYPE = 'cisco_asa'


def corp_asa_top_talkers_bytes():
    """
    Performs a "sh conn" on either prod or corp ASA and provides top 50 talkers to user
    :return:
    """

    print("")
    print("\t========= Prod ASA Top 50 Top-Talkers by Bytes =========")
    print("")

    node_setup = NodeSetup(NODE_LIST, OS_TYPE)

    for node in node_setup.node_list:
        node_connect = node_setup.initiate_connection(node)
        node_connect.enable()  # entering enable mode

        # Running Top Talkers Function from crexlibs library

        asa_top_50_top_talkers_bytes(node_connect, CONFIG_DATE, CONFIG_TIME, node, single_host_check=False)

