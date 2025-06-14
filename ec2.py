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
ec2_img_id = os.getenv('EC2_AMI_ID')
ec2_inst_type = os.getenv('EC2_INSTANCE_TYPE')
key_pair_name = os.getenv('EC2_KEY_PAIR_NAME')

ec2_name = f'ec2_{project}_{env}'

def create_key_pair(client:boto3.client):
    response = client.create_key_pair(
        KeyName=key_pair_name,
        KeyType='ed25519',
        TagSpecifications=[
            {
                'ResourceType': 'key-pair',
                'Tags': tagit(
                    [
                        {'Key': 'Name','Value': key_pair_name},
                        {'Key': 'env','Value': env},
                    ]
                )
            },
        ],
        KeyFormat='pem',
    )

def describe_ec2(client:boto3.client):
    try:
        response = client.describe_instances(
            Filters=[
                {'Name': 'tag:project', 'Values': [project]},
                {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}
            ]
        )
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append(instance)
        return instances
    except ClientError as e:
        print(f'Could not describe ec2 {ec2_name} {e}')
        return []

def create_all_ec2(client:boto3.client):
    
    subnets_response = client.describe_subnets(Filters=[
        {'Name': 'tag:project','Values': [project]},
    ])

    if len(subnets_response):
        subnet_ids=[]
        
        for sn in  subnets_response['Subnets']:
            subnet_ids.append(sn['SubnetId'])
        print(subnet_ids)
        
        fe_sg_response = client.describe_security_groups(Filters=[
            {'Name': 'tag:project', 'Values': [project]},
            {'Name': 'tag:level', 'Values': ['frontend']},
        ])
        fe_sg_id = fe_sg_response['SecurityGroups'][0]['GroupId'] 
        print(fe_sg_id)

        be_sg_response = client.describe_security_groups(Filters=[
            {'Name': 'tag:project', 'Values': [project]},
            {'Name': 'tag:level', 'Values': ['backend']},
        ])
        be_sg_id = be_sg_response['SecurityGroups'][0]['GroupId'] 
        print(be_sg_id)
        
        create_key_pair(client)
        
        for i , sn_id in enumerate(subnet_ids):
            ec2_instance_name = f'{ec2_name}_{i}'
            if i%2==0:
                create_ec2(client, ec2_instance_name, sn_id, fe_sg_id)
            else:
                create_ec2(client, ec2_instance_name, sn_id, be_sg_id)

def create_ec2(client:boto3.client , ec2_instance_name:str, subnet_id:str, sg_id:str):
    
    print('Creating EC2 instance ...')

    try:
        response = client.run_instances(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sdh',
                    'Ebs': {
                        'VolumeSize': 100,
                    },
                },
            ],
            ImageId=ec2_img_id,
            InstanceType=ec2_inst_type,
            KeyName=key_pair_name,
            MaxCount=1,
            MinCount=1,
            SecurityGroupIds=[sg_id],
            SubnetId=subnet_id,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': tagit(
                        [
                            {'Key': 'Name','Value': ec2_instance_name},
                            {'Key': 'env','Value': env},
                        ]
                    )
                },
            ],
        )
        instance_id = response['Instances'][0]['InstanceId']

        waiter = client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        print(f'EC2 instance created {instance_id}')    
    
    except ClientError as e:
        print(f'Could not create EC2 instance {response} {e}')


def destroy_ec2 (client:boto3.client):
    instances = describe_ec2(client)

    if len(instances) > 0:
        print(f'Terminating all EC2 instances')
        instances_ids=[]
        for instance in instances: instances_ids.append(instance['InstanceId'])
        
        client.terminate_instances(InstanceIds=instances_ids)
        waiter = client.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=instances_ids)
        print(f'All EC2 instances {instances_ids} have been deleted successfully')

    else:
        print(f'There are no instances of EC2 up')