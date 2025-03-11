import boto3
from fastapi import HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os

# OAuth2PasswordBearer to extract token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Cognito configuration
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_REGION = os.getenv('COGNITO_REGION')
COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID')

# Create a Cognito client using boto3
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)


def get_public_keys():
    """
    Fetch public keys from Cognito to validate JWT tokens.
    Cognito publishes its keys at a specific URL.
    """
    jwks_url = f'https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json'
    response = boto3.client('apigatewaymanagementapi').get_jwks(jwks_url)
    return response['keys']


def verify_token(token: str):
    """
    Verify JWT token by checking its signature and claims.
    """
    try:
        # Decode the token and verify signature against the public keys
        payload = jwt.decode(token, get_public_keys(), algorithms=["RS256"], audience=COGNITO_APP_CLIENT_ID)
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_current_user(token: str = Security(oauth2_scheme)):
    """
    This function verifies the JWT token and extracts the user information.
    It is called as a dependency in FastAPI routes.
    """
    # Verify the token using Cognito public keys
    user_info = verify_token(token)

    return user_info['sub']
