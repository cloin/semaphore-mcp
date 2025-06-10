#!/bin/bash
set -e

# Set the Semaphore URL or use default
SEMAPHORE_URL=${SEMAPHORE_URL:-http://localhost:3000}
echo "Using Semaphore URL: $SEMAPHORE_URL"

# Step 1: Login to Semaphore and get cookie
echo "Logging in to get cookie..."
LOGIN_RESPONSE=$(curl -s -c /tmp/semaphore-cookie -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{"auth": "admin", "password": "admin123"}' \
  $SEMAPHORE_URL/api/auth/login)

echo "Login response: $LOGIN_RESPONSE"

# Step 2: Generate a new token
echo "Generating new token..."
CREATE_RESPONSE=$(curl -s -b /tmp/semaphore-cookie -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  $SEMAPHORE_URL/api/user/tokens)

echo "Create token response: $CREATE_RESPONSE"

# Step 3: Get the token value
echo "Getting token list..."
TOKEN_JSON=$(curl -s -b /tmp/semaphore-cookie \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  $SEMAPHORE_URL/api/user/tokens)

echo "Token list response: $TOKEN_JSON"

# Extract token from JSON array
TOKEN=$(echo "$TOKEN_JSON" | jq -r '.[0].id')
echo "Extracted token: ${TOKEN:0:10}..."

# Fallback if needed
if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
  echo "Trying alternative method..."
  ALT_TOKEN=$(curl -s -X POST \
    -H 'Content-Type: application/json' \
    -d '{"auth": "admin", "password": "admin123"}' \
    $SEMAPHORE_URL/api/auth/login | jq -r '.token')
    
  if [ -n "$ALT_TOKEN" ] && [ "$ALT_TOKEN" != "null" ]; then
    echo "Alternative method succeeded"
    TOKEN=$ALT_TOKEN
    echo "Alternative token: ${TOKEN:0:10}..."
  else
    echo "All token generation methods failed"
    exit 1
  fi
fi

# Create .env file with token if requested
if [ "$1" = "--save-env" ]; then
  echo "SEMAPHORE_URL=$SEMAPHORE_URL" > .env
  echo "SEMAPHORE_API_TOKEN=$TOKEN" >> .env
  echo "Token saved to .env file"
fi

# Output token
echo ""
echo "FINAL TOKEN: $TOKEN"
echo ""
echo "Use this token in your .env file or as SEMAPHORE_API_TOKEN environment variable"
