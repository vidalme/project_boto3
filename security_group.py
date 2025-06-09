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

sg_base_name = "sg_"+project+"_"+env
fe_sg_name = 'fe_'+sg_base_name
be_sg_name = 'be_'+sg_base_name

def describe_sg(client:boto3.client, sg_name:str):
    try:
        response = client.describe_security_groups(
            Filters=[
                {
                    'Name': 'tag:project',
                    'Values': [
                        project,
                    ]
                },
                {
                    'Name': 'tag:Name',
                    'Values': [
                        sg_name,
                    ]
                },
            ]
        )
        # print(response['SecurityGroups'])
        return response['SecurityGroups']
    except ClientError as e:
        print(f'Could not create securitygroup {sg_name} {e}')

def create_sgs(client:boto3.client, vpc_id:str):
    create_sg(client,vpc_id,fe_sg_name) if not describe_sg(client,fe_sg_name) else print(f'SecurityGroup {fe_sg_name} already exist')
    create_sg(client,vpc_id,be_sg_name) if not describe_sg(client,be_sg_name) else print(f'SecurityGroup {be_sg_name} already exist')

def create_sg(client:boto3.client, vpc_id:str, sg_name:str):
    try:
        print('Creating security group...')
        response = client.create_security_group(
            Description='Security Group for the frontend of the application',
            GroupName=sg_name,
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'security-group',
                    'Tags': tagit(
                        [
                            {
                                'Key': 'Name',
                                'Value': sg_name
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
        print('Security group created')
    except ClientError as e:
        print(f'Could not create securitygroup {sg_name} {e}')

def authorize_fe_sg_ingress(client:boto3.client):
    response = client.authorize_security_group_ingress(
        CidrIp='0.0.0.0/0',
        FromPort=-1,
        GroupId='string',
        GroupName='string',
        IpProtocol='string',
        SourceSecurityGroupName='string',
        SourceSecurityGroupOwnerId='string',
        ToPort=-1,
        TagSpecifications=[
            {
                'ResourceType': 'capacity-reservation'|'client-vpn-endpoint'|'customer-gateway'|'carrier-gateway'|'coip-pool'|'declarative-policies-report'|'dedicated-host'|'dhcp-options'|'egress-only-internet-gateway'|'elastic-ip'|'elastic-gpu'|'export-image-task'|'export-instance-task'|'fleet'|'fpga-image'|'host-reservation'|'image'|'import-image-task'|'import-snapshot-task'|'instance'|'instance-event-window'|'internet-gateway'|'ipam'|'ipam-pool'|'ipam-scope'|'ipv4pool-ec2'|'ipv6pool-ec2'|'key-pair'|'launch-template'|'local-gateway'|'local-gateway-route-table'|'local-gateway-virtual-interface'|'local-gateway-virtual-interface-group'|'local-gateway-route-table-vpc-association'|'local-gateway-route-table-virtual-interface-group-association'|'natgateway'|'network-acl'|'network-interface'|'network-insights-analysis'|'network-insights-path'|'network-insights-access-scope'|'network-insights-access-scope-analysis'|'outpost-lag'|'placement-group'|'prefix-list'|'replace-root-volume-task'|'reserved-instances'|'route-table'|'security-group'|'security-group-rule'|'service-link-virtual-interface'|'snapshot'|'spot-fleet-request'|'spot-instances-request'|'subnet'|'subnet-cidr-reservation'|'traffic-mirror-filter'|'traffic-mirror-session'|'traffic-mirror-target'|'transit-gateway'|'transit-gateway-attachment'|'transit-gateway-connect-peer'|'transit-gateway-multicast-domain'|'transit-gateway-policy-table'|'transit-gateway-route-table'|'transit-gateway-route-table-announcement'|'volume'|'vpc'|'vpc-endpoint'|'vpc-endpoint-connection'|'vpc-endpoint-service'|'vpc-endpoint-service-permission'|'vpc-peering-connection'|'vpn-connection'|'vpn-gateway'|'vpc-flow-log'|'capacity-reservation-fleet'|'traffic-mirror-filter-rule'|'vpc-endpoint-connection-device-type'|'verified-access-instance'|'verified-access-group'|'verified-access-endpoint'|'verified-access-policy'|'verified-access-trust-provider'|'vpn-connection-device-type'|'vpc-block-public-access-exclusion'|'route-server'|'route-server-endpoint'|'route-server-peer'|'ipam-resource-discovery'|'ipam-resource-discovery-association'|'instance-connect-endpoint'|'verified-access-endpoint-target'|'ipam-external-resource-verification-token'|'mac-modification-task',
                'Tags': [
                    {
                        'Key': 'string',
                        'Value': 'string'
                    },
                ]
            },
        ],
    )

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

