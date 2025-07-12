import os
import django
from django.core.wsgi import get_wsgi_application
from mangum import Mangum

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_packing_list.settings_aws')

# Initialize Django
django.setup()

# Get Django WSGI application
django_app = get_wsgi_application()

# Create Lambda handler using Mangum
handler = Mangum(django_app, lifespan="off")

# For debugging
def lambda_handler(event, context):
    """
    AWS Lambda handler for Django application
    """
    try:
        # Log the event for debugging
        print(f"Event: {event}")
        print(f"Context: {context}")
        
        # Handle the request
        response = handler(event, context)
        
        # Log the response for debugging
        print(f"Response: {response}")
        
        return response
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error response
        return {
            'statusCode': 500,
            'body': f'Internal server error: {str(e)}',
            'headers': {
                'Content-Type': 'text/plain'
            }
        }

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'httpMethod': 'GET',
        'path': '/',
        'headers': {},
        'body': None,
        'isBase64Encoded': False
    }
    
    test_context = type('Context', (), {
        'aws_request_id': 'test-request-id',
        'function_name': 'test-function',
        'function_version': '1',
        'invoked_function_arn': 'arn:aws:lambda:us-east-1:123456789012:function:test-function',
        'memory_limit_in_mb': '1024',
        'remaining_time_in_millis': lambda: 30000
    })()
    
    result = lambda_handler(test_event, test_context)
    print(f"Test result: {result}") 