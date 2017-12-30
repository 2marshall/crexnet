from crexlibs import *
from datetime import datetime


CONFIG_DATE = str(datetime.today().strftime('%m%d%Y'))
CONFIG_TIME = str(datetime.today().strftime('%I%M%S%p'))
NODE_LIST = ['192.168.41.1']
OS_TYPE = 'cisco_asa'


def prod_asa_top_embryonic_conns():
    """
    Performs a "sh conn" on either prod or corp ASA and provides top 50 talkers to user
    :return:
    """

    print("")
    print("\t========= Prod ASA Hosts w/Over 100 Half-Open Connections (SYN Attack) =========")
    print("")

    node_setup = NodeSetup(NODE_LIST, OS_TYPE)

    print("")
    print("")

    for node in node_setup.node_list:

        node_connect = node_setup.initiate_connection(node)
        node_connect.enable()  # entering enable mode

        asa_top_50_host_embryonic_conns(node_connect, CONFIG_DATE, CONFIG_TIME)




