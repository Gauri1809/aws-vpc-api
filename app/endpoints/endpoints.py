from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from app.models.models import *
from app.auth.auth import *
from app.handlers.vpcHandler import *

router = APIRouter()

# Route for creating a VPC
@router.post("/create-vpc", response_model=VPCInfo)
async def create_vpc(request: CreateVPCRequest, token: str = Depends(get_current_user)):
    try:
        vpc_id, subnet_ids = create_vpc_with_subnets(request.vpc_name, request.cidr_block, request.subnets)
        return VPCInfo(vpc_id=vpc_id, subnets=subnet_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route for getting VPC details
@router.get("/get-vpc/{vpc_id}", response_model=VPCInfo)
async def get_vpc(vpc_id: str, token: str = Depends(get_current_user)):
    try:
        vpc_data = get_vpc_data(vpc_id)
        if not vpc_data:
            raise HTTPException(status_code=404, detail="VPC not found")
        return vpc_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


