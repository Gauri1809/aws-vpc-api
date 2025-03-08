#!/bin/bash

# Initialize Terraform
terraform init

# Apply Terraform configuration
terraform apply --auto-approve

# Zip the FastAPI application for Lambda deployment
zip -r deployment.zip app/

# Update Lambda function with the new zip file
aws lambda update-function-code --function-name vpc-api-lambda --zip-file fileb://deployment.zip

# Output API Gateway URL
echo "API Gateway URL: $(terraform output api_gateway_url)"
