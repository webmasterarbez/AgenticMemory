#!/bin/bash
# Quick wrapper script for testing PostCall endpoint
# Usage: ./test_postcall.sh [conversation_file.json]

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists (look in project root)
if [ -f ../.env ]; then
    echo -e "${GREEN}✅ Loading credentials from .env file${NC}"
    export $(grep -v '^#' ../.env | xargs)
elif [ -f .env ]; then
    echo -e "${GREEN}✅ Loading credentials from .env file${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found. You'll be prompted for credentials.${NC}"
    echo "   Create a .env file in project root with:"
    echo "   ELEVENLABS_POST_CALL_URL=https://..."
    echo "   ELEVENLABS_HMAC_KEY=wsec_..."
    echo ""
fi

# Get conversation file from argument or use default
if [ -n "$1" ]; then
    CONV_FILE="$1"
else
    CONV_FILE="conv_01jxd5y165f62a0v7gtr6bkg56.json"
fi

# Check if file exists (try current dir first, then test_data)
if [ -f "$CONV_FILE" ]; then
    FILE_PATH="$CONV_FILE"
elif [ -f "../test_data/$CONV_FILE" ]; then
    FILE_PATH="../test_data/$CONV_FILE"
    echo -e "${GREEN}📁 Found file in test_data directory${NC}"
else
    echo -e "${RED}❌ Error: File not found: $CONV_FILE${NC}"
    echo ""
    echo "Available conversation files in test_data/:"
    ls -1 ../test_data/conv_*.json 2>/dev/null | xargs -n1 basename || echo "  (none found)"
    exit 1
fi
CONV_FILE="$FILE_PATH"

echo -e "${GREEN}🚀 Testing PostCall with: $CONV_FILE${NC}"
echo ""

# Run the Python script
python3 test_postcall_with_file.py "$CONV_FILE"
TEST_EXIT_CODE=$?

echo ""
echo "=================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Test completed${NC}"
    echo ""
    echo "📊 Next steps:"
    echo "   1. Check logs:"
    echo "      aws logs tail /aws/lambda/AgenticMemoriesPostCall --since 5m --follow"
    echo ""
    echo "   2. Verify memories (extract caller_id from output above):"
    echo "      Use Retrieve endpoint or check Mem0 dashboard"
else
    echo -e "${YELLOW}⚠️  Test encountered an issue${NC}"
    echo ""
    echo "Common fixes:"
    echo "   - Timeout errors are normal (Lambda processes async)"
    echo "   - Check CloudWatch logs for actual processing status"
    echo "   - Verify credentials in .env or environment variables"
fi

echo "=================================="
