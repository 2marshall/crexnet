from crexlibs import NetAutomationTasks

#
# ACL Updater will Update the OUTSIDE_ACL on both LEVEL3 and COX ASR's
#

#
# --- New Features to Add ---
#
# 1. Ability to remove ACL's
# 2.

NODE_LIST = ['192.168.40.10', '192.168.40.11']
OS_TYPE = 'cisco_ios'


def prod_asr_acl_updater():

    """
    Primary Script Being Called by crexnet.py which will add either a host or subnet as the next ACL in the COMMAND
    :return:
    """

    # come up with way to integrate both subnets and hosts on a single line

    # Setting up Connect Handler Object

    net_automate = NetAutomationTasks(OS_TYPE)  # initiating network automation object which provides all needed connection related variable for our devices
    net_automate.ios_acl_updater(NODE_LIST) # running specific ios_acl_updater






