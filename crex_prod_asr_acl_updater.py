from crexlibs import *
from datetime import datetime

#
# ACL Updater will Update the OUTSIDE_ACL on both LEVEL3 and COX ASR's
#

#
# --- New Features to Add ---
#
# 1. Ability to remove ACL's
# 2.

CONFIG_DATE = str(datetime.today().strftime('%m%d%Y'))
CONFIG_TIME = str(datetime.today().strftime('%I%M%S%p'))
NODE_LIST = ['192.168.40.10', '192.168.40.11']
OS_TYPE = 'cisco_ios'
SINGLE_HOST_CHECK = True


def prod_asr_acl_updater():

    """
    Primary Script Being Called by crexnet.py which will add either a host or subnet as the next ACL in the COMMAND
    :return:
    """

    # come up with way to integrate both subnets and hosts on a single line

    # Setting up Connect Handler Object

    node_obj = Node(OS_TYPE, CONFIG_DATE, CONFIG_TIME)  # initiating object Node and passing in variables.

    for node in NODE_LIST:  # iterating through NODE_LIST
        node_obj.run_function(ios_acl_updater, node, CONFIG_DATE, CONFIG_TIME, SINGLE_HOST_CHECK)  # running function within crexlibs library






