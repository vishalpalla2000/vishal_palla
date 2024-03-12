from pysnmp.hlapi import *
import json

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


if __name__ == "__main__":
    results = {}  # Dictionary to store results for each IP

    # Read data from the JSON configuration file
    with open("config.json", "r") as file:
        config_data = json.load(file)

    for device_config in config_data:
        device_ip = device_config["ip"]
        community_string = device_config["community"]
        oid_pairs = device_config["oid_pairs"]

        snmp_data = get_snmp_data(device_ip, community_string, oid_pairs)
        if device_ip not in results:
            results[device_ip] = []  # Initialize an empty list for this IP if it doesn't exist
        results[device_ip].append(snmp_data)  # Append the SNMP data to the list

    json_results = json.dumps(results, indent=4)
    print(json_results)
