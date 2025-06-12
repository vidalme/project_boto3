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
    {'IpProtocol': 'tcp', 'FromPort': 3306, 'ToPort': 3306, 'SourceSecurityGroupId': 'dummy'} # MySQL port
    # {'IpProtocol': 'tcp', 'FromPort': 3306, 'ToPort': 3306, 'SourceSecurityGroupId': ec2_sg_id} # MySQL port
]

def describe_sg(client:boto3.client, sg_name:str):
    try:
        response = client.describe_security_groups(
            Filters=[
                {'Name': 'tag:project', 'Values': [project,]},
                {'Name': 'tag:Name', 'Values': [ sg_name,]},
            ]
        )
        # print(response['SecurityGroups'])
        return response['SecurityGroups']
    except ClientError as e:
        print(f'Could not create securitygroup {sg_name} {e}')

def create_sgs(client:boto3.client, vpc_id:str):
    create_sg(client,vpc_id,fe_sg_name, 'fe') if not describe_sg(client,fe_sg_name) else print(f'SecurityGroup {fe_sg_name} already exist')
    create_sg(client,vpc_id,be_sg_name, 'be') if not describe_sg(client,be_sg_name) else print(f'SecurityGroup {be_sg_name} already exist')

def create_sg(client:boto3.client, vpc_id:str, sg_name:str, ms:str):
    try:
        print('Creating security group...')
        response = client.create_security_group(
            Description='Security Group for the frontend of the application',
            GroupName=sg_name,
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'security-group',
                    'Tags': tagit([ 
                        {'Key': 'Name', 'Value': sg_name},
                        {'Key': 'env', 'Value': env},
                    ])
                },
            ],
        )
        print('Security group created')

        if ms.lower() == 'fe':
            fe_rule_name = sg_name+'_rule'
            fe_authorize_sg_rules(client,fe_rule_name,fe_ingress_rules,'fe')
        if ms.lower() == 'be':
            be_rule_name = sg_name+'_rule'
            be_authorize_sg_rules(client,fe_rule_name,be_ingress_rules,'be')
            
    except ClientError as e:
        print(f'Could not create securitygroup {sg_name} {e}')

def fe_authorize_sg_rules(client:boto3.client,fe_rule_name:str,ingress_rules:dict):
    print('Creating frontend security group rules...')
    try:
        response = client.authorize_security_group_ingress(
            CidrIp=ingress_rules['CidrIp'],
            FromPort=ingress_rules['FromPort'],
            IpProtocol=ingress_rules['IpProtocol'],
            ToPort=ingress_rules['ToPort'],
            TagSpecifications=[
                {
                    'ResourceType': 'security-group-rule',
                    'Tags': tagit([ 
                        {'Key': 'Name', 'Value': fe_rule_name},
                        {'Key': 'env', 'Value': env},
                    ])
                },
            ],
        )
        print(f'Security group rule for frontend created')
    except ClientError as e:
        print(f'Could not create frontend security group rule {e}') 

def be_authorize_sg_rules(client:boto3.client,be_rule_name:str,ingress_rules:dict):
    print('Creating backend security group rules...')
    try:    
        response = client.authorize_security_group_ingress(
            SourceSecurityGroupName=ingress_rules['SourceSecurityGroupId'],
            FromPort=ingress_rules['FromPort'],
            IpProtocol=ingress_rules['IpProtocol'],
            ToPort=ingress_rules['ToPort'],
            TagSpecifications=[
                {
                    'ResourceType': 'security-group-rule',
                    'Tags': tagit([ 
                        {'Key': 'Name', 'Value': be_rule_name},
                        {'Key': 'env', 'Value': env},
                    ])
                },
            ],
        )
        print(f'Security group rule for backend created')
    except ClientError as e:
        print(f'Could not create backend security group rule {e}') 

def authorize_fe_sg_egress(client:boto3.client):
    pass

def authorize_be_sg_ingress(client:boto3.client):
    pass

def authorize_be_sg_egress(client:boto3.client):
    pass








def destroy_all_sgs(client:boto3.client):
    try:
        response = client.describe_security_groups( Filters=[{ 'Name': 'tag:project','Values': [project] }] )
        for sg in response['SecurityGroups']: 
            try:
                client.delete_security_group(GroupId=sg['GroupId'])
            except ClientError as e:
                print(f'Could not delete security group {sg['GroupId']}')
    except ClientError as e:
        print(f'Could not delete securitygroup {e}')

