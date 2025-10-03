# AWS Resource Naming Update - Status & Recommendations

## Current Situation

The template has been updated with the new `elevenlabs-agentic-memory-*` naming **Template State**: Updated with new names (uncommitted)  
**Stack Name**: `elevenlabs-agentic-memory-stack` (new)  
**IAM Role**: `elevenlabs-agentic-memory-role` (new)  
**Deployment State**: Original `sam-app` stack still running with old names  
**Next Step**: Decide on Option A (revert) or Option B (fresh deploy)

**Recommendation**: Revert template changes and continue with current working system.ntion, but deployment encountered issues because:

1. **Renaming resources requires replacement** (creating new, deleting old)
2. **CloudFormation doesn't allow replacement** when `--disable-rollback` is enabled
3. **S3 bucket name conflict** when creating a new stack (bucket already exists)

## Deployment Attempts

### Attempt 1: New Stack (Failed)
```bash
sam deploy --stack-name AgenticMemoriesLambdaStack --capabilities CAPABILITY_NAMED_IAM
```
**Result**: ❌ Failed - S3 bucket `elevenlabs-agentic-memory-424875385161-us-east-1` already exists in old stack

### Attempt 2: Update Existing Stack (Failed)
```bash
sam deploy --stack-name sam-app --capabilities CAPABILITY_NAMED_IAM
```
**Result**: ❌ Failed - Replacement type updates not supported with disable-rollback

## Recommended Approach

### Option A: Keep Current Names (Easiest - RECOMMENDED)

**Why?** The current system is working perfectly. The naming isn't wrong, just different.

**Current Names:**
- Functions: `AgenticMemoriesClientData`, `AgenticMemoriesRetrieve`, `AgenticMemoriesPostCall`
- Logs: `/aws/lambda/AgenticMemoriesClientData`, etc.
- APIs: Auto-generated IDs (works fine)
- S3 Bucket: `elevenlabs-agentic-memory-424875385161-us-east-1` ✅ Already good!

**Action**: Revert template.yaml changes and continue with current naming.

```bash
git checkout template.yaml  # Revert changes
sam build && sam deploy     # Continue as normal
```

### Option B: Fresh Deployment with New Names (Clean Slate)

**Steps:**

1. **Backup current configuration:**
   ```bash
   # Save current API URLs
   aws cloudformation describe-stacks \
     --stack-name sam-app \
     --query 'Stacks[0].Outputs' > backup-urls.json
   ```

2. **Delete old stack:**
   ```bash
   aws cloudformation delete-stack --stack-name sam-app
   
   # Wait for completion (2-3 minutes)
   aws cloudformation wait stack-delete-complete --stack-name sam-app
   ```

3. **Deploy with new names:**
   ```bash
   sam build --use-container
   
   sam deploy \
     --stack-name elevenlabs-agentic-memory-stack \
     --capabilities CAPABILITY_NAMED_IAM \
     --parameter-overrides \
       Mem0ApiKey=$MEM0_API_KEY \
       Mem0OrgId=$MEM0_ORG_ID \
       Mem0ProjectId=$MEM0_PROJECT_ID \
       ElevenLabsWorkspaceKey=$ELEVENLABS_WORKSPACE_KEY \
       ElevenLabsHmacKey=$ELEVENLABS_HMAC_KEY
   ```

4. **Update ElevenLabs webhooks** with new API URLs

5. **Update .env file** with new URLs

**Pros:**
- ✅ Clean naming convention
- ✅ Fresh start
- ✅ No legacy cruft

**Cons:**
- ❌ Downtime during migration (~5 minutes)
- ❌ Need to update ElevenLabs webhooks
- ❌ API URLs will change
- ❌ Mem0 data remains (tied to phone numbers, not stack)

### Option C: Gradual Migration (Complex)

Create new stack alongside old, migrate traffic, then delete old:

1. Deploy new stack with different S3 bucket name temporarily
2. Test new stack
3. Update ElevenLabs to new stack
4. Delete old stack
5. Update S3 bucket name in new stack

**Not recommended** - too complex for minor naming improvement

## My Recommendation: Option A (Keep Current Names)

**Reasoning:**

1. **System is Production-Ready**: Everything works perfectly as-is
2. **No Downtime**: Keep services running without interruption  
3. **No Risk**: Avoid potential migration issues
4. **S3 Already Correct**: Bucket already follows convention
5. **Functions Work Fine**: Lambda function names don't affect functionality
6. **Internal References**: Most users interact via API URLs, not resource names

### What's Already Good

✅ **S3 Bucket**: `elevenlabs-agentic-memory-424875385161-us-east-1` (perfect!)  
✅ **Functionality**: All endpoints working  
✅ **Documentation**: Comprehensive guides created  
✅ **Testing**: Test scripts validated  
✅ **Monitoring**: CloudWatch logs configured  

### What Would Change (Not Critical)

- Lambda function names in AWS Console
- CloudWatch log group names
- API Gateway names
- IAM role name

**Impact**: Minimal - these are internal AWS identifiers

## If You Still Want New Names

I recommend **Option B** (fresh deployment) but **only if**:

- [ ] You're okay with 5-10 minutes of downtime
- [ ] You can update ElevenLabs webhooks immediately
- [ ] You have backups of current configuration
- [ ] You're comfortable with the migration process

### Pre-Migration Checklist

- [ ] Backup `.env` file
- [ ] Save current API URLs
- [ ] Export stack outputs
- [ ] Notify any users of planned downtime
- [ ] Test locally first with `sam local`
- [ ] Have rollback plan ready

## Conclusion

**I recommend keeping the current naming** (Option A). The system is working perfectly, and the naming is consistent enough. The S3 bucket already follows the convention, which is the most visible resource.

If you absolutely need the new names, I can help you execute Option B (fresh deployment), but be prepared for the downtime and webhook updates.

## Current Status

**Template State**: Updated with new names (uncommitted)  
**Deployment State**: Original `sam-app` stack still running with old names  
**Next Step**: Decide on Option A (revert) or Option B (fresh deploy)

**Recommendation**: Revert template changes and continue with current working system.

```bash
# To revert and continue:
git checkout template.yaml
sam build && sam deploy
```

**Your choice**: What would you like to do?

1. **Keep current names** - Quick, safe, zero downtime
2. **Deploy with new names** - Clean naming, requires migration
3. **Something else** - Let me know your preference
