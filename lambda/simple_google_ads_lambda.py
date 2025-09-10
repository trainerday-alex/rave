import json
import os
import base64
import requests
from google.auth import credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account

def lambda_handler(event, context):
    try:
        action = event.get('action')
        campaign_name = event.get('campaign_name')
        
        if action == 'create-campaign' and campaign_name:
            result = create_google_ads_campaign_rest(campaign_name)
            return {
                'statusCode': 200,
                'body': {
                    'success': True,
                    'message': 'Campaign created successfully',
                    'campaign_name': campaign_name,
                    'result': result
                }
            }
        else:
            return {
                'statusCode': 400,
                'body': {
                    'success': False,
                    'message': 'Invalid action or missing campaign_name'
                }
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'success': False,
                'error': str(e),
                'message': 'Failed to process Google Ads request'
            }
        }

def create_google_ads_campaign_rest(campaign_name):
    try:
        # Get environment variables
        developer_token = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN')
        customer_id = os.environ.get('GOOGLE_ADS_CLIENT_CUSTOMER_ID')
        credentials_json = os.environ.get('GOOGLE_ADS_CREDENTIALS')
        
        if not all([developer_token, customer_id, credentials_json]):
            raise Exception("Missing required environment variables")
        
        # Decode service account credentials to validate they exist
        credentials_data = json.loads(base64.b64decode(credentials_json).decode('utf-8'))
        
        # Verify we have the service account
        if not credentials_data.get('client_email'):
            raise Exception("Invalid service account credentials")
        
        # Create service account credentials
        creds = service_account.Credentials.from_service_account_info(
            credentials_data,
            scopes=['https://www.googleapis.com/auth/adwords']
        )
        
        # Get access token
        creds.refresh(Request())
        access_token = creds.token
        
        # Headers for all requests
        headers = {
            'Authorization': f'Bearer {access_token}',
            'developer-token': developer_token,
            'Content-Type': 'application/json'
        }
        
        # Step 1: Create campaign budget first
        budget_data = {
            "operations": [{
                "create": {
                    "name": f"{campaign_name} Budget",
                    "deliveryMethod": "STANDARD",
                    "amountMicros": "1000000"  # $1.00
                }
            }]
        }
        
        budget_url = f'https://googleads.googleapis.com/v17/customers/{customer_id}/campaignBudgets:mutate'
        budget_response = requests.post(budget_url, headers=headers, json=budget_data)
        
        if budget_response.status_code != 200:
            return {
                'success': False,
                'error': f'Budget creation failed: {budget_response.status_code}',
                'response': budget_response.text,
                'test_account': True
            }
        
        budget_result = budget_response.json()
        budget_resource_name = budget_result['results'][0]['resourceName']
        
        # Step 2: Create campaign with the budget
        campaign_data = {
            "operations": [{
                "create": {
                    "name": campaign_name,
                    "status": "PAUSED",
                    "advertisingChannelType": "SEARCH",
                    "campaignBudget": budget_resource_name
                }
            }]
        }
        
        campaign_url = f'https://googleads.googleapis.com/v17/customers/{customer_id}/campaigns:mutate'
        campaign_response = requests.post(campaign_url, headers=headers, json=campaign_data)
        
        if campaign_response.status_code == 200:
            campaign_result = campaign_response.json()
            campaign_resource_name = campaign_result['results'][0]['resourceName']
            campaign_id = campaign_resource_name.split('/')[-1]
            
            return {
                'success': True,
                'message': f'Campaign "{campaign_name}" created successfully in test account',
                'campaign_id': campaign_id,
                'campaign_resource_name': campaign_resource_name,
                'budget_resource_name': budget_resource_name,
                'customer_id': customer_id,
                'status': 'PAUSED',
                'type': 'SEARCH',
                'test_account': True
            }
        else:
            return {
                'success': False,
                'error': f'Campaign creation failed: {campaign_response.status_code}',
                'response': campaign_response.text,
                'budget_created': budget_resource_name,
                'test_account': True
            }
        
    except Exception as e:
        raise Exception(f"Campaign creation failed: {str(e)}")