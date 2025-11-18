#!/bin/bash

# GitHub PR Analysis API Test Script

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "GitHub PR Analysis API Test"
echo "=========================================="

# Check if API is running
echo -e "\n[1] Checking API health..."
HEALTH=$(curl -s "$BASE_URL/health")
if [ $? -eq 0 ]; then
    echo "✓ API is running"
    echo "  Response: $HEALTH"
else
    echo "✗ API is not responding"
    echo "  Make sure docker-compose is running: docker-compose up"
    exit 1
fi

# Get repository URL and PR number from arguments or use defaults
REPO_URL=${1:-"https://github.com/octocat/Hello-World"}
PR_NUMBER=${2:-1}

echo -e "\n[2] Starting PR analysis..."
echo "  Repository: $REPO_URL"
echo "  PR Number: $PR_NUMBER"

TASK_RESPONSE=$(curl -s -X POST "$BASE_URL/analyze-pr?repo_url=$REPO_URL&pr_number=$PR_NUMBER")
TASK_ID=$(echo $TASK_RESPONSE | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$TASK_ID" ]; then
    echo "✗ Failed to create task"
    echo "  Response: $TASK_RESPONSE"
    exit 1
fi

echo "  ✓ Task created: $TASK_ID"

# Poll for status
echo -e "\n[3] Waiting for analysis to complete..."
MAX_WAIT=300
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    STATUS_RESPONSE=$(curl -s "$BASE_URL/status/$TASK_ID")
    STATUS=$(echo $STATUS_RESPONSE | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    
    echo -ne "\r  Status: $STATUS (${ELAPSED}s)     "
    
    if [ "$STATUS" == "completed" ]; then
        echo -e "\n  ✓ Analysis completed!"
        break
    elif [ "$STATUS" == "failed" ]; then
        echo -e "\n  ✗ Analysis failed!"
        exit 1
    fi
    
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo -e "\n  ✗ Timeout after $MAX_WAIT seconds"
    exit 1
fi

# Get results
echo -e "\n[4] Retrieving results..."
RESULTS=$(curl -s "$BASE_URL/results/$TASK_ID")

echo -e "\n=========================================="
echo "RESULTS"
echo "=========================================="
echo "$RESULTS" | python -m json.tool 2>/dev/null || echo "$RESULTS"

echo -e "\n=========================================="
echo "Test completed successfully!"
echo "=========================================="

