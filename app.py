#!/bin/python3.6
import json
import re

from flask import Flask
from flask_assistant import Assistant, tell


app = Flask(__name__)
assist = Assistant(
    app,
    route='/',
    project_id='XXXXXXXXXXX.apps.googleusercontent.com'
)

def _clean_pod(pod):
    """
    Simple regex matching to better ensuring parsing of voice to 
    text values
    """
    r = re.match(r'pod\s*[1,one]', pod)
    if r:
        return 'pod1'

    r = re.match(r'pod\s*[2,two]', pod)
    if r:
        return 'pod2'

@assist.action('add_vlan')
def add_vlan(vlan_name, pod):
    pod = _clean_pod(pod)
    # Grab available vlans
    temp_vlans = []
    with open('next_vlans.json', 'r') as f:
        temp_vlans = json.loads(f.read())

    # Assign next available vlan
    network = temp_vlans.pop(0)
    # Overwrite previous vlan file
    with open('next_vlans.json', 'w') as f:
        f.write(json.dumps(temp_vlans))

    # Determine vlan ID by third octect of subnet plus 100
    vlan_id = str(int(network.split('.')[2])+100)

    # Grab current vlans 
    vlans = {}
    with open('vlans.json','r') as f:
        vlans = json.loads(f.read())

    # Add new vlan to json file
    vlans[pod].append(
        {
            "name": vlan_name,
            "id": vlan_id,
            "network": network
        }
    )
    with open('vlans.json','w') as f:
        f.write(json.dumps(vlans))

    # Send response to Google
    return tell(f'''Ok, your job is being executed.
{vlan_name} is being added to {pod} with V LAN ID {vlan_id}''')

@assist.action('get_vlans')
def available_vlans(pod):
    # Grab available vlans for a pod from local file system
    pod = _clean_pod(pod)
    with open('vlans.json','r') as f:
        vlans = [i['name']+': '+i['id'] for i in json.loads(f.read())[pod]]

    # Send response to Google
    return tell('Available V LANS on {}:\n'.format(pod)+'\n'.join(vlans))

@assist.action('get_networks')
def available_networks(pod):
    # Grab available networks for a pod from local file system
    pod = _clean_pod(pod)
    with open('vlans.json','r') as f:
        networks = [i['name']+': '+i['network'] for i in json.loads(f.read())[pod]]

    # Send response to Google
    return tell('Available networks on {}:\n'.format(pod)+'\n'.join(networks))

@assist.action('get_hosts')
def available_hosts(pod):
    # Grab available hosts for a pod from local file system
    pod = _clean_pod(pod)
    with open('hosts.json','r') as f:
        hosts = json.loads(f.read())[pod]

    # Send response to Google
    return tell('Available hosts:\n'+'\n'.join(hosts))

# Run flask web server
app.run(
    host='0.0.0.0',
    port=80,
    debug=True
)
