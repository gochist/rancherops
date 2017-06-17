#!/usr/bin/env python
"""

"""

import argparse
import subprocess
import json

VALID_GROUPS = ["rancher-db", "rancher-server", "configure-mgt"]
LOCAL_HOSTVARS = {"ansible_connection": "local",
                  "ansible_become": "true",
                  "ansible_python_interpreter": "/usr/bin/python3"}
HOSTS_HEADER = """\
## This file is automatically generate by ansible playbook. Do not edit this manually.
127.0.0.1 localhost

"""


def get_list():
    def validates_server_groups(tags):
        server_groups = tags.get("ansible_server_groups").split(',')
        for group in server_groups:
            if group in VALID_GROUPS:
                return True
        return False

    ret = subprocess.check_output(["triton", "ls", "--json"])
    instances = list()
    for line in ret.splitlines():
        instance = json.loads(line)
        tags = instance.get("tags")
        state = instance.get("state")
        managed = tags.get("rancherops_managed")

        if managed and state == "running" and validates_server_groups(tags):
            instances.append(instance)

    return instances


def get_host(hostname):
    ret = subprocess.check_output(["triton", "inst", "get", "--json", hostname])
    instance = json.loads(ret)
    return instance


def parse_host(instance):
    host = dict()
    primary_ip, internal_ip, ips = get_ips(instance)
    host["ansible_host"] = primary_ip
    host["ansible_host_primary_ip"] = primary_ip
    host["ansible_host_internal_ip"] = internal_ip
    host["ansible_host_ips"] = ips
    host["ansible_python_interpreter"] = "/usr/bin/python3"
    host["ansible_user"] = "ubuntu"
    host["ansible_become"] = "true"

    tags = instance.get("tags")

    for tag, value in tags.iteritems():
        if tag.startswith("ansible"):
            host[tag] = value

    return host


def get_ips(instance):
    primary_ip = instance.get("primaryIp")
    ips = instance.get("ips")
    internal_ip = [ip for ip in ips if ip != primary_ip][0]
    return primary_ip, internal_ip, ips


def convert_to_inventory(instances):
    inventory = dict()
    hostvars = dict()
    hosts = dict()
    for inst in instances:
        tags = inst.get("tags")
        ansible_host = inst.get("name")
        ansible_server_groups = tags.get("ansible_server_groups", "").split(',')
        ansible_host_names = tags.get("ansible_host_names", "").split(',')
        primary_ip, internal_ip, ips = get_ips(inst)

        for sg in ansible_server_groups:
            # add inventory
            if inventory.has_key(sg):
                inventory[sg].append(ansible_host)
            else:
                inventory[sg] = [ansible_host, ]

            # add hostvars
            hostvars[ansible_host] = parse_host(inst)

            # add hosts
            ansible_host_names.append(ansible_host)
            public_hosts = sorted([host for host in ansible_host_names if host])
            internal_hosts = ["%s.internal" % host for host in public_hosts]
            if hosts.has_key(primary_ip):
                hosts[primary_ip] += public_hosts
            else:
                hosts[primary_ip] = public_hosts

            if hosts.has_key(internal_ip):
                hosts[internal_ip] += internal_hosts
            else:
                hosts[internal_ip] = internal_hosts

    # deduplicate host in hosts
    hosts_list = []
    for k, v in sorted(hosts.iteritems()):
        hosts_list.append("%s %s" % (k, " ".join(list(set(v)))))
    hosts_contents = HOSTS_HEADER + "\n".join(hosts_list)

    # deduplicate host in host_group
    for k, v in inventory.iteritems():
        inventory[k] = list(set(v))

    # add configure-mgt
    if "configure-mgt" not in inventory:
        inventory["configure-mgt"] = ["localhost"]
        hostvars["localhost"] = LOCAL_HOSTVARS

    # make rancher-mgt group as a parent group of the others
    inventory["rancher-mgt"] = {"children": [k for k in inventory.keys() if k != "configure-mgt"],
                               "vars": {"inventory_hosts_contents": hosts_contents}}

    # add hostvars
    inventory["_meta"] = {"hostvars": hostvars}

    return inventory


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate ansible inventory from triton-cli")
    parser.add_argument('--list', action="store_true", help='list inventory')
    parser.add_argument('--host', type=str, help='get host')
    args = parser.parse_args()

    if args.list:
        instances = get_list()
        inventory = convert_to_inventory(instances)
        print(json.dumps(inventory))

    elif args.host:
        if args.host == "localhost":
            var = LOCAL_HOSTVARS
        else:
            var = parse_host(get_host(args.host))

        print(json.dumps(var))
