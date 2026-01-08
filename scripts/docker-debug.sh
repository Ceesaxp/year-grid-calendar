#!/bin/bash

echo "=== Docker Container Debug Script ==="
echo ""

CONTAINER_ID=$1

if [ -z "$CONTAINER_ID" ]; then
    echo "Usage: ./docker-debug.sh <container-id-or-name>"
    echo ""
    echo "Example: ./docker-debug.sh year-grid-calendar"
    exit 1
fi

echo "1. Checking BASE_URL environment variable:"
docker exec $CONTAINER_ID sh -c 'echo $BASE_URL'
echo ""

echo "2. Checking Python can see BASE_URL:"
docker exec $CONTAINER_ID python -c "import os; print(os.getenv('BASE_URL', 'NOT SET'))"
echo ""

echo "3. Checking the robots() function code:"
docker exec $CONTAINER_ID grep -A 8 "async def robots" /app/web/app.py
echo ""

echo "4. Testing robots endpoint directly:"
docker exec $CONTAINER_ID python -c "
import sys
sys.path.insert(0, '/app')
import os
print(f'BASE_URL env: {os.getenv(\"BASE_URL\", \"NOT SET\")}')
from web.app import BASE_URL, robots
import asyncio
print(f'BASE_URL in module: {BASE_URL}')
result = asyncio.run(robots())
print('robots.txt output:')
print(result)
"
echo ""

echo "5. Testing via HTTP:"
docker exec $CONTAINER_ID wget -qO- http://localhost:8080/robots.txt || \
docker exec $CONTAINER_ID wget -qO- http://localhost:8000/robots.txt || \
echo "Could not fetch via HTTP (wget not available)"
echo ""

