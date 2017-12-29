#!/bin/python3

import crex_prod_asr_acl_updater
import crex_prod_asa_top_talkers

print("")
print("")
print("\t\t============== Crexendo Python Network Automation Tasks ==============")
print("")
print("")
print("\t======= General Automation Tasks")
print("")
print("{:<} {:.^35} {:>}".format("\tProd ASR OUTSIDE_ACL Updater", ".", "1"))
print("{:<} {:.^31} {:>}".format("\tProd ASA 50 Top Talkers by Bytes", ".", "2"))
print("")
print("")

# If all of these statements are true than repeat while loop. otherwise move on

menu_decision = str()
while menu_decision.lower() == "" and menu_decision.lower() != '1' and menu_decision.lower() != '2':
    menu_decision = input("\t>>> ")
print("")

if menu_decision.lower() == '1':

    crex_prod_asr_acl_updater.acl_updater()

if menu_decision.lower() == '2':

    crex_prod_asa_top_talkers.top_talkers()
