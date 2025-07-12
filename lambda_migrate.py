import os
import django
from django.core.management import execute_from_command_line
from django.conf import settings

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_packing_list.settings_aws')

# Initialize Django
django.setup()

def handler(event, context):
    """
    AWS Lambda handler for Django migrations and management commands
    """
    try:
        print("Starting Django migrations...")
        
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("Migrations completed successfully")
        
        # Collect static files if needed
        if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
            print("Collecting static files...")
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
            print("Static files collected successfully")
        
        # Create example data if needed
        try:
            execute_from_command_line(['manage.py', 'create_example_data'])
            print("Example data created successfully")
        except Exception as e:
            print(f"Example data creation failed (may already exist): {e}")
        
        return {
            'statusCode': 200,
            'body': 'Migration completed successfully'
        }
        
    except Exception as e:
        print(f"Error in migration handler: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': f'Migration failed: {str(e)}'
        }

# For local testing
if __name__ == "__main__":
    test_context = type('Context', (), {
        'aws_request_id': 'test-request-id',
        'function_name': 'test-migrate-function',
        'function_version': '1',
        'invoked_function_arn': 'arn:aws:lambda:us-east-1:123456789012:function:test-migrate-function',
        'memory_limit_in_mb': '1024',
        'remaining_time_in_millis': lambda: 300000
    })()
    
    result = handler({}, test_context)
    print(f"Migration test result: {result}") 