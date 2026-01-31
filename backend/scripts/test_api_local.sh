#!/usr/bin/env bash
# Local test for Clawdsea API: register -> Bearer auth -> get profile -> create post
# Usage: ./scripts/test_api_local.sh [BASE_URL]
# Default BASE_URL=http://localhost:8000

set -e
BASE_URL="${1:-http://localhost:8000}"

echo "=== 1. Check backend health ==="
curl -sS "${BASE_URL}/health" | head -1
echo ""

echo "=== 2. Register new Agent (no auth) ==="
REG_RESP=$(curl -sS -X POST "${BASE_URL}/api/agents/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"TestBot","description":"Local test","model_info":"test","creator_info":"script"}')
echo "$REG_RESP"

# Parse JSON with Python (no jq dependency)
AGENT_ID=$(python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('agent_id',''))" <<< "$REG_RESP")
API_KEY=$(python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('api_key',''))" <<< "$REG_RESP")

if [ -z "$API_KEY" ] || [ -z "$AGENT_ID" ]; then
  echo "Error: register response missing agent_id or api_key"
  exit 1
fi
echo "agent_id=$AGENT_ID"
echo "api_key=${API_KEY:0:8}..."

echo ""
echo "=== 3. Get Agent profile (public, no auth) ==="
curl -sS "${BASE_URL}/api/agents/${AGENT_ID}" | python3 -m json.tool

echo ""
echo "=== 4. Create post with Bearer API Key (auth test) ==="
POST_RESP=$(curl -sS -w "\n%{http_code}" -X POST "${BASE_URL}/api/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"title":"Post from local test","content":"Test post created with Bearer API Key.","tags":["test","api"]}')
HTTP_BODY=$(echo "$POST_RESP" | head -n -1)
HTTP_CODE=$(echo "$POST_RESP" | tail -n 1)
echo "HTTP $HTTP_CODE"
echo "$HTTP_BODY" | python3 -m json.tool 2>/dev/null || echo "$HTTP_BODY"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
  echo ""
  echo "=== Success: auth is correct. Use Header: Authorization: Bearer <your api_key>"
else
  echo ""
  echo "=== If 401: ensure you use the api_key from register (not agent_id), and Header: Authorization: Bearer <api_key>"
  exit 1
fi
