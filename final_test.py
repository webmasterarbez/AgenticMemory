#!/usr/bin/env python3
import json, time, hmac, hashlib, subprocess

# Load env
env = {}
for line in open('.env'):
    if '=' in line and not line.startswith('#'):
        k, v = line.strip().split('=', 1)
        env[k] = v

# Load payload
with open('elevenlabs_post_call_payload.json') as f:
    payload = json.load(f)

# Create signature
payload_json = json.dumps(payload, separators=(',', ':'))
timestamp = str(int(time.time()))
to_sign = f"{timestamp}.{payload_json}"
sig = hmac.new(env['ELEVENLABS_HMAC_KEY'].encode(), to_sign.encode(), hashlib.sha256).hexdigest()
full_sig = f"t={timestamp},v0={sig}"

print("Sending POST request...")
result = subprocess.run([
    'curl', '-X', 'POST', env['ELEVENLABS_POST_CALL_URL'],
    '-H', 'Content-Type: application/json',
    '-H', f'ElevenLabs-Signature: {full_sig}',
    '-d', payload_json,
    '-s', '-w', '\nHTTP: %{http_code}\n'
], capture_output=True, text=True, timeout=30)

print(result.stdout)
print("\nWaiting 10 seconds...")
time.sleep(10)

print("\nChecking logs...")
logs = subprocess.run([
    'aws', 'logs', 'tail', '/aws/lambda/AgenticMemoriesPostCall',
    '--since', '1m', '--format', 'short'
], capture_output=True, text=True, timeout=20)

for line in logs.stdout.split('\n'):
    if any(x in line for x in ['Processing', 'Stored', 'ERROR', 'Missing', 'caller_id']):
        print(line)

print("\n✅ Done! Check above for 'Stored factual' and 'Stored semantic' messages")
