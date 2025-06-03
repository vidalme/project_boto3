import os
import sys

import boto3
from botocore.exceptions import ClientError 

from utils.tagger import tagit
from utils.region_azs import list_available_zones_names

from dotenv import load_dotenv
load_dotenv()

project = os.getenv('PROJECT')
env = os.getenv('ENV')

subnets_name = "subnets_"+project+"_"+env

# def list_available_zones():

def create_subnets(client:boto3.client, vpc_id:str):
    # , cidr_block:str, az:str

    # subnets_list = client.describe_subnets(
    #     Filters=[
    #         {
    #             'Name':'qqum',
    #             'Value':[
    #                 'string'
    #             ]
    #         }
    #     ],
    #     SubnetIds=['string']
    # )

    print(list_available_zones_names(client))

    try:
        create_subnet_response = client.create_subnet(
            TagSpecifications=tagit([
                {
                    'ResourceType': 'subnet',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': subnets_name
                        },
                        {
                            'Key': 'env',
                            'Value': env
                        },
                    ]
                },
            ]),
            VpcId=vpc_id,
            # CidrBlock=cidr_block,
            # AvailabilityZone=az,
            # AvailabilityZoneId=az_id,
        )

    except Exception as e:
        print(f'Could not create Subnet: {e}')
    