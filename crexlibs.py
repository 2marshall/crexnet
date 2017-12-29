import getpass
from netmiko import ConnectHandler
import difflib


class NodeSetup(object):

    """
    User must provide node_list list() and os_type str() when instantiating this object
    :param node_list - a list of IP's ['192.168.40.11', '192.168.40.10']
    :param os_type - a string matching the Netmiko OS type. Here are choices.  juniper, cisco_ios, cisco_asa, cisco_xe
    """

    def __init__(self, node_list, os_type):

        self.username = input('Username: ')
        self.password = getpass.getpass('Password: ')
        self.enable_pass = getpass.getpass('Enable Password: ')
        self.node_list = node_list
        self.os_type = os_type

    def initiate_connection(self, node):

        print(self.os_type)

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

        node_connection = ConnectHandler(**node_data)

        return node_connection


def diff_data(data_before, data_after, node):

    """ checks pre and post files and builds diff results file. data_before and data_after need to be lists
    :return:
    """

    diff_library = difflib.Differ()
    diff = diff_library.compare(data_before, data_after)    # data_before and data_after must be lists

    print("")
    print("\t========= CHANGES BELOW {} =========".format(node))
    print("")
    print('\n'.join(diff))
    print("")

