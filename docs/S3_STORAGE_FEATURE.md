# S3 Storage Feature - Post-Call Data Persistence

## Overview

The AgenticMemory system now saves all post-call webhook payloads to Amazon S3 for long-term storage and analysis. This feature automatically stores both the complete conversation transcript (JSON) and the audio recording (MP3) in an organized, searchable structure.

## Architecture

### S3 Bucket

**Bucket Name:** `elevenlabs-agentic-memory-{AWS::AccountId}-{AWS::Region}`

**Example:** `elevenlabs-agentic-memory-424875385161-us-east-1`

**Key Features:**
- **Versioning:** Enabled (keeps history of all changes)
- **Public Access:** Blocked (all files are private)
- **Lifecycle Policy:** Automatic cost optimization
  - 30 days: Transition to Standard-IA (Infrequent Access)
  - 90 days: Transition to Glacier (long-term archive)

### Directory Structure

Files are organized by caller's phone number (external_number) and conversation ID:

```
s3://elevenlabs-agentic-memory-{AccountId}-{Region}/
├── 15074595005/                              # Caller's phone (+ removed)
│   ├── conv_01jxd5y165f62a0v7gtr6bkg56.json  # Conversation transcript
│   └── conv_01jxd5y165f62a0v7gtr6bkg56.mp3   # Audio recording
├── 16129782029/
│   ├── conv_01jxabcdefghijk1234567890.json
│   └── conv_01jxabcdefghijk1234567890.mp3
└── ...
```

**Directory Naming:** Phone numbers have the leading `+` removed (e.g., `+15074595005` becomes `15074595005`)

**File Naming Convention:**
- JSON: `{conversation_id}.json`
- MP3: `{conversation_id}.mp3`

## Stored Data

### JSON File Content

The complete ElevenLabs post-call webhook payload, including:

- **Conversation Metadata:**
  - `conversation_id`: Unique conversation identifier
  - `agent_id`: ElevenLabs agent identifier
  - `status`: Call completion status
  - `metadata`: Call metadata (duration, phone details, etc.)

- **Transcript:**
  - Full message-by-message conversation
  - Role (agent/user), content, timestamps
  - Tool calls and results
  - LLM usage metrics
  - Conversation turn metrics

- **Analysis:**
  - Call summary
  - Evaluation criteria results
  - Performance metrics

**Example:**
```json
{
  "agent_id": "agent_01jxbrc1trfxev5sdp5xk4ra67",
  "conversation_id": "conv_01jxd5y165f62a0v7gtr6bkg56",
  "status": "done",
  "metadata": {
    "phone_call": {
      "external_number": "+15074595005",
      "call_duration_secs": 450
    }
  },
  "transcript": [...],
  "analysis": {...}
}
```

### MP3 File Content

The complete audio recording of the conversation, decoded from the base64 `full_audio` field in the webhook payload.

- **Format:** MP3 (audio/mpeg)
- **Content:** Full conversation audio from ElevenLabs
- **Source:** Decoded from `payload.full_audio` (base64)

**Note:** MP3 files are only saved if the `full_audio` field is present in the webhook payload.

## Implementation Details

### Lambda Function Modifications

The `AgenticMemoriesPostCall` Lambda function (`src/post_call/handler.py`) was enhanced with:

1. **S3 Client Initialization:**
   ```python
   import boto3
   s3_client = boto3.client('s3')
   S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
   ```

2. **save_to_s3() Function:**
   - Extracts `external_number` and `conversation_id` from payload
   - Sanitizes phone number (removes `+` prefix)
   - Saves JSON with `ContentType: application/json`
   - Decodes base64 audio and saves MP3 with `ContentType: audio/mpeg`
   - Includes metadata (external_number, conversation_id, timestamp)

3. **Integration in lambda_handler:**
   ```python
   # After extracting caller_id, before storing memories
   try:
       save_to_s3(caller_id, conversation_id, payload)
   except Exception as e:
       logger.error(f"Error saving to S3: {str(e)}", exc_info=True)
       # Continue processing - S3 failure shouldn't block memory storage
   ```

### IAM Permissions

The Lambda execution role (`AgenticMemoriesLambdaRole`) was updated with S3 access:

```yaml
Policies:
  - PolicyName: S3PostCallDataAccess
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Action:
            - s3:PutObject
            - s3:PutObjectAcl
            - s3:GetObject
          Resource: !Sub '${ElevenLabsAgenticMemoryBucket.Arn}/*'
```

### Environment Variables

The PostCall Lambda function includes:

```yaml
Environment:
  Variables:
    S3_BUCKET_NAME: !Ref ElevenLabsAgenticMemoryBucket
    # ... other variables
```

## Testing

### Test Script

**Location:** `scripts/test_s3_storage.py`

**Features:**
- Sends test post-call webhook with HMAC signature
- Waits for async processing (5 seconds)
- Verifies JSON file in S3
- Verifies MP3 file in S3 (if present)
- Displays file metadata (size, content-type, timestamps)

**Usage:**
```bash
# Ensure .env has required variables:
# - ELEVENLABS_POST_CALL_URL
# - ELEVENLABS_HMAC_KEY
# - S3_BUCKET_NAME

cd /home/ubuntu/home/ubuntu/proj/claude/AgenticMemory
/home/ubuntu/home/ubuntu/proj/claude/AgenticMemory/test_env/bin/python scripts/test_s3_storage.py
```

**Expected Output:**
```
======================================================================
S3 STORAGE TEST - Post-Call Webhook
======================================================================
📂 Loading test payload: .../conv_01jxd5y165f62a0v7gtr6bkg56.json
📞 Conversation ID: conv_01jxd5y165f62a0v7gtr6bkg56
📱 External Number: +15074595005
🎵 Audio present: Yes/No

STEP 1: Send webhook to PostCall endpoint
✅ Webhook sent: Success

STEP 2: Verify files in S3
✅ JSON file found: 144755 bytes
⚠️  MP3 file not found (may not be in test payload)

TEST SUMMARY
✅ Webhook sent: Success
✅ JSON file in S3: Success
⚠️  MP3 file in S3: Not found
```

### Manual Verification

**List files in S3:**
```bash
aws s3 ls s3://elevenlabs-agentic-memory-424875385161-us-east-1/
aws s3 ls s3://elevenlabs-agentic-memory-424875385161-us-east-1/16129782029/
```

**Download file:**
```bash
aws s3 cp s3://elevenlabs-agentic-memory-424875385161-us-east-1/16129782029/conv_01jxd5y165f62a0v7gtr6bkg56.json ./downloaded.json
```

**View file metadata:**
```bash
aws s3api head-object \
  --bucket elevenlabs-agentic-memory-424875385161-us-east-1 \
  --key 16129782029/conv_01jxd5y165f62a0v7gtr6bkg56.json
```

## Monitoring

### CloudWatch Logs

The PostCall Lambda logs all S3 operations:

```bash
aws logs tail /aws/lambda/AgenticMemoriesPostCall --follow
```

**Key log messages:**
- `Saving JSON to S3: s3://{bucket}/{key}` - JSON save initiated
- `Successfully saved JSON for conversation {id}` - JSON save completed
- `Saving MP3 to S3: s3://{bucket}/{key} ({bytes} bytes)` - MP3 save initiated
- `Successfully saved MP3 for conversation {id}` - MP3 save completed
- `No full_audio field found` - MP3 not present in payload
- `Error saving to S3: {error}` - S3 operation failed

### S3 Metrics

Monitor S3 usage in AWS Console:
- **Storage:** CloudWatch → S3 → BucketSizeBytes
- **Requests:** CloudWatch → S3 → AllRequests, PutRequests
- **Cost:** AWS Cost Explorer → S3 service costs

## Cost Optimization

### Lifecycle Policy

The bucket automatically transitions files to cheaper storage classes:

| Age | Storage Class | Cost (per GB/month) | Use Case |
|-----|---------------|---------------------|----------|
| 0-30 days | Standard | $0.023 | Recent calls, frequent access |
| 30-90 days | Standard-IA | $0.0125 | Older calls, occasional access |
| 90+ days | Glacier | $0.004 | Archive, rare access |

**Example Cost Calculation:**
- 1,000 calls/month
- Average JSON: 150KB
- Average MP3: 2MB (if present)
- Total per call: ~2.15MB
- Monthly storage: ~2.15GB

**Monthly Cost:**
- Month 1-2: 2.15GB × $0.023 = $0.05
- Month 3-4: Add 2.15GB × $0.0125 = $0.027 (cumulative $0.077)
- Month 5+: Add 2.15GB × $0.004 = $0.009 (cumulative $0.086)

**Annual Cost:** ~$1.00 for 1,000 calls/month

### Optimization Tips

1. **Remove audio if not needed:** Modify handler to skip MP3 storage
2. **Compress JSON:** Use gzip compression (reduces size by ~80%)
3. **Shorter retention:** Adjust lifecycle rules to move to Glacier sooner
4. **Selective storage:** Only store calls meeting certain criteria

## Error Handling

### S3 Failures

S3 save errors are logged but **do not block memory storage**:

```python
try:
    save_to_s3(caller_id, conversation_id, payload)
except Exception as e:
    logger.error(f"Error saving to S3: {str(e)}", exc_info=True)
    # Continue processing - memory storage proceeds normally
```

**Common Errors:**
- **NoSuchBucket:** Bucket doesn't exist (check deployment)
- **AccessDenied:** IAM permissions missing (check role policy)
- **ServiceUnavailable:** S3 temporary issue (retry automatically)
- **Base64DecodeError:** Invalid audio data (logged, JSON still saved)

### Retry Logic

The Lambda execution model provides automatic retries:
- **Async invocation:** 2 automatic retries on failure
- **S3 operations:** boto3 includes built-in exponential backoff
- **Timeout:** 120 seconds allows for large file uploads

## Data Retention

### Current Policy

- **Versioning:** Enabled - all file versions are kept
- **Deletion:** Manual only - no automatic deletion
- **Lifecycle:** Transitions to cheaper storage, but never deleted

### Future Enhancements

Consider adding:
- **Expiration rule:** Delete files older than X years
- **Intelligent-Tiering:** Auto-optimize based on access patterns
- **Glacier Deep Archive:** Even cheaper for rarely accessed data

## Security

### Access Control

- **Public Access:** Blocked at bucket level
- **IAM Policy:** Lambda role has minimal required permissions (PutObject, GetObject)
- **Encryption:** Uses AWS-managed encryption (SSE-S3) by default
- **Bucket Policy:** None (relies on IAM policies only)

### Data Privacy

- **Personal Data:** Contains phone numbers, conversation content
- **Compliance:** Consider GDPR, CCPA requirements
- **Retention:** Implement data deletion on user request
- **Access Logs:** Enable S3 access logging for audit trail

### Recommendations

1. **Enable S3 Object Lock:** Prevent accidental deletions
2. **Enable CloudTrail:** Track all S3 API calls
3. **Add bucket policy:** Restrict access to specific AWS accounts
4. **Customer-managed encryption:** Use KMS for enhanced control

## Integration with ElevenLabs

### Workflow

1. **Call Completion:** ElevenLabs agent finishes conversation
2. **Webhook Trigger:** ElevenLabs sends POST to `/post-call` endpoint
3. **HMAC Validation:** Lambda verifies webhook signature
4. **Parallel Processing:**
   - **S3 Storage:** Save JSON + MP3 to S3
   - **Memory Storage:** Save to Mem0 (factual + semantic)
5. **Response:** Return 200 OK immediately (async processing)

### Payload Requirements

The webhook payload must include:

**Required:**
- `conversation_id`: Conversation identifier
- `metadata.phone_call.external_number`: Caller's phone number
- `transcript`: Array of conversation messages

**Optional:**
- `full_audio`: Base64-encoded MP3 audio (for MP3 storage)
- `analysis`: Call summary and evaluation

### ElevenLabs Configuration

No additional configuration required in ElevenLabs dashboard. The existing post-call webhook automatically provides all necessary data.

## Querying Stored Data

### AWS CLI Examples

**List all callers:**
```bash
aws s3 ls s3://elevenlabs-agentic-memory-424875385161-us-east-1/ | grep "PRE"
```

**List calls for specific caller:**
```bash
aws s3 ls s3://elevenlabs-agentic-memory-424875385161-us-east-1/16129782029/
```

**Download specific conversation:**
```bash
aws s3 cp s3://elevenlabs-agentic-memory-424875385161-us-east-1/16129782029/conv_01jxd5y165f62a0v7gtr6bkg56.json ./
```

**Search JSON content (requires download):**
```bash
aws s3 cp s3://elevenlabs-agentic-memory-424875385161-us-east-1/16129782029/conv_01jxd5y165f62a0v7gtr6bkg56.json - | jq '.transcript[] | select(.role=="user") | .message'
```

### Boto3 Examples

**List conversations:**
```python
import boto3

s3 = boto3.client('s3')
bucket = 'elevenlabs-agentic-memory-424875385161-us-east-1'

# List all JSON files
response = s3.list_objects_v2(Bucket=bucket, Prefix='16129782029/')
for obj in response.get('Contents', []):
    if obj['Key'].endswith('.json'):
        print(f"{obj['Key']} - {obj['Size']} bytes")
```

**Download and parse:**
```python
import json

# Download JSON
response = s3.get_object(
    Bucket=bucket,
    Key='16129782029/conv_01jxd5y165f62a0v7gtr6bkg56.json'
)
conversation = json.loads(response['Body'].read())

# Extract user messages
user_messages = [
    msg['message'] 
    for msg in conversation['transcript'] 
    if msg['role'] == 'user'
]
```

## Future Enhancements

### Planned Features

1. **Metadata Indexing:**
   - Store searchable metadata in DynamoDB
   - Enable queries by date, duration, caller, agent, etc.
   - Build analytics dashboard

2. **Automatic Transcription:**
   - Use AWS Transcribe for audio-to-text
   - Store both original audio and transcript
   - Enable full-text search

3. **Data Analytics:**
   - Aggregate statistics across calls
   - Identify trends and patterns
   - Generate reports and insights

4. **API Access:**
   - Build REST API for querying stored data
   - Enable external integrations
   - Support webhook for real-time notifications

5. **Enhanced Security:**
   - Customer-managed KMS encryption
   - VPC endpoints for private S3 access
   - Fine-grained access controls

### Implementation Priority

**High Priority:**
- Metadata indexing (DynamoDB)
- Search API endpoint
- Cost monitoring dashboard

**Medium Priority:**
- Automatic transcription
- Analytics reports
- Data export tools

**Low Priority:**
- Advanced encryption
- VPC endpoints
- Multi-region replication

## Deployment History

**Version 1.0 (2025-10-01):**
- Initial S3 storage implementation
- Automatic JSON and MP3 saving
- Lifecycle policy for cost optimization
- IAM permissions and environment variables
- Test script and documentation

## Support

### Troubleshooting

**Q: Files not appearing in S3?**
- Check Lambda logs for errors
- Verify IAM permissions
- Ensure bucket exists
- Check external_number extraction

**Q: MP3 files missing?**
- Verify `full_audio` field in webhook payload
- Check Lambda logs for base64 decode errors
- Audio is optional - JSON always saved

**Q: High S3 costs?**
- Review lifecycle policy
- Consider removing MP3 storage
- Compress JSON files
- Implement data retention limits

### Getting Help

- **Documentation:** `/docs/` directory
- **Logs:** CloudWatch Logs for Lambda function
- **AWS Support:** For S3 or Lambda issues
- **GitHub Issues:** For feature requests

## Summary

The S3 storage feature provides **automatic, organized, cost-effective long-term storage** of all ElevenLabs voice agent conversations. Files are stored in a logical directory structure (by phone number and conversation ID), with automatic lifecycle management to minimize costs while preserving data indefinitely. The implementation is robust, with proper error handling, IAM security, and comprehensive monitoring.
