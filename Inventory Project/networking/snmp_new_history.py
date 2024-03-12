import os
import django
from pysnmp.hlapi import *
import json
from datetime import datetime
#from ups.models import SNMP, History

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "networking.settings")
django.setup()
from ups.models import SNMP, History

def get_snmp_data(ip, community, oid_pairs):
    """
    Fetch SNMP data from the device for a list of OID pairs (description and OID).

    :param ip: IP address of the device
    :param community: SNMP community string
    :param oid_pairs: List of OID pairs (description and OID) to fetch
    :return: A dictionary of fetched data with descriptions as keys
    """
    data = {}
    for oid_pair in oid_pairs:
        oid_description = oid_pair["description"]
        oid_value = oid_pair["oid"]

        iterator = getCmd(SnmpEngine(),
                          CommunityData(community),
                          UdpTransportTarget((ip, 161)),
                          ContextData(),
                          ObjectType(ObjectIdentity(oid_value)))

        error_indication, error_status, error_index, var_binds = next(iterator)

        if error_indication:
            print(error_indication)
        elif error_status:
            print('%s at %s' % (error_status.prettyPrint(), error_index and var_binds[int(error_index) - 1][0] or '?'))
        else:
            for var_bind in var_binds:
                data[oid_description] = str(var_bind[1])
    return data

def save_snmp_data_to_db(ip, snmp_data):
    SNMP.objects.update_or_create(
        ip_address=ip,
        defaults={
            "model": snmp_data["Model"],
            "ups_type": snmp_data["UPS_Type"],
            "battery_capacity": int(snmp_data["Battery_capacity"]),
            "battery_temperature": int(snmp_data["Battery_temperature"]),
            "battery_runtime_remain": int(snmp_data["Battery_runtime_remain"]),
            "battery_replace": bool(int(snmp_data["Battery_replace"])),
            "battery_type": snmp_data["Battery_replace"],
            "timestamp": datetime.now(),
            "room_temperature": int(snmp_data["Battery_temperature"])
        }
    )

def save_snmp_data_to_history(ip, snmp_data):
    snmp_instance = SNMP.objects.get(ip_address=ip)
    History.objects.create(
        snmp=snmp_instance,
        timestamp=datetime.now(),
        model=snmp_data["Model"],
        ups_type=snmp_data["UPS_Type"],
        battery_capacity=int(snmp_data["Battery_capacity"]),
        battery_temperature=int(snmp_data["Battery_temperature"]),
        battery_runtime_remain=int(snmp_data["Battery_runtime_remain"]),
        battery_replace=bool(int(snmp_data["Battery_replace"])),
        battery_type=snmp_data["Battery_replace"],
    )

if __name__ == "__main__":
    results = {}  # Dictionary to store results for each IP

    # Read data from the JSON configuration file
    with open("config.json", "r") as file:
        config_data = json.load(file)

    for device_config in config_data:
        device_ip = device_config["ip"]
        community_string = device_config["community"]
        oid_pairs = device_config["oid_pairs"]

        # Fetch SNMP data
        snmp_data = get_snmp_data(device_ip, community_string, oid_pairs)
        results[device_ip] = snmp_data  # Store the SNMP data in the results dictionary

        # Save SNMP data to the database
        save_snmp_data_to_db(device_ip, snmp_data)

        # Save SNMP data to the History table
        save_snmp_data_to_history(device_ip, snmp_data)

    json_results = json.dumps(results, indent=4)
    print(json_results)