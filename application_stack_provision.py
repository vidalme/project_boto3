import os

import boto3

from vpc import create_vpc
from subnet import create_subnets

from dotenv import load_dotenv
# Load environment variables from the .env file
load_dotenv()

project = os.getenv('PROJECT')
region = os.getenv('AWS_REGION')
vpc_cidr = os.getenv('VPC_CIDR')
subnet_cidr = os.getenv('SUBNET_CIDR')
env = os.getenv('ENV')

ec2_client = boto3.client('ec2',region_name=region)

if __name__ == '__main__':
    vpc_id = create_vpc(ec2_client, vpc_cidr)
    create_subnets(ec2_client, vpc_id)
