import requests, json, time
import meraki
import re
import ast
import ipaddress
import random
import string
import sys

# Author: Mithchell Gulledge

# class that contains all Meraki necessary config
class MerakiConfig:
    api_key = ''
    org_name = ''
    tag_prefix = ''
    org_id = None
    # enter amount of additional tunnels to add
    print("enter amount of additional tunnels to add")
    tunnel_addition_amount = input()

# placeholder variable for public IP in VPN config
meraki_vpn_config_public_ip = '169.254.169.1'

# creating authentication variable for the Meraki SDK
meraki_dashboard_sdk_auth = meraki.DashboardAPI(MerakiConfig.api_key)

# writing function to obtain org ID via linking ORG name
result_org_id = meraki_dashboard_sdk_auth.organizations.getOrganizations()
for org in result_org_id:
    if org['name'] == MerakiConfig.org_name:
        MerakiConfig.org_id = org['id']

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

# creating function to generate random string 
def get_random_string(length):
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return(result_str)

# this function performs initial get to obtain all Meraki existing VPN info 
# more information can be found in devnet under the following link:
# https://developer.cisco.com/meraki/api-v1/#!get-organization-appliance-vpn-third-party-vpn-peers
def get_meraki_ipsec_tunnels():

    originalvpn = meraki_dashboard_sdk_auth.appliance.getOrganizationApplianceVpnThirdPartyVPNPeers(
        MerakiConfig.org_id
        )  

    # indexing the peers list in the response so we get a clean list of Meraki VPN peers
    return originalvpn['peers']  

# function to update Meraki VPN config
def update_meraki_vpn(vpn_list):

    updatemvpn = meraki_dashboard_sdk_auth.appliance.updateOrganizationApplianceVpnThirdPartyVPNPeers(
    MerakiConfig.org_id, vpn_list
    ) 

# executing function to  obtain the original list of Meraki VPN peers
original_list_of_meraki_tunnels = get_meraki_ipsec_tunnels()

# placeholder variable for tunnel name in VPN config
vpn_tunnel_name = ''

# performing loop (80 times for now, just guessing)
for vpn_config_count in range(int(MerakiConfig.tunnel_addition_amount)):
    # incrementing last bit of IP address by 1
    public_ip = ipaddress.ip_address(meraki_vpn_config_public_ip) + 1
    # calling function to generate random string
    vpn_tunnel_name = get_random_string(8)
    # calling function to create template vpn tunnel config 
    primary_vpn_tunnel_template = get_meraki_ipsec_config(vpn_tunnel_name, \
            str(meraki_vpn_config_public_ip))
    # appending primary_vpn_tunnel_template to original vpn tunnel list
    original_list_of_meraki_tunnels.append(primary_vpn_tunnel_template)

print(original_list_of_meraki_tunnels)

# calling function to update Meraki VPNs
update_meraki_vpn(original_list_of_meraki_tunnels)
