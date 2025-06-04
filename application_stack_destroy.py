import os

import boto3

from dotenv import load_dotenv
load_dotenv()

project = os.getenv('PROJECT')
client = boto3.client('ec2')

# Destroys all subnets with the project name Tag associated
def destroy_all_subnets():

    response = client.describe_subnets(
        Filters=[
            {
                'Name': 'tag:project',
                'Values': [
                    project,
                ]
            },
        ],
    )
    for i in response['Subnets']:
        response = client.delete_subnet(
            SubnetId=i['SubnetId'],
        )
        print(f"Subnet {i['SubnetId']} has been deleted successfully")


# for testing I made this a VPC wipe out
# loops all vpcs and deletes every non default vpc
def destroy_all_non_default_vpcs(): 
    
    response = client.describe_vpcs()
    for vpc in response['Vpcs']:
        if vpc['IsDefault']:
            print(f'Let us not delete {vpc['VpcId']}, the Default VPC please')
        else:
            print(f'VPC {vpc['VpcId']} has been deleted successfully.')
            print("\n")
            client.delete_vpc(VpcId=vpc['VpcId'])



if __name__ == '__main__':
    destroy_all_subnets()
    destroy_all_non_default_vpcs()