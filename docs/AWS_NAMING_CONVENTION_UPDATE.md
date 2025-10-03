# AWS Resource Naming Convention Update

## Overview

Updated all AWS resource names to follow the consistent `elevenlabs-agentic-memory-*` naming convention for better organization and clarity.

## Resource Name Changes

### CloudFormation Stack
- **Old**: `sam-app`
- **New**: `elevenlabs-agentic-memory-stack`
- **Note**: Set during deployment with `--stack-name` parameter

### IAM Role
- **Old**: `sam-app-AgenticMemoriesLambdaRole-sgXy7220LdNt` (auto-generated)
- **New**: `elevenlabs-agentic-memory-role` (explicit name)
- **Resource ID**: `AgenticMemoriesLambdaRole`

### S3 Bucket
- **Current**: `elevenlabs-agentic-memory-424875385161-us-east-1` ✅
- **No changes needed** - Already follows convention

### Lambda Functions

| Old Name | New Name | Resource ID |
|----------|----------|-------------|
| `AgenticMemoriesClientData` | `elevenlabs-agentic-memory-lambda-function-client-data` | `AgenticMemoriesClientData` |
| `AgenticMemoriesRetrieve` | `elevenlabs-agentic-memory-lambda-function-search-data` | `AgenticMemoriesRetrieve` |
| `AgenticMemoriesPostCall` | `elevenlabs-agentic-memory-lambda-function-post-call` | `AgenticMemoriesPostCall` |

### CloudWatch Log Groups

| Old Name | New Name | Resource ID |
|----------|----------|-------------|
| `/aws/lambda/AgenticMemoriesClientData` | `/aws/lambda/elevenlabs-agentic-memory-log-client-data` | `AgenticMemoriesClientDataLogGroup` |
| `/aws/lambda/AgenticMemoriesRetrieve` | `/aws/lambda/elevenlabs-agentic-memory-log-search-data` | `AgenticMemoriesRetrieveLogGroup` |
| `/aws/lambda/AgenticMemoriesPostCall` | `/aws/lambda/elevenlabs-agentic-memory-log-post-call` | `AgenticMemoriesPostCallLogGroup` |

### API Gateways

| Old Name | New Name | Resource ID |
|----------|----------|-------------|
| `sam-app` (auto-generated) | `elevenlabs-agentic-memory-api-gateway-client-data` | `AgenticMemoriesClientDataHttpApi` |
| `sam-app` (auto-generated) | `elevenlabs-agentic-memory-api-gateway-search-data` | `AgenticMemoriesRetrieveHttpApi` |
| `sam-app` (auto-generated) | `elevenlabs-agentic-memory-api-gateway-post-call` | `AgenticMemoriesPostCallHttpApi` |

## Deployment Instructions

### Option 1: Fresh Deployment (Recommended)

Deploy with the new stack name:

```bash
sam build --use-container

sam deploy \
  --stack-name elevenlabs-agentic-memory-stack \
  --region us-east-1 \
  --parameter-overrides \
    Mem0ApiKey=$MEM0_API_KEY \
    Mem0OrgId=$MEM0_ORG_ID \
    Mem0ProjectId=$MEM0_PROJECT_ID \
    ElevenLabsWorkspaceKey=$ELEVENLABS_WORKSPACE_KEY \
    ElevenLabsHmacKey=$ELEVENLABS_HMAC_KEY \
  --capabilities CAPABILITY_NAMED_IAM \
  --resolve-s3 \
  --no-confirm-changeset
```

**Note**: The `CAPABILITY_NAMED_IAM` is required because we're now specifying an explicit IAM role name.

### Option 2: Update Existing Stack

Update the existing `sam-app` stack with new resource names:

```bash
sam build --use-container

sam deploy --stack-name sam-app --capabilities CAPABILITY_NAMED_IAM
```

**⚠️ Warning**: This will **replace** existing Lambda functions and API Gateways with new ones. The API endpoint URLs will change.

### Option 3: Migrate with Zero Downtime

1. **Deploy new stack** (fresh deployment with new name)
2. **Update ElevenLabs webhooks** to point to new API URLs
3. **Test new stack** thoroughly
4. **Delete old stack** when ready:
   ```bash
   aws cloudformation delete-stack --stack-name sam-app
   ```

## Updated samconfig.toml

Update your `samconfig.toml` to use the new stack name:

```toml
version = 0.1

[default.deploy.parameters]
stack_name = "elevenlabs-agentic-memory-stack"
region = "us-east-1"
capabilities = "CAPABILITY_NAMED_IAM"
parameter_overrides = "Mem0ApiKey=\"***\" Mem0OrgId=\"***\" ..."
resolve_s3 = true
s3_prefix = "elevenlabs-agentic-memory-stack"
```

## Post-Deployment Verification

### 1. Verify Stack Resources

```bash
aws cloudformation describe-stack-resources \
  --stack-name elevenlabs-agentic-memory-stack \
  --query 'StackResources[].{Type:ResourceType,Name:PhysicalResourceId}' \
  --output table
```

Expected output:
```
-----------------------------------------------------------------
|                   DescribeStackResources                      |
+--------------------------------------+-------------------------+
|                Type                  |          Name           |
+--------------------------------------+-------------------------+
|  AWS::IAM::Role                      |  elevenlabs-agentic-memory-role |
|  AWS::Lambda::Function               |  elevenlabs-agentic-memory-lambda-function-client-data |
|  AWS::Lambda::Function               |  elevenlabs-agentic-memory-lambda-function-search-data |
|  AWS::Lambda::Function               |  elevenlabs-agentic-memory-lambda-function-post-call |
|  AWS::ApiGatewayV2::Api              |  elevenlabs-agentic-memory-api-gateway-client-data |
|  AWS::ApiGatewayV2::Api              |  elevenlabs-agentic-memory-api-gateway-search-data |
|  AWS::ApiGatewayV2::Api              |  elevenlabs-agentic-memory-api-gateway-post-call |
|  AWS::Logs::LogGroup                 |  /aws/lambda/elevenlabs-agentic-memory-log-client-data |
|  AWS::Logs::LogGroup                 |  /aws/lambda/elevenlabs-agentic-memory-log-search-data |
|  AWS::Logs::LogGroup                 |  /aws/lambda/elevenlabs-agentic-memory-log-post-call |
|  AWS::S3::Bucket                     |  elevenlabs-agentic-memory-424875385161-us-east-1 |
+--------------------------------------+-------------------------+
```

### 2. Test Lambda Functions

```bash
# Test ClientData
aws lambda invoke \
  --function-name elevenlabs-agentic-memory-lambda-function-client-data \
  --payload '{"caller_id": "+16129782029"}' \
  /tmp/response.json

# Test Retrieve
aws lambda invoke \
  --function-name elevenlabs-agentic-memory-lambda-function-search-data \
  --payload '{"query": "preferences", "user_id": "+16129782029"}' \
  /tmp/response.json

# Test PostCall
aws lambda invoke \
  --function-name elevenlabs-agentic-memory-lambda-function-post-call \
  --payload '{"conversation_id": "test", "agent_id": "test", "metadata": {"phone_call": {"external_number": "+16129782029"}}}' \
  /tmp/response.json
```

### 3. Check CloudWatch Logs

```bash
# ClientData logs
aws logs tail /aws/lambda/elevenlabs-agentic-memory-log-client-data --follow

# Retrieve logs
aws logs tail /aws/lambda/elevenlabs-agentic-memory-log-search-data --follow

# PostCall logs
aws logs tail /aws/lambda/elevenlabs-agentic-memory-log-post-call --follow
```

### 4. Get API Endpoints

```bash
aws cloudformation describe-stacks \
  --stack-name elevenlabs-agentic-memory-stack \
  --query 'Stacks[0].Outputs' \
  --output table
```

## Breaking Changes

### ⚠️ Important: API URLs Will Change

When you deploy with new resource names, the API Gateway endpoints will have new IDs:

**Old URLs:**
```
https://8nv3jj2gie.execute-api.us-east-1.amazonaws.com/Prod/client-data
https://7h6j2vasna.execute-api.us-east-1.amazonaws.com/Prod/retrieve
https://7iumhxcckh.execute-api.us-east-1.amazonaws.com/Prod/post-call
```

**New URLs:** (example - actual IDs will be different)
```
https://xyz123abc4.execute-api.us-east-1.amazonaws.com/Prod/client-data
https://def456ghi7.execute-api.us-east-1.amazonaws.com/Prod/retrieve
https://jkl789mno0.execute-api.us-east-1.amazonaws.com/Prod/post-call
```

**Action Required:**
1. Capture new URLs from CloudFormation outputs
2. Update ElevenLabs webhook configurations
3. Update any test scripts or documentation with new URLs
4. Update `.env` file with new URLs

## Migration Checklist

- [ ] Backup current `.env` file and test scripts
- [ ] Run `sam build --use-container`
- [ ] Deploy with new stack name: `--stack-name elevenlabs-agentic-memory-stack`
- [ ] Include `--capabilities CAPABILITY_NAMED_IAM` flag
- [ ] Capture new API endpoint URLs from outputs
- [ ] Update `.env` file with new URLs:
  ```bash
  ELEVENLABS_CLIENT_DATA_URL=https://new-id.execute-api.us-east-1.amazonaws.com/Prod/client-data
  ELEVENLABS_POST_CALL_URL=https://new-id.execute-api.us-east-1.amazonaws.com/Prod/post-call
  ELEVENLABS_RETRIEVE_URL=https://new-id.execute-api.us-east-1.amazonaws.com/Prod/retrieve
  ```
- [ ] Update ElevenLabs agent webhooks:
  - [ ] Conversation Initiation webhook → New ClientData URL
  - [ ] Agent tool endpoint → New Retrieve URL
  - [ ] Post-call webhook → New PostCall URL
- [ ] Run test scripts to verify:
  - [ ] `test_clientdata.py`
  - [ ] `test_postcall.py`
  - [ ] `test_s3_storage.py`
- [ ] Monitor CloudWatch logs for errors
- [ ] Verify S3 storage still working
- [ ] Test with real ElevenLabs call
- [ ] Delete old `sam-app` stack (optional, after verification)

## Rollback Plan

If issues occur with new deployment:

### Option 1: Keep Old Stack Running
```bash
# Old stack is still functional at sam-app
# Just update ElevenLabs to point back to old URLs
```

### Option 2: Delete New Stack and Redeploy Old
```bash
# Delete new stack
aws cloudformation delete-stack --stack-name elevenlabs-agentic-memory-stack

# Redeploy old stack (revert template.yaml changes first)
sam deploy --stack-name sam-app
```

## Benefits of New Naming Convention

✅ **Consistency**: All resources follow same `elevenlabs-agentic-memory-*` pattern  
✅ **Clarity**: Resource purpose clear from name (client-data, search-data, post-call)  
✅ **Organization**: Easy to find related resources in AWS Console  
✅ **Professional**: Production-ready naming convention  
✅ **Searchability**: Filter by prefix in AWS Console  
✅ **Documentation**: Names match documentation and guides  

## Notes

- **S3 Bucket**: Already follows convention, no changes needed
- **Lambda Layer**: Keeps `AgenticMemoriesLambdaLayer` name (internal resource)
- **IAM Role**: Now has explicit name `AgenticMemoriesLambdaRole`
- **Resource IDs**: CloudFormation logical IDs remain the same for compatibility

## Support

If you encounter issues during migration:

1. Check CloudFormation events: 
   ```bash
   aws cloudformation describe-stack-events --stack-name elevenlabs-agentic-memory-stack
   ```

2. Review Lambda logs for errors

3. Verify IAM permissions include `iam:CreateRole` with named resources

4. Ensure `CAPABILITY_NAMED_IAM` is included in deploy command

## Summary

The template has been updated with consistent AWS resource naming. Deploy with `--stack-name elevenlabs-agentic-memory-stack` and `--capabilities CAPABILITY_NAMED_IAM` to use the new naming convention. Update ElevenLabs webhooks with the new API URLs after deployment.
