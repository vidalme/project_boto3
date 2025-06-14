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

sg_base_name = f'sg_{project}_{env}'
fe_sg_name = f'fe_{sg_base_name}'
be_sg_name = f'be_{sg_base_name}'

fe_ingress_rules = [
    {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'CidrIp': '0.0.0.0/0'}, # SSH from anywhere (for demo, restrict in prod)
    {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'CidrIp': '0.0.0.0/0'}  # HTTP from anywhere
]

be_ingress_rules = [
    {'IpProtocol': 'tcp', 'FromPort': 3306, 'ToPort': 3306} # MySQL port
    # {'IpProtocol': 'tcp', 'FromPort': 3306, 'ToPort': 3306, 'SourceSecurityGroupId': ec2_sg_id} # MySQL port
]

def describe_sg(client:boto3.client, sg_name:str):
    try:
        response = client.describe_security_groups(
            Filters=[
                {'Name': 'tag:project', 'Values': [project ]},
                {'Name': 'tag:Name', 'Values': [ sg_name ]},
            ]
        )
        # print(response['SecurityGroups'])
        return response['SecurityGroups']
    except ClientError as e:
        print(f'Could not describe securitygroup {sg_name} {e}')

def create_sgs(client:boto3.client, vpc_id:str ):

    fe_sec_id:str = ""

    if not describe_sg(client,fe_sg_name):
        try:
            print('Creating frontend security group...')
            fe_response = client.create_security_group(
                Description='Security Group for the frontend of the application',
                GroupName=fe_sg_name,
                VpcId=vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': tagit([ 
                            {'Key': 'Name', 'Value': fe_sg_name},
                            {'Key': 'env', 'Value': env},
                            {'Key': 'level', 'Value': 'frontend'},
                        ])
                    },
                ],
            )

            fe_sec_id = fe_response['GroupId']
            print(f'Security group created for frontend {fe_sec_id}')

            for rule in fe_ingress_rules: fe_authorize_sg_rules(client,rule,fe_sec_id)
             
        except ClientError as e:
            print(f'Could not create securitygroup {fe_sg_name} {e}')

    if not describe_sg(client,be_sg_name):
        try:                      
            print('Creating backend security group...')
            be_response = client.create_security_group(
                Description='Security Group for the backend of the application',
                GroupName=be_sg_name,
                VpcId=vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': tagit([ 
                            {'Key': 'Name', 'Value': be_sg_name},
                            {'Key': 'env', 'Value': env},
                            {'Key': 'level', 'Value': 'backend'},
                        ])
                    },
                ],
            )
            
            be_sec_id = be_response['GroupId']
            print(f'Security group created for backend {be_sec_id}')            

            for rule in be_ingress_rules:
                be_authorize_sg_rules(client,vpc_id,rule,be_sec_id,fe_sec_id)

        except ClientError as e:
            print(f'Could not create securitygroup {be_sg_name} {e}')

    return fe_sec_id
    

def fe_authorize_sg_rules(client:boto3.client,ingress_rules:dict, fe_sec_id:str):
    print('Creating frontend security group rules...')
    try:
        response = client.authorize_security_group_ingress(
            GroupId=fe_sec_id,
            CidrIp=ingress_rules['CidrIp'],
            FromPort=ingress_rules['FromPort'],
            IpProtocol=ingress_rules['IpProtocol'],
            ToPort=ingress_rules['ToPort'],
            TagSpecifications=[
                {
                    'ResourceType': 'security-group-rule',
                    'Tags': tagit([ 
                        {'Key': 'env', 'Value': env},
                    ])
                },
            ],
        )
        print(f'Security group rule for frontend created')
    except ClientError as e:
        print(f'Could not create frontend security group rule {e}') 

def be_authorize_sg_rules(client:boto3.client, vpc_id:str, ingress_rules:dict, be_sec_id:str,fe_sec_id:str):
    print('Creating backend security group rules...')
    try:
        response = client.authorize_security_group_ingress(
            GroupId=be_sec_id,
            TagSpecifications=[
                {
                    'ResourceType': 'security-group-rule',
                    'Tags': tagit([ 
                        {'Key': 'env', 'Value': env},
                    ])
                },
            ],
            IpPermissions=[
                    {
                        'FromPort': ingress_rules['FromPort'],
                        'IpProtocol': ingress_rules['IpProtocol'],
                        'ToPort': ingress_rules['ToPort'],
                        'UserIdGroupPairs': [
                            {
                                'Description': 'HTTP access from other instances',
                                'GroupId': fe_sec_id,
                            },
                        ],
                    },
                ]
        )
        print(f'Security group rule for backend created')
    except ClientError as e:
        print(f'Could not create backend security group rule {e}') 

def destroy_all_sgs(client:boto3.client):
    try:
        response = client.describe_security_groups( Filters=[{ 'Name': 'tag:project','Values': [project] }] )
        for sg in response['SecurityGroups']: 
            try:
                client.delete_security_group(GroupId=sg['GroupId'])
                print(f"Security group {sg['GroupId']} has been deleted successfully")
            except ClientError as e:
                print(f'Could not delete security group {sg['GroupId']}')
    except ClientError as e:
        print(f'Could not delete securitygroup {e}')