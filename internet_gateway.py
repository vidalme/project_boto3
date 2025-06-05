import sys
import os
from dotenv import load_dotenv

import boto3
from botocore.exceptions import ClientError

from utils.tagger import tagit

load_dotenv()
project = os.getenv('PROJECT')
env = os.getenv('ENV')

igw_name = "igw_"+project+"_"+env

filters = [{'Name': 'tag:project', 'Values': [project]}]

def create_internet_gateway(client:boto3.client, vpc_id:str)->str:

    response_describe = client.describe_internet_gateways(
        Filters=filters
    )
    if response_describe['InternetGateways']:
        igw_id = response_describe['InternetGateways'][0]['InternetGatewayId']
        print(f'Internet Gateway {igw_id} already exists')
        return igw_id 

    try:
        print('Creating Internet Gateway...')
        response = client.create_internet_gateway(
            TagSpecifications=[
                {
                    'ResourceType': 'internet-gateway',
                    'Tags': tagit([
                        {
                            'Key': 'Name',
                            'Value': igw_name
                        },
                        {
                            'Key': 'env',
                            'Value': 'env'
                        },
                    ])
                },
            ],
        )
        igw_id = response['InternetGateway']['InternetGatewayId']
        print(f"Internet Gateway created: {igw_id}")
        
        attach = client.attach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
        )
        print(f"Internet Gateway {igw_id} attached to VPC {vpc_id}")
        return igw_id
    
    except ClientError as e:
        print(f'Could not create interenet gateway: {e}')

def destroy_internet_gateway(client:boto3.client):
    
    
    r_describe_igw = client.describe_internet_gateways(
        Filters=filters
    )
    if len(r_describe_igw['InternetGateways'])>0:
        
        igw_id = r_describe_igw['InternetGateways'][0]['InternetGatewayId']

        r_describe_vpcs = client.describe_vpcs(
            Filters=filters
        )
        vpc_id = r_describe_vpcs['Vpcs'][0]['VpcId']
        
        r_detach = client.detach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
        )
        print(f'Internet Gateway {igw_id} has been detached from VPC {vpc_id}.')

        r_destroy = client.delete_internet_gateway(
                InternetGatewayId=igw_id
        )
        print(f'Internet Gateway {igw_id} has been deleted successfully.')