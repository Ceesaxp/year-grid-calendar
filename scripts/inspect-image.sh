#!/bin/bash

echo "=== Inspecting Docker Image: ceesaxp/year-grid-calendar:latest ==="
echo ""

# Pull the image
echo "📥 Pulling image from Docker Hub..."
docker pull ceesaxp/year-grid-calendar:latest --no-cache

echo ""
echo "🔍 Starting temporary container to inspect..."
CONTAINER_ID=$(docker run -d -e BASE_URL=https://test.example.com ceesaxp/year-grid-calendar:latest)
sleep 2

echo ""
echo "1️⃣ Checking robots() function code in image:"
echo "=============================================="
docker exec $CONTAINER_ID grep -A 10 "async def robots" /app/web/app.py | head -15

echo ""
echo "2️⃣ Checking if it's the OLD code or NEW code:"
echo "=============================================="
if docker exec $CONTAINER_ID grep -A 5 "async def robots" /app/web/app.py | grep -q "return f"; then
    echo "✅ NEW CODE FOUND (direct return)"
else
    echo "❌ OLD CODE FOUND (using Response object)"
fi

echo ""
echo "3️⃣ Testing BASE_URL environment variable:"
echo "=========================================="
docker exec $CONTAINER_ID sh -c 'echo "ENV BASE_URL: $BASE_URL"'
docker exec $CONTAINER_ID python -c "import os; print(f'Python sees BASE_URL: {os.getenv(\"BASE_URL\", \"NOT SET\")}')"

echo ""
echo "4️⃣ Testing robots() function directly:"
echo "========================================"
docker exec $CONTAINER_ID python << 'PYEOF'
import sys
sys.path.insert(0, '/app')
import os
print(f"OS env BASE_URL: {os.getenv('BASE_URL', 'NOT SET')}")

from web.app import BASE_URL, robots
import asyncio

print(f"Module BASE_URL: {BASE_URL}")
print("\nCalling robots():")
result = asyncio.run(robots())
print(result)

if '{BASE_URL}' in result:
    print("\n❌ PROBLEM: Literal {BASE_URL} found in output!")
elif 'test.example.com' in result:
    print("\n✅ SUCCESS: BASE_URL correctly substituted!")
else:
    print(f"\n⚠️  WARNING: Neither found. Got: {result[:100]}")
PYEOF

echo ""
echo "5️⃣ Testing via HTTP endpoint:"
echo "=============================="
sleep 2
docker exec $CONTAINER_ID python << 'PYEOF'
import urllib.request
try:
    response = urllib.request.urlopen('http://localhost:8080/robots.txt')
    content = response.read().decode('utf-8')
    print(content)
    if '{BASE_URL}' in content:
        print("\n❌ HTTP RESPONSE: Literal {BASE_URL} in HTTP response!")
    elif 'test.example.com' in content:
        print("\n✅ HTTP RESPONSE: BASE_URL correctly substituted in HTTP response!")
except Exception as e:
    print(f"Error: {e}")
PYEOF

echo ""
echo "🧹 Cleaning up..."
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null

echo "✅ Done!"
