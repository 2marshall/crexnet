# crexnet
Crexendo Network Automation Python Scripts

# Required Libraries
import getpass
from netmiko import ConnectHandler
import difflib
import subprocess
import re
from ciscoconfparse import CiscoConfParse

# Install

1. Create directory structure like this
    /scripts
    git clone https://github.com/2marshall/crexnet
    /scripts/crexnet/asa_top_talkers_logs
2. chmod 777 /scripts/crexnet/asa_top_talkers_logs
3. Modify NODE_LIST global variable in each python file below to adjust for your ASA's or ASR's IP

import crex_prod_asr_acl_updater
import crex_prod_asa_top_talkers
import crex_corp_asa_top_talkers
import crex_prod_asa_top_embryonic_conns
import crex_corp_asa_top_embryonic_conns

4. Execute crexnet.py to load menu
