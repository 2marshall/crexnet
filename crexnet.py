#!/bin/python3

import crex_prod_asr_acl_updater
import crex_asa_top_talkers

print("")
print("")
print("\t\t============== Crexendo Python Network Automation Tasks ==============")
print("")
print("")
print("{:<} {:.^45} {:>}".format("\tProd ASR OUTSIDE_ACL Updater", ".", "1"))
print("")
print("")
# print("{:<} {:.^41} {:>}".format("\tProd ASA 50 Top Talkers by Bytes", ".", "2"))
# print("{:<} {:.^13} {:>}".format("\tProd ASA Hosts w/Over 100 Half-Open Connections (SYN Attack)", ".", "3"))
# print("")
# print("\t======= Corporate Automation Tasks")
# print("")
print("{:<} {:.^41} {:>}".format("\tASA 50 Top Talkers by Bytes", ".", "2"))
# print("{:<} {:.^13} {:>}".format("\tCorp ASA Hosts w/Over 100 Half-Open Connections (SYN Attack)", ".", "5"))
# print("")

# If all of these statements are true than repeat while loop. otherwise move on

menu_decision = str()
while menu_decision.lower() == "" and menu_decision.lower() != '1' and menu_decision.lower() != '2' and menu_decision.lower() != '3' and menu_decision.lower() != '4' and menu_decision.lower() != '5':
    menu_decision = input("\t>>> ")
print("")

if menu_decision.lower() == '1':

    crex_prod_asr_acl_updater.prod_asr_acl_updater()

# elif menu_decision.lower() == '2':
#
#     crex_prod_asa_top_talkers.prod_asa_top_talkers_bytes()
#
# elif menu_decision.lower() == '3':
#
#     crex_prod_asa_top_embryonic_conns.prod_asa_top_embryonic_conns()

elif menu_decision.lower() == '2':

    crex_asa_top_talkers.asa_top_talkers_bytes()

# elif menu_decision.lower() == '5':
#
#     crex_corp_asa_top_embryonic_conns.corp_asa_top_embryonic_conns()


