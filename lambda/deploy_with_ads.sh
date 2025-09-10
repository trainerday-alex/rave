#!/bin/bash

echo "Creating deployment package with Google Ads API..."

# Create deployment package with dependencies
cd package
zip -r ../lambda-deployment-with-ads.zip . -x "*.pyc"
cd ..

# Update Lambda function code
FUNCTION_NAME="rave-mcp-lambda"
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://lambda-deployment-with-ads.zip

# Set environment variables for Lambda
echo "You need to set these environment variables in Lambda:"
echo "GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token"
echo "GOOGLE_ADS_CLIENT_CUSTOMER_ID=your_customer_id"
echo "GOOGLE_ADS_CREDENTIALS=base64_encoded_service_account_json"

# Clean up
rm lambda-deployment-with-ads.zip

echo "Lambda function updated. Set the environment variables in AWS Lambda console."