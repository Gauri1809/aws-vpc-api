import boto3
from app.models.models import *
import uuid

aws_region = "us-west-2"

# Boto3 client for interacting with AWS
ec2_client = boto3.client('ec2', region_name=aws_region)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('VpcTable')


# Function to create a VPC and subnets
def create_vpc_with_subnets(vpc_name: str, cidr_block: str, subnets: List[SubnetConfig]):
    try:
        # Create the VPC
        vpc_response = ec2_client.create_vpc(CidrBlock=cidr_block, AmazonProvidedIpv6CidrBlock=False)
        vpc_id = vpc_response['Vpc']['VpcId']

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

        # Store results in DynamoDB
        store_vpc_data(vpc_id, subnet_ids)

        return vpc_id, subnet_ids

    except Exception as e:
        raise Exception(f"Failed to create VPC data: {e}")

# Function to store the created VPC details in dynamoDB
def store_vpc_data(vpc_id, subnet_ids):
    try:
        table.put_item(
            Item={
                'VpcId': vpc_id,
                'SubnetIds': subnet_ids,
                'createTS': str(uuid.uuid4())
            }
        )
    except Exception as e:
        raise Exception(f"Failed to store VPC data: {e}")

# Function to retrieve VPC data from DynamoDB by VPC ID
def get_vpc_data(vpc_id):
    try:
        response = table.get_item(
            Key={'VpcId': vpc_id}
        )

        item = response.get('Item')
        if item is None:
            raise Exception("VPC not found")

        return response.get('Item')
    except Exception as e:
        raise Exception(f"Failed to retrieve VPC data: {e}")
