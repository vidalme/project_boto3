import os
import sys

import boto3
from botocore.exceptions import ClientError

from utils.tagger import tagit

from dotenv import load_dotenv
# Load environment variables from the .env file
load_dotenv()

project:str = os.getenv('PROJECT')
env:str = os.getenv('ENV')

vpc_name = f'vpc_{project}_{env}'

def create_vpc( client:boto3.client , vpc_cidr:str ):
    # VPC creation and tagging
    try:
        # check if the VPC already exists   
        describe_vpcs_response = client.describe_vpcs(Filters=[{'Name': 'tag:Name','Values': [vpc_name]}])
        if len(describe_vpcs_response['Vpcs']) != 0:
            current_vpc_id = describe_vpcs_response['Vpcs'][-1]['VpcId']
            print(f'The VPC {current_vpc_id} already existed')
            return current_vpc_id
        
        # create VPC in case there isnt one already
        print('Creating VPC...')
        create_vpc_response = client.create_vpc(
            CidrBlock = vpc_cidr,
            TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags': tagit(
                        [
                            {
                                'Key': 'Name',
                                'Value': vpc_name
                            },
                            {
                                'Key': 'env',
                                'Value': env
                            }
                        ]
                    ),
                }
            ]
        )

        vpc_id = create_vpc_response['Vpc']['VpcId']
        print(f"Created VPC: {vpc_id}")

        waiter = client.get_waiter('vpc_available')
        waiter.wait(VpcIds=[vpc_id])
        print(f"VPC {vpc_id} is available")

        return vpc_id
    
    except ClientError as e:
        print(f"Error creating VPC: {str(e)}")
        sys.exit(1)

# for testing I made this a VPC wipe out
# loops all vpcs and deletes every non default vpc
def destroy_all_non_default_vpcs(client:boto3.client): 
    
    response = client.describe_vpcs()
    for vpc in response['Vpcs']:
        if vpc['IsDefault']:
            # Let us not delete the Default VPC please')
            pass
        else:
            try:
                client.delete_vpc(VpcId=vpc['VpcId'])
                print(f'VPC {vpc['VpcId']} has been deleted successfully.')
            except ClientError as e:
                print(f'Could not delete VPC {vpc['VpcId']} error {e}')