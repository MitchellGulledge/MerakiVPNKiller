import requests, json, time
import meraki
import re
import ast
import ipaddress
import random
import string

# Author: Mithchell Gulledge

# class that contains all Meraki necessary config
class MerakiConfig:
    api_key = ''
    org_name = ''
    org_id = None

# writing function to obtain org ID via linking ORG name
mdashboard = meraki.DashboardAPI(MerakiConfig.api_key)
result_org_id = mdashboard.organizations.getOrganizations()
for x in result_org_id:
    if x['name'] == MerakiConfig.org_name:
        MerakiConfig.org_id = x['id']

# defining function that creates dictionary of IPsec config from dummy variables in loop
def get_meraki_ipsec_config(name, public_ip) -> dict:
    ipsec_config = {
        "name": name,
        "publicIp": public_ip,
        "privateSubnets": ["0.0.0.0/0"],
        "secret": "secret",
        "ikeVersion": "2",
        "ipsecPolicies": {
            "ikeCipherAlgo": ["aes256"],
            "ikeAuthAlgo": ["sha256"],
            "ikeDiffieHellmanGroup": ["group14"],
            "ikeLifetime": 28800,
            "childCipherAlgo": ["aes256"],
            "childAuthAlgo": ["sha256"],
            "childPfsGroup": ["group14"],
            "childLifetime": 3600
        },
    }
    return ipsec_config

# random string 
def get_random_string(length):
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return(result_str)

# function to update Meraki VPN config
def update_meraki_vpn(vpn_list):
    updatemvpn = mdashboard.organizations.updateOrganizationThirdPartyVPNPeers(
    MerakiConfig.org_id, vpn_list
    )

# this function performs initial get to obtain all Meraki existing VPN info 
def get_meraki_ipsec_tunnels():
    originalvpn = mdashboard.organizations.getOrganizationThirdPartyVPNPeers(
        MerakiConfig.org_id
        )  
    return originalvpn     

# variable with new and existing s2s VPN config for Meraki
merakivpns = []

# performing initial get to obtain all Meraki existing VPN info 
original_meraki_tunnels = get_meraki_ipsec_tunnels()
print(original_meraki_tunnels)

# placeholder variable for public IP in VPN config
public_ip = '169.254.169.1'

# placeholder variable for tunnel name in VPN config
vpn_tunnel_name = ''

# performing loop (80 times for now, just guessing)
for vpn_config_count in range(80):
    # incrementing last bit of IP address by 1
    public_ip = ipaddress.ip_address(public_ip) + 1
    # calling function to generate random string
    vpn_tunnel_name = get_random_string(8)
    # calling function to create template vpn tunnel config 
    primary_vpn_tunnel_template = get_meraki_ipsec_config(vpn_tunnel_name, \
            str(public_ip))
    # appending primary_vpn_tunnel_template to original vpn tunnel list
    merakivpns.append(primary_vpn_tunnel_template)

print(merakivpns)

# calling function to update Meraki VPNs
update_meraki_vpn(merakivpns)
