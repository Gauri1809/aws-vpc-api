from fastapi import FastAPI, Depends, HTTPException, status
from mangum import Mangum  # AWS Lambda handler
from models import *
from auth import *
from vpcHandler import *


# FastAPI app setup
app = FastAPI()

# In-memory store for VPC and subnet data (this could be replaced with a database in a real application)
vpc_data_store = {}

# Route for authenticating users and getting JWT token
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordBearer = Depends()):
    # Replace this with actual authentication logic (e.g., checking username/password)
    if form_data != "valid_password":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Create JWT token for authenticated user
    access_token = create_access_token(data={"sub": "authenticated_user"})
    return {"access_token": access_token, "token_type": "bearer"}



def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)


# Route for creating a VPC
@app.post("/create-vpc", response_model=VPCInfo)
async def create_vpc(request: CreateVPCRequest, current_user: dict = Depends(get_current_user)):
    vpc_id, subnet_ids = create_vpc_with_subnets(request.vpc_name, request.cidr_block, request.subnets)

    # Store the VPC data (in-memory store for now)
    vpc_data_store[vpc_id] = {
        "vpc_id": vpc_id,
        "subnets": subnet_ids
    }

    return VPCInfo(vpc_id=vpc_id, subnets=subnet_ids)

# Route for getting VPC details
@app.get("/get-vpc/{vpc_id}", response_model=VPCInfo)
async def get_vpc(vpc_id: str, current_user: dict = Depends(get_current_user)):
    vpc_info = vpc_data_store.get(vpc_id)
    if not vpc_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VPC not found")
    return VPCInfo(**vpc_info)

# AWS Lambda handler for FastAPI
handler = Mangum(app)

