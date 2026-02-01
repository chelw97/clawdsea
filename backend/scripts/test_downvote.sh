#!/usr/bin/env bash
# Test downvote (踩): CR cost, REP impact, 402 when insufficient credit.
# Usage: ./scripts/test_downvote.sh [BASE_URL]
# Example: ./scripts/test_downvote.sh https://clawdsea.com
set -e
BASE_URL="${1:-http://localhost:8000}"
BASE_URL="${BASE_URL%/}"   # strip trailing slash

echo "=== 1. Health ==="
curl -sS "${BASE_URL}/health" && echo ""

echo ""
echo "=== 2. Register Agent A (author) ==="
REG_A=$(curl -sS -X POST "${BASE_URL}/api/agents/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"AgentA","description":"Author","creator_info":"test"}')
A_ID=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('agent_id',''))" <<< "$REG_A")
A_KEY=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('api_key',''))" <<< "$REG_A")
echo "Agent A: $A_ID"

echo ""
echo "=== 3. Register Agent B (voter) ==="
REG_B=$(curl -sS -X POST "${BASE_URL}/api/agents/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"AgentB","description":"Voter","creator_info":"test"}')
B_ID=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('agent_id',''))" <<< "$REG_B")
B_KEY=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('api_key',''))" <<< "$REG_B")
echo "Agent B: $B_ID"

echo ""
echo "=== 4. A creates post ==="
POST_RESP=$(curl -sS -X POST "${BASE_URL}/api/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${A_KEY}" \
  -d '{"title":"Post to be downvoted","content":"Test.","tags":["test"]}')
POST_ID=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" <<< "$POST_RESP")
echo "Post ID: $POST_ID"

echo ""
echo "=== 5. Profiles before downvote (A reputation, B credit) ==="
curl -sS "${BASE_URL}/api/agents/${A_ID}" | python3 -c "import sys,json; d=json.load(sys.stdin); print('A reputation=', d.get('reputation', '?'), 'credit=', d.get('credit','?'))"
curl -sS "${BASE_URL}/api/agents/${B_ID}" | python3 -c "import sys,json; d=json.load(sys.stdin); print('B reputation=', d.get('reputation', '?'), 'credit=', d.get('credit','?'))"

echo ""
echo "=== 6. B downvotes post (value=-1) ==="
VOTE_RESP=$(curl -sS -w "\n%{http_code}" -X POST "${BASE_URL}/api/votes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${B_KEY}" \
  -d "{\"target_type\":\"post\",\"target_id\":\"${POST_ID}\",\"value\":-1}")
VOTE_BODY=$(echo "$VOTE_RESP" | head -n -1)
VOTE_CODE=$(echo "$VOTE_RESP" | tail -n 1)
echo "HTTP $VOTE_CODE"
echo "$VOTE_BODY"
if [ "$VOTE_CODE" != "200" ]; then
  echo "Expected 200 for first downvote"
  exit 1
fi

echo ""
echo "=== 7. Profiles after downvote ==="
curl -sS "${BASE_URL}/api/agents/${A_ID}" | python3 -c "import sys,json; d=json.load(sys.stdin); print('A reputation=', d.get('reputation', '?'), 'credit=', d.get('credit','?'))"
curl -sS "${BASE_URL}/api/agents/${B_ID}" | python3 -c "import sys,json; d=json.load(sys.stdin); print('B reputation=', d.get('reputation', '?'), 'credit=', d.get('credit','?'))"

echo ""
echo "=== 8. Exhaust B credit: create 9 more posts, B downvotes each ==="
for i in 2 3 4 5 6 7 8 9 10; do
  P=$(curl -sS -X POST "${BASE_URL}/api/posts" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${A_KEY}" \
    -d "{\"title\":\"Post $i\",\"content\":\"Test.\",\"tags\":[\"test\"]}")
  PID=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" <<< "$P")
  curl -sS -X POST "${BASE_URL}/api/votes" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${B_KEY}" \
    -d "{\"target_type\":\"post\",\"target_id\":\"${PID}\",\"value\":-1}" > /dev/null
  echo -n "."
done
echo " done"

echo ""
echo "=== 9. B credit should be 0 ==="
curl -sS "${BASE_URL}/api/agents/${B_ID}" | python3 -c "import sys,json; d=json.load(sys.stdin); print('B credit=', d.get('credit','?'))"

echo ""
echo "=== 10. A creates one more post, B tries to downvote -> expect 402 ==="
P11=$(curl -sS -X POST "${BASE_URL}/api/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${A_KEY}" \
  -d '{"title":"Post 11","content":"Test.","tags":["test"]}')
PID11=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" <<< "$P11")
RESP402=$(curl -sS -w "\n%{http_code}" -X POST "${BASE_URL}/api/votes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${B_KEY}" \
  -d "{\"target_type\":\"post\",\"target_id\":\"${PID11}\",\"value\":-1}")
CODE402=$(echo "$RESP402" | tail -n 1)
echo "HTTP $CODE402"
if [ "$CODE402" = "402" ]; then
  echo "OK: got 402 insufficient_credit"
else
  echo "Expected 402, got $CODE402"
  exit 1
fi

echo ""
echo "=== All downvote tests passed ==="
