output "api_gateway_url" {
  value = aws_api_gateway_rest_api.vpc_api.execution_arn
}
