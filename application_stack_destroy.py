import os

import boto3

from dotenv import load_dotenv
load_dotenv()

from internet_gateway import destroy_internet_gateway
from subnet import destroy_all_subnets
from vpc import destroy_all_non_default_vpcs

project = os.getenv('PROJECT')

client = boto3.client('ec2')

if __name__ == '__main__':
    destroy_internet_gateway(client)
    destroy_all_subnets(client)
    destroy_all_non_default_vpcs(client)