import json
import os
import sys
sys.path.insert(0, 'package')

from lambda_function import lambda_handler

class MockContext:
    def __init__(self):
        self.aws_request_id = "test-request-id-123"

os.environ['GOOGLE_ADS_DEVELOPER_TOKEN'] = 'YOUR_DEVELOPER_TOKEN_HERE'
os.environ['GOOGLE_ADS_CLIENT_CUSTOMER_ID'] = 'YOUR_CUSTOMER_ID_HERE'

with open('google-ads-credentials.json', 'r') as f:
    import base64
    creds_b64 = base64.b64encode(f.read().encode()).decode()
    os.environ['GOOGLE_ADS_CREDENTIALS'] = creds_b64

test_event = {
    'httpMethod': 'GET',
    'path': '/rave-mcp',
    'queryStringParameters': {
        'param': 'create-campaign',
        'name': 'test'
    }
}

context = MockContext()
response = lambda_handler(test_event, context)
print(json.dumps(response, indent=2))