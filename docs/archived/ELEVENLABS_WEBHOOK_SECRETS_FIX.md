# ElevenLabs Webhook Configuration Fix

## Problem Identified
Based on the CloudWatch logs and ElevenLabs documentation, the issue is that ElevenLabs is not sending the workspace key header correctly. The ElevenLabs documentation shows that custom headers need to be configured as "secrets" in their interface.

## Root Cause
ElevenLabs requires authentication headers to be configured as **secrets** in their settings, not just as regular headers. The workspace key needs to be:
1. Added as a **secret** in the ElevenLabs Settings page
2. Then mapped to a **header** in the webhook configuration

## Step-by-Step Fix

### Step 1: Add Workspace Key as Secret
1. Go to [ElevenLabs Agents Settings](https://elevenlabs.io/app/agents/settings)
2. In the "Secrets" section, add a new secret:
   - **Secret Name**: `WORKSPACE_KEY`
   - **Secret Value**: `wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70`

### Step 2: Configure Conversation Initiation Webhook
1. In the same settings page, find "Conversation Initiation Webhook"
2. Set the webhook URL: `https://idr7oxv9q6.execute-api.us-east-1.amazonaws.com/Prod/client-data`
3. **CRITICAL**: Click on the webhook to modify headers
4. Add header mapping:
   - **Header Name**: `X-Workspace-Key`
   - **Header Value**: Select the `WORKSPACE_KEY` secret from dropdown

### Step 3: Enable Webhook in Agent Security Settings
1. Go to your specific agent page: [ElevenLabs Agents](https://elevenlabs.io/app/agents/agents/)
2. Click on your memoir interviewer agent
3. Go to the **"Security"** tab
4. Enable **"Fetch conversation initiation data for inbound Twilio calls"**
5. Enable any overrides you want to allow (prompt, first_message, etc.)

### Step 4: Configure Webhook Payload
The webhook should send this payload format:
```json
{
  "caller_id": "{{system__caller_id}}",
  "agent_id": "{{system__agent_id}}"
}
```

Note: ElevenLabs automatically populates `{{system__caller_id}}` with the caller's phone number.

## Expected Webhook Request from ElevenLabs
After correct configuration, ElevenLabs will send:

**Headers:**
```
X-Workspace-Key: wsec_c345664e5d1cea8a9afe4750927861b65c6636b4267aef63448a73b5c9dbba70
Content-Type: application/json
```

**Body:**
```json
{
  "caller_id": "+16129782029",
  "agent_id": "agent_4301k6n146bgfs2tqtq5nhejw0r7"
}
```

## Expected Response to ElevenLabs
Your webhook should return:
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_id": "+16129782029",
    "memory_count": "4",
    "memory_summary": "User wants to update email address",
    "returning_caller": "yes",
    "caller_name": "Stefan"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "CALLER CONTEXT:\nThis caller has 4 previous interactions..."
      },
      "first_message": "Hello Stefan! I know you prefer email updates. How can I assist you today?"
    }
  }
}
```

## Verification Steps

### 1. Test the Configuration
After making the changes above, make a test call to +1 720 575 2470 from +1 612 978 2029.

### 2. Check CloudWatch Logs
Monitor the logs during the call:
```bash
aws logs tail /aws/lambda/elevenlabs-agentic-memory-lambda-function-client-data --follow
```

You should see:
- ✅ `Retrieving memories for user_id: +16129782029`
- ✅ `Retrieved 4 memories for +16129782029`
- ❌ No more "Invalid workspace key" errors

### 3. Verify Agent Response
The agent should greet you with:
> "Hello Stefan! I know you prefer email updates. How can I assist you today?"

This confirms that:
- The webhook is working
- Dynamic variables are populated
- Memory context is being used

## Common Configuration Mistakes

### ❌ Wrong: Setting header directly in webhook URL field
- Don't add headers to the URL or in a generic "headers" field

### ✅ Correct: Using secrets management
- Add workspace key as a secret first
- Map secret to header in webhook configuration

### ❌ Wrong: Not enabling security permissions
- The agent must have "Fetch conversation initiation data" enabled

### ✅ Correct: Enable in agent security settings
- Each agent needs this permission enabled individually

## Troubleshooting

If the issue persists after configuration:

1. **Double-check secret name**: Ensure the secret name exactly matches what you reference in headers
2. **Verify header mapping**: The header name must be exactly `X-Workspace-Key`
3. **Check agent permissions**: Security tab must have conversation initiation enabled
4. **Test with different phone number**: Try a new number to test first-time caller flow

## Support Resources

- [ElevenLabs Secrets Manager](https://elevenlabs.io/app/agents/settings)
- [Agent Security Settings](https://elevenlabs.io/app/agents/agents/)
- [Twilio Personalization Docs](https://elevenlabs.io/docs/agents-platform/customization/personalization/twilio-personalization)

The key insight is that ElevenLabs treats authentication headers as **secrets that need to be managed through their secure interface**, not as simple header key-value pairs.