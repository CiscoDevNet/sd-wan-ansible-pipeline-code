#!/usr/bin/env python

import os
import sys
import json
import argparse
import requests
import re


CONFIG_FILES = [
    '.virlrc',
    '~/.virlrc'
]


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--list', action='store_true',
                        help='List host records from NIOS for use in Ansible')

    parser.add_argument('--host',
                        help='List meta data about single host (not used)')

    return parser.parse_args()


def main():
    args = parse_args()
    sim_name = ''
    hostvars = {}
    all_hosts = []
    simulation = ''

    if 'VIRL_HOST' in os.environ:
        host = os.environ['VIRL_HOST']
        username = os.environ['VIRL_USERNAME']
        password = os.environ['VIRL_PASSWORD']
    else:
        for config_file in CONFIG_FILES:
            if config_file[0] == '~':
                config_file = os.path.expanduser(config_file)
            if os.path.exists(config_file):
                break
        else:
            sys.stdout.write('unable to locate .virlrc\n')
            sys.exit(-1)

        envre = re.compile(r'''^([^\s=]+)=(?:[\s"']*)(.+?)(?:[\s"']*)$''')
        result = {}
        with open(config_file) as ins:
            for line in ins:
                match = envre.match(line)
                if line.startswith('#'):
                    continue
                if match is not None:
                    result[match.group(1)] = match.group(2)


        host = result['VIRL_HOST']
        username = result['VIRL_USERNAME']
        password = result['VIRL_PASSWORD']

    inventory = {
        '_meta': {
            'hostvars': hostvars
        },
        'all': {
            'hosts': all_hosts,
            'vars': {
                'virl_host': host,
                'virl_username': username,
                'virl_password': password
            }
        },
        'virl_hosts': {
            'hosts': all_hosts,
            'vars': {
                'virl_host': host,
                'virl_username': username,
                'virl_password': password
            }
        }
    }

    if os.path.exists('.virl/default/id'):
        with open('.virl/default/id') as file:
            simulation = file.read()

    if simulation:
        inventory['all']['vars'].update({'virl_simulation': simulation})

        url = "http://%s:19399/simengine/rest/interfaces/%s" % (host, simulation)

        # perform REST operation
        simulations = requests.get(url, auth=(username,password))
        if simulations.status_code == 200:

            interfaces = simulations.json()[simulation]

            for key, value in interfaces.items():
                if 'management' in value and 'ip-address' in value['management']:
                    if value['management']['ip-address']:
                        management_address = value['management']['ip-address'].split('/')[0]
                        all_hosts.append(key)
                        hostvars[key] = {'ansible_host': management_address}

        # else:
        #     print >> sys.stderr, "http error (%s): %s" % (simulations.status_code, simulations.text)

    sys.stdout.write(json.dumps(inventory, indent=4))
    sys.exit(0)


if __name__ == '__main__':
    main()
