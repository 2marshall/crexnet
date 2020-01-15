from crexlibs import NetAutomationTasks
from datetime import datetime


CONFIG_DATE = str(datetime.today().strftime('%m%d%Y'))
CONFIG_TIME = str(datetime.today().strftime('%I%M%S%p'))
NODE_LIST = '192.168.41.1'
OS_TYPE = 'cisco_asa'
SINGLE_HOST_CHECK = True


def asa_top_talkers_bytes():
    """
    Performs a "sh conn" on either prod or corp ASA and provides top 50 talkers to user
    :return:
    """

    print("")
    print("\t========= ASA Top 25 Top-Talkers by Bytes =========")
    print("")

    # Setting up Connect Handler Object

    net_automate = NetAutomationTasks(OS_TYPE)  # initiating network automation object which provides all needed connection related variable for our devices
    net_automate.asa_top_50_top_talkers_bytes(NODE_LIST, CONFIG_DATE, CONFIG_TIME)  # running specific ios_acl_updater



