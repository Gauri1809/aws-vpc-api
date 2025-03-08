from pydantic import BaseModel
from typing import List

# Models for input and output validation
class SubnetConfig(BaseModel):
    name: str
    cidr_block: str
    availability_zone: str

class CreateVPCRequest(BaseModel):
    vpc_name: str
    cidr_block: str
    subnets: List[SubnetConfig]

class VPCInfo(BaseModel):
    vpc_id: str
    subnets: List[str]
