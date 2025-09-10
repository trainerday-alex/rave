#!/bin/bash

# Create deployment package
zip -r lambda-deployment.zip lambda_function.py

# Create Lambda function
FUNCTION_NAME="rave-mcp-lambda"
aws lambda create-function \
  --function-name $FUNCTION_NAME \
  --runtime python3.9 \
  --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda-deployment.zip \
  --description "Lambda function for rave-mcp API"

# Create API Gateway REST API
API_NAME="rave-mcp-api"
API_ID=$(aws apigateway create-rest-api \
  --name $API_NAME \
  --description "API Gateway for rave-mcp Lambda" \
  --query 'id' --output text)

echo "API Gateway ID: $API_ID"

# Get the root resource ID
ROOT_RESOURCE_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[?path==`/`].id' \
  --output text)

# Create rave-mcp resource
RESOURCE_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_RESOURCE_ID \
  --path-part "rave-mcp" \
  --query 'id' --output text)

# Create GET method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method GET \
  --authorization-type NONE

# Create integration with Lambda
LAMBDA_ARN="arn:aws:lambda:$(aws configure get region):$(aws sts get-caller-identity --query Account --output text):function:$FUNCTION_NAME"

aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method GET \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:$(aws configure get region):lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations"

# Add permission for API Gateway to invoke Lambda
aws lambda add-permission \
  --function-name $FUNCTION_NAME \
  --statement-id "api-gateway-invoke" \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$(aws configure get region):$(aws sts get-caller-identity --query Account --output text):$API_ID/*/*"

# Deploy the API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod

# Output the endpoint URL
REGION=$(aws configure get region)
echo "Your API endpoint is: https://$API_ID.execute-api.$REGION.amazonaws.com/prod/rave-mcp"

# Clean up
rm lambda-deployment.zip