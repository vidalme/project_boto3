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
ec2_key_pair_name = os.getenv('EC2_KEY_PAIR_NAME')


ec2_name = f'ec2_{project}_{env}'


def create_ec2(client:boto3.client ,vpc_id:str, subnet_id:str, fe_sg_id:str):
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
            KeyName=ec2_key_pair_name,
            MaxCount=1,
            MinCount=1,
            SecurityGroupIds=[
                fe_sg_id,
            ],
            SubnetId=subnet_id,
            TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': tagit(
                        [
                            {
                                'Key': 'Name',
                                'Value': ec2_name
                            },
                            {
                                'Key': 'env',
                                'Value': env
                            },
                        ]
                    )
                },
            ],
        )
    except ClientError as e:
        print(f'Could not create ec2 {e}')