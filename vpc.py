import os

import boto3

from dotenv import load_dotenv

from utils.tagger import tagit

def create_vpc( client:boto3.client , vpc_cidr:str , env:str ):
    # VPC creation and tagging
    try:
        
        describe_response = client.describe_vpcs(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': ['vpc_project_boto3_'+env]
                },
            ],
        )
        if len(describe_response['Vpcs']) != 0:
            print("This VPC here already existed so I will not create a new one - > "+describe_response['Vpcs'][-1]['VpcId'])
            return describe_response['Vpcs'][-1]['VpcId']

        vpc_response = client.create_vpc(
            CidrBlock = vpc_cidr,
            TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags': tagit(
                        [
                            {
                                'Key': 'Name',
                                'Value': 'vpc_project_boto3_'+env
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

        vpc_id = vpc_response['Vpc']['VpcId']
        return vpc_id
    
    except KeyError as e:
        # Print the error for debugging
        print(f"Error creating VPC: {str(e)}")
        raise

    

