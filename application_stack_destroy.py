import os

import boto3

from dotenv import load_dotenv
load_dotenv()

from ec2 import destroy_ec2
from security_group import destroy_all_sgs
from route_table import destroy_route_table
from subnet import destroy_all_subnets
from internet_gateway import destroy_internet_gateway
from vpc import destroy_all_non_default_vpcs


project = os.getenv('PROJECT')

client = boto3.client('ec2')

if __name__ == '__main__':
    destroy_ec2(client)
    destroy_all_sgs(client)
    destroy_route_table(client)
    destroy_all_subnets(client)
    destroy_internet_gateway(client)
    destroy_all_non_default_vpcs(client)