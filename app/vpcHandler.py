import boto3
from models import *


# AWS credentials setup (ensure you have AWS credentials set in your environment, or use a config file)
aws_region = "us-west-2"  # Replace with your region


# Boto3 client for interacting with AWS
ec2_client = boto3.client('ec2', region_name=aws_region)


# Helper function to create a VPC and subnets using Boto3
def create_vpc_with_subnets(vpc_name: str, cidr_block: str, subnets: List[SubnetConfig]):
    # Create the VPC
    vpc_response = ec2_client.create_vpc(CidrBlock=cidr_block, AmazonProvidedIpv6CidrBlock=False)
    vpc_id = vpc_response['Vpc']['VpcId']

    # Add a Name tag to the VPC
    ec2_client.create_tags(Resources=[vpc_id], Tags=[{"Key": "Name", "Value": vpc_name}])

    subnet_ids = []
    for subnet in subnets:
        # Create subnets
        subnet_response = ec2_client.create_subnet(
            VpcId=vpc_id,
            CidrBlock=subnet.cidr_block,
            AvailabilityZone=subnet.availability_zone
        )
        subnet_id = subnet_response['Subnet']['SubnetId']
        subnet_ids.append(subnet_id)

    return vpc_id, subnet_ids
