import os

import boto3
from dotenv import load_dotenv

from vpc import create_vpc

# Load environment variables from the .env file
load_dotenv()

region = os.getenv('AWS_REGION')
vpc_cidr = os.getenv('VPC_CIDR')
subnet_cidr = os.getenv('SUBNET_CIDR')
env = os.getenv('ENV')


ec2_client = boto3.client('ec2')


def main():
    vpc_id = create_vpc( ec2_client , vpc_cidr , env )
    print(vpc_id)

if __name__ == '__main__':
    main()
