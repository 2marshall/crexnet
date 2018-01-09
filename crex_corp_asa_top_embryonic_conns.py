from crexlibs import *
from datetime import datetime


CONFIG_DATE = str(datetime.today().strftime('%m%d%Y'))
CONFIG_TIME = str(datetime.today().strftime('%I%M%S%p'))
NODE_LIST = ['10.3.1.1']
OS_TYPE = 'cisco_asa'
SINGLE_HOST_CHECK = True


def corp_asa_top_embryonic_conns():
    """
    Performs a "sh conn" on either prod or corp ASA and provides top 50 talkers to user
    :return:
    """

    print("")
    print("\t========= Corp ASA Hosts w/Over 100 Half-Open Connections (SYN Attack) =========")
    print("")

    for node in NODE_LIST:  # iterating through NODE_LIST
        node_obj = Node(node, OS_TYPE, CONFIG_DATE, CONFIG_TIME)  # initiating object Node and passing in variables.
        node_obj.run_function(asa_top_50_host_embryonic_conns, CONFIG_DATE, CONFIG_TIME, SINGLE_HOST_CHECK)  # running run_top_talkers function




