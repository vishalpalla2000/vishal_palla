import os
import django
import json
from datetime import datetime
from pysnmp.hlapi import *

import os
import sys

# Add your Django project's root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))  # Get the directory where the script is located
project_path = os.path.dirname(project_root)  # Get the Django project's root directory
sys.path.append(project_path)

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "networking.settings")
django.setup()

from ups.models import SNMP, History


def get_snmp_data(ip, community, oid_pairs):
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


if __name__ == "__main__":
    results = {}

    # Read data from the JSON configuration file
    config_file_path = "config.json"
    with open(config_file_path, "r") as file:
        config_data = json.load(file)

    for device_config in config_data:
        device_ip = device_config["ip"]
        community_string = device_config["community"]
        oid_pairs = device_config["oid_pairs"]

        snmp_data = get_snmp_data(device_ip, community_string, oid_pairs)
        if device_ip not in results:
            results[device_ip] = []
        results[device_ip].append(snmp_data)

        snmp_instance, created = SNMP.objects.update_or_create(
            ip_address=device_ip,
            defaults={
                "model": snmp_data.get("Model", ""),
                "ups_type": snmp_data.get("UPS_Type", ""),
                "battery_capacity": int(snmp_data.get("Battery_capacity", 0)),
                "battery_temperature": int(snmp_data.get("Battery_temperature", 0)),
                "battery_runtime_remain": int(snmp_data.get("Battery_runtime_remain", 0)),
                "battery_replace": bool(int(snmp_data.get("Battery_replace", 0))),
                "battery_type": snmp_data.get("Battery_type", ""),
                "timestamp": datetime.now(),
            }
        )
    history_instance = History()
    history_instance.save_snmp_data(snmp_instance)
    json_results = json.dumps(results, indent=4)
    print(json_results)
