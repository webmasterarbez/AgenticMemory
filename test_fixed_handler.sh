#!/bin/bash
# Quick test of the fixed PostCall handler

# Read env vars
source .env

# Load payload
PAYLOAD=$(cat elevenlabs_post_call_payload.json)

# Create signature
TIMESTAMP=$(date +%s)
PAYLOAD_JSON=$(echo "$PAYLOAD" | jq -c .)
TO_SIGN="${TIMESTAMP}.${PAYLOAD_JSON}"
SIGNATURE=$(echo -n "$TO_SIGN" | openssl dgst -sha256 -hmac "$ELEVENLABS_HMAC_KEY" | cut -d' ' -f2)
FULL_SIG="t=${TIMESTAMP},v0=${SIGNATURE}"

echo "=== Testing Fixed PostCall Handler ==="
echo "Sending request..."

curl -X POST "$ELEVENLABS_POST_CALL_URL" \
  -H "Content-Type: application/json" \
  -H "ElevenLabs-Signature: $FULL_SIG" \
  -d "$PAYLOAD_JSON" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s

echo ""
echo "Waiting 8 seconds for processing..."
sleep 8

echo ""
echo "=== Recent Logs ==="
aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 1m --format short 2>&1 | grep -E "Processing|Stored|ERROR|Missing" | tail -10

