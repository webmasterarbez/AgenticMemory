# Quick Reference: Adding New Lambda Functions

**Use this guide when adding new functions to the AgenticMemory project.**

---

## 🚀 Quick Start (5 Steps)

### 1️⃣ Create Handler
```bash
# Create directory and file
mkdir src/YOUR_FUNCTION_NAME
nano src/YOUR_FUNCTION_NAME/handler.py
```

### 2️⃣ Update Template
```bash
# Edit template.yaml - add your function definition
nano template.yaml
```

### 3️⃣ Build
```bash
sam build --use-container
```

### 4️⃣ Deploy
```bash
sam deploy
```

### 5️⃣ Test
```bash
# Get endpoint URL from outputs
aws cloudformation describe-stacks --stack-name sam-app --query 'Stacks[0].Outputs'
```

---

## 📝 Function Handler Template

```python
"""
src/YOUR_FUNCTION_NAME/handler.py
"""
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Function description
    
    Event structure:
    {
        "body": "...",  # JSON string for POST
        "headers": {...},
        "queryStringParameters": {...}
    }
    """
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        # Parse body if POST request
        if event.get('body'):
            body = json.loads(event['body'])
        
        # Your logic here
        result = {
            'message': 'Success',
            'data': {}
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # If CORS needed
            },
            'body': json.dumps(result)
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON'})
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

## 📋 template.yaml Addition

Add this to the `Resources:` section:

```yaml
  YourFunctionName:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/YOUR_FUNCTION_NAME/
      Handler: handler.lambda_handler
      Runtime: python3.12
      Timeout: 30  # Adjust as needed (max 900)
      MemorySize: 256  # Adjust as needed
      ReservedConcurrentExecutions: 10
      Environment:
        Variables:
          MEM0_API_KEY: !Ref Mem0ApiKey
          MEM0_ORG_ID: !Ref Mem0OrgId
          MEM0_PROJECT_ID: !Ref Mem0ProjectId
          # Add more env vars as needed
      Layers:
        - !Ref AgenticMemoriesLambdaLayer  # If using mem0
      Events:
        HttpPost:
          Type: HttpApi
          Properties:
            Path: /your-endpoint
            Method: POST  # or GET

  YourFunctionNameLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub /aws/lambda/${YourFunctionName}
      RetentionInDays: 7
```

Add this to the `Outputs:` section:

```yaml
  YourFunctionApiUrl:
    Description: "API Gateway endpoint URL for YourFunction"
    Value: !Sub "https://${ServerlessHttpApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/your-endpoint"
```

---

## 🎯 Common Patterns

### Using Mem0 Client
```python
from mem0 import MemoryClient
import os

# Initialize OUTSIDE handler (reused across invocations)
client = MemoryClient(
    api_key=os.environ['MEM0_API_KEY'],
    org_id=os.environ['MEM0_ORG_ID'],
    project_id=os.environ['MEM0_PROJECT_ID']
)

def lambda_handler(event, context):
    # Use client here
    memories = client.get_all(user_id="...")
```

### Header-Based Authentication
```python
def lambda_handler(event, context):
    headers = event.get('headers', {})
    api_key = headers.get('X-Api-Key') or headers.get('x-api-key')
    
    if api_key != os.environ['EXPECTED_API_KEY']:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Unauthorized'})
        }
    
    # Process request...
```

### HMAC Signature Validation
```python
import hmac
import hashlib

def verify_signature(body, signature_header, secret):
    """Verify HMAC signature"""
    parts = signature_header.split(',')
    timestamp = parts[0].split('=')[1]
    signature = parts[1].split('=')[1]
    
    # Check timestamp (30 min tolerance)
    if abs(int(time.time()) - int(timestamp)) > 1800:
        return False
    
    # Verify signature
    message = f"{timestamp}.{body}"
    expected = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)
```

### Async Processing Pattern
```python
def lambda_handler(event, context):
    # Return immediately to prevent timeout
    response = {
        'statusCode': 200,
        'body': json.dumps({'status': 'processing'})
    }
    
    try:
        # Long-running processing here
        # Errors logged but don't affect response
        result = do_heavy_processing()
    except Exception as e:
        logger.error(f"Processing error: {str(e)}", exc_info=True)
    
    return response
```

---

## 🧪 Testing

### Create Test Script
```bash
# Create in scripts/
cat > scripts/test_your_function.py << 'EOF'
#!/usr/bin/env python3
import os
import json
import urllib.request

# Get environment variables
API_URL = os.getenv("YOUR_FUNCTION_URL") or input("Enter API URL: ")

# Prepare request
payload = {"key": "value"}
data = json.dumps(payload).encode('utf-8')

req = urllib.request.Request(
    API_URL,
    data=data,
    headers={'Content-Type': 'application/json'}
)

# Send request
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f"✅ Success: {json.dumps(result, indent=2)}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
EOF

chmod +x scripts/test_your_function.py
```

### Test Locally with SAM
```bash
# Create test event
cat > events/your_function.json << 'EOF'
{
  "body": "{\"key\": \"value\"}",
  "headers": {
    "Content-Type": "application/json"
  }
}
EOF

# Test locally
sam local invoke YourFunctionName -e events/your_function.json

# Start local API
sam local start-api
curl -X POST http://localhost:3000/your-endpoint -d '{"key":"value"}'
```

---

## 📊 Monitoring

### View Logs
```bash
# Tail logs in real-time
aws logs tail /aws/lambda/YourFunctionName --follow

# Get recent logs
aws logs tail /aws/lambda/YourFunctionName --since 1h

# Filter for errors
aws logs filter-pattern /aws/lambda/YourFunctionName --filter-pattern "ERROR"
```

### Check Metrics
```bash
# Get function metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=YourFunctionName \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

---

## 🔧 Troubleshooting

### Build Issues
```bash
# Clean build
rm -rf .aws-sam
sam build --use-container

# Check build output
ls -la .aws-sam/build/YourFunctionName/
```

### Deployment Issues
```bash
# Check stack events
aws cloudformation describe-stack-events \
  --stack-name sam-app \
  --max-items 20

# Force deployment
sam deploy --no-confirm-changeset
```

### Runtime Issues
```bash
# Check function configuration
aws lambda get-function-configuration \
  --function-name YourFunctionName

# Test function directly
aws lambda invoke \
  --function-name YourFunctionName \
  --payload '{"body": "{\"test\": true}"}' \
  response.json
cat response.json
```

---

## 📚 Documentation Checklist

After adding a new function:

- [ ] Update main README.md with function description
- [ ] Add test script to scripts/
- [ ] Update scripts/README.md with test instructions
- [ ] Add function to docs/SPECIFICATION.md if applicable
- [ ] Update docs/QUICK_REFERENCE.md with new endpoint
- [ ] Document any new environment variables
- [ ] Add example payloads to test_data/ if needed
- [ ] Update CHANGELOG.md with changes

---

## ⚡ Pro Tips

1. **Reuse Lambda Layer**: Include `Layers: [!Ref AgenticMemoriesLambdaLayer]` to use mem0
2. **Initialize Outside Handler**: Create clients at module level for reuse
3. **Log User IDs**: Always include user/caller ID in logs for debugging
4. **Set Timeouts Appropriately**: 30s for sync, 60s+ for async processing
5. **Use Reserved Concurrency**: `ReservedConcurrentExecutions: 10` prevents cold starts
6. **Return Early**: For async processing, return 200 immediately
7. **Test Locally First**: Use `sam local invoke` before deploying
8. **Version Control**: Commit changes before deploying

---

## 🎯 Next Steps

1. **Plan your function**: What will it do? What inputs? What outputs?
2. **Create handler**: Use the template above
3. **Update template.yaml**: Add function definition
4. **Build and test locally**: `sam build && sam local invoke`
5. **Deploy**: `sam deploy`
6. **Test deployed**: Use test script or curl
7. **Monitor**: Check CloudWatch logs
8. **Document**: Update relevant docs

---

**Need help?** Check:
- BASE_READINESS_CHECKLIST.md - Complete setup verification
- docs/SPECIFICATION.md - Architecture details
- docs/CLAUDE.md - Development guide
- docs/QUICK_REFERENCE.md - Command reference
