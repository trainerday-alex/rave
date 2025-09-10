import json
import os
import base64
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def lambda_handler(event, context):
    try:
        action = event.get('action')
        campaign_name = event.get('campaign_name')
        
        if action == 'create-campaign' and campaign_name:
            result = create_google_ads_campaign(campaign_name)
            return {
                'statusCode': 200,
                'body': {
                    'success': True,
                    'message': 'Campaign created successfully',
                    'campaign_name': campaign_name,
                    'campaign_id': result.get('campaign_id'),
                    'campaign_resource_name': result.get('campaign_resource_name')
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

def create_google_ads_campaign(campaign_name):
    try:
        credentials_json = os.environ.get('GOOGLE_ADS_CREDENTIALS')
        if not credentials_json:
            raise Exception("Google Ads credentials not found in environment variables")
        
        credentials_data = json.loads(base64.b64decode(credentials_json).decode('utf-8'))
        
        config = {
            'developer_token': os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN'),
            'client_customer_id': os.environ.get('GOOGLE_ADS_CLIENT_CUSTOMER_ID'),
            'use_proto_plus': True,
        }
        
        client = GoogleAdsClient.load_from_dict(config, version="v17")
        client._credentials = credentials_data
        
        customer_id = os.environ.get('GOOGLE_ADS_CLIENT_CUSTOMER_ID')
        
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        
        campaign.name = campaign_name
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        
        campaign_budget_service = client.get_service("CampaignBudgetService")
        budget_operation = client.get_type("CampaignBudgetOperation")
        budget = budget_operation.create
        budget.name = f"{campaign_name} Budget"
        budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        budget.amount_micros = 1000000
        
        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[budget_operation]
        )
        
        budget_resource_name = budget_response.results[0].resource_name
        campaign.campaign_budget = budget_resource_name
        
        response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        
        campaign_id = response.results[0].resource_name.split('/')[-1]
        
        return {
            'campaign_id': campaign_id,
            'campaign_resource_name': response.results[0].resource_name
        }
        
    except GoogleAdsException as ex:
        raise Exception(f"Google Ads API error: {ex}")
    except Exception as e:
        raise Exception(f"Campaign creation failed: {str(e)}")