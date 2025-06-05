import os
import sys
import random

import boto3
from botocore.exceptions import ClientError 

from utils.tagger import tagit
from utils.region_azs import list_available_zones_names

from dotenv import load_dotenv
load_dotenv()

project = os.getenv('PROJECT')
env = os.getenv('ENV')

subnet_base_name = "subnets_"+project+"_"+env

subnets_cidr = ['10.0.1.0/24','10.0.2.0/24','10.0.3.0/24','10.0.4.0/24'] 

def create_subnets(client:boto3.client, vpc_id:str):
    
    subnets_describe_response = client.describe_subnets(
        Filters=[
            {
                'Name': 'tag:project',
                'Values': [
                    project,
                ]
            },
        ],
    )

    if len(subnets_describe_response['Subnets'])!=0:
        subnets_names = []
        for sn in subnets_describe_response['Subnets']:
            for tag in sn['Tags']:
                if tag['Key'] == 'Name': 
                    subnets_names.append(tag['Value'])
        print(f'Subnets already exist') 
        return subnets_names

    try:
        subnets_names=[]
        az_list = list_available_zones_names(client)
        print('Creating subnets...')
        for i in range(4):
            subnet_name = f"{subnet_base_name}_{i}"
            subnets_names.append(subnet_name)
            create_subnet_response = client.create_subnet(
                TagSpecifications=[
                    {
                        'ResourceType': 'subnet',
                        'Tags': tagit(
                            [
                                {
                                    'Key': 'Name',
                                    'Value': subnet_name
                                },
                                {
                                    'Key': 'env',
                                    'Value': env
                                },
                            ]
                        )
                    },
                ],
                VpcId=vpc_id,
                CidrBlock=subnets_cidr[i],
                AvailabilityZone=az_list[i],
            )
            print(f"Subnet created: {create_subnet_response['Subnet']['Tags'][-1]['Value']}")
        print(f'Subnets are available')    
        return subnets_names

    except ClientError as e:
        print(f'Could not create Subnet: {e}')
    
# Destroys all subnets with the project name Tag associated
def destroy_all_subnets(client:boto3.client):

    response = client.describe_subnets(
        Filters=[
            {
                'Name': 'tag:project',
                'Values': [
                    project,
                ]
            },
        ],
    )
    for i in response['Subnets']:
        response = client.delete_subnet(
            SubnetId=i['SubnetId'],
        )
        print(f"Subnet {i['SubnetId']} has been deleted successfully")