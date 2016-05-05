# -*- coding: utf-8 -*-
"""configs specific to epiphan pearls"""
import sys
import json
import subprocess
import os

source_ca_servername = sys.argv[1]
target_ca_servername = sys.argv[2]
private_key = os.getenv('EPIPHAN_PRIVATE_KEY_FILE')
inventory = os.getenv('EPIPHAN_ANSIBLE_INVENTORY_FILE')
ansible_env_vars = 'ANSIBLE_SCP_IF_SSH=y'

command = \
'%s ansible %s -i %s -u root --private-key=%s -a "/sbin/configdb dump -u"' \
        % (ansible_env_vars,
                source_ca_servername,
                inventory,
                private_key)

output = subprocess.check_output(
        command,
        shell=True,
        stderr=subprocess.STDOUT)

cfg = {}
for c in output.splitlines():
    # skips comments
    if c.find('::') != 0:
        continue

    (r1, r2, key, name, r3, value) = c.split(':', 5)
    if key:
        if not key in cfg:
            cfg[key] = {}

        if name:
            cfg[key][name] = value

#json_config = json.dumps(cfg)
#print json_config

for k,x in cfg.items():
    for n,v in x.items():
#        if k != 'timesync':
#            continue

#        if k != 'system':
#            continue

        command = '%s ansible %s -i %s -u root --private-key=%s -a "/sbin/configdb set %s %s %s"' \
                % (
                        ansible_env_vars,
                        target_ca_servername,
                        inventory,
                        private_key,
                        k, n, v)
        print command
        #output = subprocess.check_output(
        #        command,
        #        shell=True,
        #        stderr=subprocess.STDOUT)
        #print output
        print ''
