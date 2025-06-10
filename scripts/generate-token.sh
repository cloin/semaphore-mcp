#!/bin/bash
set -e

# Check for required arguments
if [ $# -lt 2 ]; then
  echo "Usage: $0 <username> <password> [semaphore_url]"
  exit 1
fi

# Get arguments
ADMIN_USER="$1"
ADMIN_PASS="$2"

# Set the Semaphore URL from args or default
if [ $# -ge 3 ]; then
  SEMAPHORE_URL="$3"
else
  SEMAPHORE_URL="http://localhost:3000"
fi

echo "Using Semaphore URL: $SEMAPHORE_URL"

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

# Extract the token ID directly from creation response with portable command
if echo "$CREATE_RESPONSE" | grep -q "id"; then
  # Use jq if available for JSON parsing (more reliable)
  if command -v jq &> /dev/null; then
    FULL_TOKEN=$(echo "$CREATE_RESPONSE" | jq -r '.id')
  else
    # Fallback to sed for basic extraction
    FULL_TOKEN=$(echo "$CREATE_RESPONSE" | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
  fi
  echo "Extracted token from creation response"
else
  # Step 3: Get the token value from list
  echo "Getting token list..."
  TOKEN_JSON=$(curl -s -b /tmp/semaphore-cookie \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    $SEMAPHORE_URL/api/user/tokens)

  echo "Token list response: $TOKEN_JSON"

  # Extract FULL token using jq
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

# Show token length for debug
TOKEN_LENGTH=${#FULL_TOKEN}
echo "Token length: $TOKEN_LENGTH"
echo "Token first part: ${FULL_TOKEN:0:10}..."

# Check if we're running in GitHub Actions
if [ -n "$GITHUB_ENV" ] && [ -n "$GITHUB_OUTPUT" ]; then
  # Output token for GitHub Actions
  echo "SEMAPHORE_API_TOKEN=$FULL_TOKEN" >> $GITHUB_ENV
  echo "token=$FULL_TOKEN" >> $GITHUB_OUTPUT
else
  # Just echo the token for local usage
  echo "SEMAPHORE_API_TOKEN=$FULL_TOKEN"
fi

# Return the token as the command output
echo "$FULL_TOKEN"

# Exit with success
exit 0
