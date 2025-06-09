import sys
import os

import boto3
from botocore.exceptions import ClientError

from dotenv import load_dotenv

from utils.tagger import tagit

load_dotenv()

project = os.getenv('PROJECT')
env = os.getenv('ENV')
vpc_cidr = os.getenv('VPC_CIDR')

route_table_base_name = "route_table_"+project+"_"+env

def set_route_tables(client:boto3.client, vpc_id:str, igw_id:str, subnets_ids:list):
    
    rts = describe_routetables(client)
    
    if len(rts)==0:
        # create_private_route_table(client, vpc_id, igw_id, subnets_ids)
        create_public_route_table(client, vpc_id, igw_id, subnets_ids)
    else:
        print(f'There are route tables already')

def describe_routetables(client:boto3.client)->list:
    r = client.describe_route_tables(Filters=[{'Name': 'tag:project','Values': [project]}])
    return r['RouteTables']

def create_private_route_table(client:boto3.client, vpc_id:str, igw_id:str, subnets_ids:list):
    try:
        private_table_name = "private_"+route_table_base_name
        response = client.create_route_table(
            TagSpecifications=[{'ResourceType': 'route-table','Tags': tagit([{'Key': 'Name','Value': private_table_name},{'Key': 'env','Value':'env'}])}],
            VpcId=vpc_id
        )
        return response['RouteTable']['RouteTableId']
    except ClientError as e:
        print(f'Could not create RouteTable: {e}') 

def create_public_route_table(client:boto3.client, vpc_id:str, igw_id:str, subnets_ids:list):
    print(f'Creating RouteTables...')
    try:
        public_table_name = "public_"+route_table_base_name
        response = client.create_route_table(
            TagSpecifications=[{'ResourceType': 'route-table','Tags': tagit([{'Key': 'Name','Value': public_table_name},{'Key': 'env','Value':'env'}])}],
            VpcId=vpc_id
        )
        rt_id = response['RouteTable']['RouteTableId']
        print(f'Created RouteTable {rt_id}')
        client.create_route(DestinationCidrBlock='0.0.0.0/0',GatewayId=igw_id,RouteTableId=rt_id)
        print(f'Created public route for RouteTable {rt_id}')
        
        for i in range(len(subnets_ids)):
            if i%2==0:
                associate_route_table(client,rt_id,subnets_ids[i])
                print(f'Associated public routetable {rt_id} with public subnet {subnets_ids[i]}')
        return rt_id
    except ClientError as e:
        print(f'Could not create RouteTable: {e}') 

def associate_route_table(client:boto3.client, rt_id:str, subnet_id:str):
    try:
        response_asssociate = client.associate_route_table(
            SubnetId=subnet_id,
            RouteTableId=rt_id
        )
    except ClientError as e:
        print(f'The routertable {rt_id} is associated to the subnet {subnet_id}')

def destroy_route_table(client:boto3.client):
    route_tables = describe_routetables(client)
    if route_tables:
        for rt in route_tables:
            if rt['Associations']:
                for assoc in rt['Associations']:
                    try:
                        client.disassociate_route_table(AssociationId=assoc['RouteTableAssociationId'])
                        print(f'Route table association {assoc['RouteTableAssociationId']} was desassociated')
                    except ClientError as e:
                        print(f'Could not disassociate route table with subnet {e}')
            try:
                response_delete_table = client.delete_route_table(RouteTableId=rt['RouteTableId'])
                print(f'Route table {rt['RouteTableId']} has been deleted successfully')
            except ClientError as e:
                print(f'Could not delete route table {e}')
