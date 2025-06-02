import boto3


client = boto3.client('ec2')

response = client.describe_vpcs()

for vpc in response['Vpcs']:
    if vpc['IsDefault']:
        print(f'Let us not delete {vpc['VpcId']}, the Default VPC please')
        print("\n")
    else:
        print(f'{vpc['VpcId']} is not the Default VPC, it can be deleted safely.')
        print("\n")
        client.delete_vpc(VpcId=vpc['VpcId'])
    



