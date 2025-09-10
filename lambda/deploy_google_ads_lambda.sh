#!/bin/bash

echo "Creating Google Ads Lambda function..."

# Copy the Google Ads Lambda code to package directory
cp google_ads_lambda.py package/lambda_function.py
cp google-ads-credentials.json package/

# Create deployment package for Google Ads Lambda
cd package
zip -r ../google-ads-lambda-deployment.zip . -x "*.pyc"
cd ..

# Create the Google Ads Lambda function
GOOGLE_ADS_FUNCTION_NAME="rave-mcp-google-ads"
aws lambda create-function \
  --function-name $GOOGLE_ADS_FUNCTION_NAME \
  --runtime python3.9 \
  --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://google-ads-lambda-deployment.zip \
  --description "Google Ads Lambda function for rave-mcp" \
  --timeout 30 \
  --memory-size 256

echo "Google Ads Lambda function created: $GOOGLE_ADS_FUNCTION_NAME"

# Update main Lambda function
echo "Updating main Lambda function..."
zip lambda-main-deployment.zip lambda_function.py

aws lambda update-function-code \
  --function-name rave-mcp-lambda \
  --zip-file fileb://lambda-main-deployment.zip

echo "Main Lambda function updated"

# Add IAM permission for main Lambda to invoke Google Ads Lambda
aws lambda add-permission \
  --function-name $GOOGLE_ADS_FUNCTION_NAME \
  --statement-id "allow-main-lambda-invoke" \
  --action lambda:InvokeFunction \
  --principal lambda.amazonaws.com \
  --source-arn "arn:aws:lambda:$(aws configure get region):$(aws sts get-caller-identity --query Account --output text):function:rave-mcp-lambda"

# Clean up
rm google-ads-lambda-deployment.zip lambda-main-deployment.zip

echo ""
echo "✅ Deployment complete!"
echo ""
echo "⚠️  IMPORTANT: Set these environment variables for $GOOGLE_ADS_FUNCTION_NAME:"
echo "   GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token"
echo "   GOOGLE_ADS_CLIENT_CUSTOMER_ID=your_customer_id" 
echo "   GOOGLE_ADS_CREDENTIALS=base64_encoded_service_account_json"
echo ""
echo "You can set them using:"
echo "aws lambda update-function-configuration --function-name $GOOGLE_ADS_FUNCTION_NAME --environment Variables='{\"GOOGLE_ADS_DEVELOPER_TOKEN\":\"your_token\",\"GOOGLE_ADS_CLIENT_CUSTOMER_ID\":\"your_id\",\"GOOGLE_ADS_CREDENTIALS\":\"your_base64_creds\"}'"