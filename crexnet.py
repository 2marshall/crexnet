#!/bin/python3

import crex_prod_asr_acl_updater
import crex_prod_asa_top_talkers
import crex_corp_asa_top_talkers

print("")
print("")
print("\t\t============== Crexendo Python Network Automation Tasks ==============")
print("")
print("")
print("\t======= General Automation Tasks")
print("")
print("{:<} {:.^35} {:>}".format("\tProd ASR OUTSIDE_ACL Updater", ".", "1"))
print("{:<} {:.^31} {:>}".format("\tProd ASA 50 Top Talkers by Bytes", ".", "2"))
print("{:<} {:.^31} {:>}".format("\tCorp ASA 50 Top Talkers by Bytes", ".", "3"))
print("")
print("")

# If all of these statements are true than repeat while loop. otherwise move on

menu_decision = str()
while menu_decision.lower() == "" and menu_decision.lower() != '1' and menu_decision.lower() != '2' and menu_decision.lower() != '3':
    menu_decision = input("\t>>> ")
print("")

if menu_decision.lower() == '1':

    crex_prod_asr_acl_updater.acl_updater()

elif menu_decision.lower() == '2':

    crex_prod_asa_top_talkers.top_talkers()

elif menu_decision.lower() == '3':

    crex_corp_asa_top_talkers.top_talkers()

