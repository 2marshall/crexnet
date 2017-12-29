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
print("{:<} {:.^43} {:>}".format("\tProd ASA 50 Top Talkers by Bytes", ".", "2"))
print("")
print("")
menu_decision = ""
while menu_decision.lower() == "" or menu_decision.lower() != '1' or menu_decision.lower() != '2':
    menu_decision = input("\t>>> ")
print("")

if menu_decision.lower() == '1':

    crex_prod_asr_acl_updater.acl_updater()

if menu_decision.lower() == '2':

    crex_prod_asa_top_talkers.top_talkers()
