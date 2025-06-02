import os

import boto3

from utils.tagger import tagit

from dotenv import load_dotenv
# Load environment variables from the .env file
load_dotenv()

project = os.getenv('PROJECT')
env = os.getenv('ENV')

vpc_name = "vpc_"+project+"_"+env

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

        return vpc_id
    
    except KeyError as e:
        # Print the error for debugging
        print(f"Error creating VPC: {str(e)}")
        raise

    

