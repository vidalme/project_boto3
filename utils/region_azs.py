import boto3

def list_available_zones(client:boto3.client)->list:
    az_list=[]
    for az in client.describe_availability_zones()['AvailabilityZones']:
        # print(az['RegionName'])
        # print(az['ZoneName'])
        # print("------------------")
        az_list.append(az)
    return az_list

def list_available_zones_names(client:boto3.client)->list:
    az_list_names = []
    for az in list_available_zones(client):
        az_list_names.append(az['ZoneName'])
    return az_list_names