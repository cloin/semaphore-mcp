#!/bin/bash
set -e

# Set the Semaphore URL or use default
SEMAPHORE_URL=${SEMAPHORE_URL:-http://localhost:3000}
echo "Using Semaphore URL: $SEMAPHORE_URL"

# Use environment variables for credentials or fallback to defaults
# These should be set from GitHub secrets
ADMIN_USER=${ADMIN_USERNAME:-admin}
ADMIN_PASS=${ADMIN_PASSWORD:-admin123}

# Step 1: Login to Semaphore and get cookie
echo "Logging in with user: $ADMIN_USER"
LOGIN_RESPONSE=$(curl -s -c /tmp/semaphore-cookie -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d "{\"auth\": \"$ADMIN_USER\", \"password\": \"$ADMIN_PASS\"}" \
  $SEMAPHORE_URL/api/auth/login)

echo "Login response: $LOGIN_RESPONSE"

# Step 2: Generate a new token
echo "Generating new token..."
CREATE_RESPONSE=$(curl -s -b /tmp/semaphore-cookie -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  $SEMAPHORE_URL/api/user/tokens)

echo "Create token response: $CREATE_RESPONSE"

# Extract the token ID directly from creation response if possible
if echo "$CREATE_RESPONSE" | grep -q "id"; then
  FULL_TOKEN=$(echo "$CREATE_RESPONSE" | grep -Po '"id"\s*:\s*"\K[^"]*')
  echo "Extracted token from creation response"
else
  # Step 3: Get the token value from list
  echo "Getting token list..."
  TOKEN_JSON=$(curl -s -b /tmp/semaphore-cookie \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    $SEMAPHORE_URL/api/user/tokens)

  echo "Token list response: $TOKEN_JSON"

  # Extract FULL token - not just first few characters
  FULL_TOKEN=$(echo "$TOKEN_JSON" | jq -r '.[0].id')
  echo "Extracted token from list response"
fi

# Fallback if needed
if [ -z "$FULL_TOKEN" ] || [ "$FULL_TOKEN" = "null" ]; then
  echo "Trying alternative method..."
  FULL_TOKEN=$(curl -s -X POST \
    -H 'Content-Type: application/json' \
    -d "{\"auth\": \"$ADMIN_USER\", \"password\": \"$ADMIN_PASS\"}" \
    $SEMAPHORE_URL/api/auth/login | jq -r '.token')
    
  if [ -n "$FULL_TOKEN" ] && [ "$FULL_TOKEN" != "null" ]; then
    echo "Alternative method succeeded"
  else
    echo "All token generation methods failed"
    exit 1
  fi
fi

# Show full token length for debugging
echo "Token length: ${#FULL_TOKEN}"
echo "Token first part: ${FULL_TOKEN:0:10}..."

# Output token for GitHub Actions
echo "SEMAPHORE_API_TOKEN=$FULL_TOKEN" >> $GITHUB_ENV
echo "token=$FULL_TOKEN" >> $GITHUB_OUTPUT
