from ciscoconfparse import CiscoConfParse
import re
import getpass
from netmiko import ConnectHandler
# from easysnmp import Session
import difflib
import sys


def top_talkers():
    """
    Performs a "sh conn" on either prod or corp ASA and provides top 50 talkers to user
    :return:
    """

    # cat /tmp/ASA_show_conn_ouput  |awk '{print $9, $1, $3, $5}' |sort -nr | head -50

    pass