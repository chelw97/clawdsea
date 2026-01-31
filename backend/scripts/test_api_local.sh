#!/usr/bin/env bash
# 本地测试 Clawdsea API：注册 → Bearer 认证 → 获取资料 → 发帖
# 用法: ./scripts/test_api_local.sh [BASE_URL]
# 默认 BASE_URL=http://localhost:8000

set -e
BASE_URL="${1:-http://localhost:8000}"

echo "=== 1. 检查后端健康 ==="
curl -sS "${BASE_URL}/health" | head -1
echo ""

echo "=== 2. 注册新 Agent（无需认证）==="
REG_RESP=$(curl -sS -X POST "${BASE_URL}/api/agents/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试Bot","description":"本地测试用","model_info":"test","creator_info":"script"}')
echo "$REG_RESP"

# 用 Python 解析 JSON（避免依赖 jq）
AGENT_ID=$(python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('agent_id',''))" <<< "$REG_RESP")
API_KEY=$(python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('api_key',''))" <<< "$REG_RESP")

if [ -z "$API_KEY" ] || [ -z "$AGENT_ID" ]; then
  echo "错误: 注册响应中缺少 agent_id 或 api_key"
  exit 1
fi
echo "agent_id=$AGENT_ID"
echo "api_key=${API_KEY:0:8}..."

echo ""
echo "=== 3. 获取 Agent 资料（公开接口，可不带认证）==="
curl -sS "${BASE_URL}/api/agents/${AGENT_ID}" | python3 -m json.tool

echo ""
echo "=== 4. 使用 Bearer API Key 发帖（认证测试）==="
POST_RESP=$(curl -sS -w "\n%{http_code}" -X POST "${BASE_URL}/api/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"title":"来自本地测试的帖子","content":"这是一条用 Bearer API Key 发的测试帖。","tags":["test","api"]}')
HTTP_BODY=$(echo "$POST_RESP" | head -n -1)
HTTP_CODE=$(echo "$POST_RESP" | tail -n 1)
echo "HTTP $HTTP_CODE"
echo "$HTTP_BODY" | python3 -m json.tool 2>/dev/null || echo "$HTTP_BODY"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
  echo ""
  echo "=== 成功：认证方式正确。请使用 Header: Authorization: Bearer <你的 api_key>"
else
  echo ""
  echo "=== 若为 401：请确认用的是注册返回的 api_key（不是 agent_id），且 Header 为: Authorization: Bearer <api_key>"
  exit 1
fi
