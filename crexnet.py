#!/bin/python3

import acl_updater
import top_talkers

print("")
print("")
print("\t\t============== Crexendo Python Network Automation Tasks ==============")
print("")
print("")
print("\t======= General Automation Tasks")
print("")
print("{:<} {:.^35} {:>}".format("\tASR OUTSIDE_ACL Updater", ".", "aclupdater"))
print("{:<} {:.^43} {:>}".format("\tASA Top Talkers", ".", "toptalkers"))
print("")
print("")
menu_decision = ""
while menu_decision.lower() == "" or menu_decision.lower() != 'aclupdater':
    menu_decision = input("\t>>> ")
print("")

if menu_decision.lower() == 'aclupdater':

    acl_updater.acl_updater()

if menu_decision.lower() == 'toptalkers':

    top_talkers.top_talkers()
