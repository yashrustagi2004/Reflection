#!/bin/bash
# 
# Quick test script using curl commands
# Tests the parsed content API endpoints
#

# Base URL
BASE_URL="http://localhost:5002"

echo ""
echo "Testing service health..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

echo "Checking content status..."
curl -s "$BASE_URL/api/files/content-status" | python3 -m json.tool
echo ""

echo "Getting parsed content (main test)..."
echo "This is the equivalent of the Python code:"
echo "response = requests.get('http://localhost:5002/api/files/parsed-content')"
echo ""

RESPONSE=$(curl -s "$BASE_URL/api/files/parsed-content")
echo "$RESPONSE" | python3 -m json.tool
