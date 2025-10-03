# Final AWS Resource Naming Convention

## Complete Resource Names

All resources now follow the `elevenlabs-agentic-memory-*` naming pattern:

### CloudFormation Stack
```
elevenlabs-agentic-memory-stack
```

### IAM Role  
```
elevenlabs-agentic-memory-role
```

### Lambda Functions
```
elevenlabs-agentic-memory-lambda-function-client-data
elevenlabs-agentic-memory-lambda-function-search-data
elevenlabs-agentic-memory-lambda-function-post-call
```

### CloudWatch Log Groups
```
/aws/lambda/elevenlabs-agentic-memory-log-client-data
/aws/lambda/elevenlabs-agentic-memory-log-search-data
/aws/lambda/elevenlabs-agentic-memory-log-post-call
```

### API Gateways
```
elevenlabs-agentic-memory-api-gateway-client-data
elevenlabs-agentic-memory-api-gateway-search-data
elevenlabs-agentic-memory-api-gateway-post-call
```

### S3 Bucket
```
elevenlabs-agentic-memory-424875385161-us-east-1
```
(Already correct - includes AccountId and Region for global uniqueness)

### Lambda Layer
```
AgenticMemoriesLambdaLayer
```
(Internal resource - kept as is for compatibility)

## Deployment Command

```bash
sam build --use-container

sam deploy \
  --stack-name elevenlabs-agentic-memory-stack \
  --region us-east-1 \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    Mem0ApiKey=$MEM0_API_KEY \
    Mem0OrgId=$MEM0_ORG_ID \
    Mem0ProjectId=$MEM0_PROJECT_ID \
    ElevenLabsWorkspaceKey=$ELEVENLABS_WORKSPACE_KEY \
    ElevenLabsHmacKey=$ELEVENLABS_HMAC_KEY
```

## Naming Pattern Rules

1. **Prefix**: All resources start with `elevenlabs-agentic-memory`
2. **Separator**: Use hyphens (`-`) not underscores
3. **Resource Type**: Descriptive type (lambda-function, api-gateway, log, role)
4. **Function**: Descriptive purpose (client-data, search-data, post-call)
5. **S3 Bucket**: Append AccountId-Region for global uniqueness

## Benefits

✅ **Consistency**: All resources follow same pattern  
✅ **Searchable**: Easy to filter by `elevenlabs-agentic-memory*` in AWS Console  
✅ **Self-Documenting**: Names explain purpose  
✅ **Professional**: Production-ready convention  
✅ **Organized**: Resources grouped visually in AWS Console  

## Status

- [x] Template updated with new names
- [x] Documentation updated
- [ ] Deployed to AWS (pending user decision)

## Next Steps

**Option A**: Keep current naming (revert template changes)  
**Option B**: Deploy with new naming (requires fresh deployment)

See `docs/NAMING_UPDATE_STATUS.md` for detailed recommendations.
