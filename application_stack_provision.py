import os

import boto3

from vpc import create_vpc
from subnet import create_subnets
from internet_gateway import create_internet_gateway

from dotenv import load_dotenv
# Load environment variables from the .env file
load_dotenv()

project = os.getenv('PROJECT')
region = os.getenv('AWS_REGION')
vpc_cidr = os.getenv('VPC_CIDR')
subnet_cidr = os.getenv('SUBNET_CIDR')
env = os.getenv('ENV')

client = boto3.client('ec2',region_name=region)

if __name__ == '__main__':

    # $$$$$ FINops warning $$$$$ 
    # the orrder they are deleted is crucial, if they are not in the correct order we won't be able to erase all resources.
    vpc_id:str = create_vpc(client, vpc_cidr)
    subnets_names:list = create_subnets(client, vpc_id)
    igw_id:str = create_internet_gateway(client, vpc_id)
