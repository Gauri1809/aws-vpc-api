provider "aws" {
  region = "us-west-2"
}

resource "aws_lambda_function" "vpc_api_lambda" {
  function_name = "vpc-api-lambda"
  handler       = "app.handler"
  runtime       = "python3.8"
  filename      = "deployment.zip"

  environment {
    variables = {
      AWS_REGION = "us-west-2"
    }
  }

  # The Lambda execution role that allows it to interact with EC2 resources
  role = aws_iam_role.lambda_execution_role.arn
}

resource "aws_iam_role" "lambda_execution_role" {
  name               = "lambda-execution-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions   = ["sts:AssumeRole"]
    principals = [
      {
        type        = "Service"
        identifiers = ["lambda.amazonaws.com"]
      }
    ]
  }
}

resource "aws_api_gateway_rest_api" "vpc_api" {
  name        = "VPC API"
  description = "API for creating VPC and subnets"
}

resource "aws_api_gateway_resource" "proxy" {
  parent_id   = aws_api_gateway_rest_api.vpc_api.root_resource_id
  path_part   = "{proxy+}"
  rest_api_id = aws_api_gateway_rest_api.vpc_api.id
}

resource "aws_api_gateway_method" "any_method" {
  rest_api_id   = aws_api_gateway_rest_api.vpc_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.vpc_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.any_method.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri  = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.vpc_api_lambda.arn}/invocations"
}

resource "aws_lambda_permission" "api_gateway_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vpc_api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  statement_id  = "AllowExecutionFromAPIGateway"
}
