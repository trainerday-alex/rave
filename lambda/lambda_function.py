import json
import boto3

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters', {}) or {}
        action = query_params.get('param')
        campaign_name = query_params.get('name')
        
        if action == 'create-campaign' and campaign_name:
            result = invoke_google_ads_lambda(action, campaign_name)
            
            if result.get('success'):
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET',
                        'Access-Control-Allow-Headers': 'Content-Type'
                    },
                    'body': json.dumps({
                        'message': result.get('message'),
                        'campaign_name': campaign_name,
                        'campaign_id': result.get('campaign_id'),
                        'timestamp': context.aws_request_id
                    })
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': result.get('error'),
                        'message': result.get('message', 'Failed to create campaign')
                    })
                }
        else:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'message': 'Hello from rave-mcp!',
                    'usage': 'Add ?param=create-campaign&name=YOUR_CAMPAIGN_NAME to create a campaign',
                    'timestamp': context.aws_request_id,
                    'method': event.get('httpMethod', 'GET'),
                    'path': event.get('path', '/rave-mcp')
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to process request'
            })
        }

def invoke_google_ads_lambda(action, campaign_name):
    try:
        lambda_client = boto3.client('lambda')
        
        payload = {
            'action': action,
            'campaign_name': campaign_name
        }
        
        response = lambda_client.invoke(
            FunctionName='rave-mcp-google-ads',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        return response_payload.get('body', {})
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to invoke Google Ads Lambda'
        }