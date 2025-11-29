#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  MCP End-to-End Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Configuration
SEMAPHORE_ADMIN_PASSWORD="${SEMAPHORE_ADMIN_PASSWORD:-changeme123}"
SEMAPHORE_ADMIN_NAME="${SEMAPHORE_ADMIN_NAME:-admin}"
SEMAPHORE_ADMIN_EMAIL="${SEMAPHORE_ADMIN_EMAIL:-admin@localhost}"
MCP_SERVER_URL="${MCP_SERVER_URL:-http://localhost:8000}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.test.yml}"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    docker-compose -f "$COMPOSE_FILE" down -v 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Trap cleanup on exit
trap cleanup EXIT INT TERM

# Function to wait for service
# Usage: wait_for_service URL [expect_any_response]
# If expect_any_response is "true", accepts any HTTP response (including 4xx)
wait_for_service() {
    local url=$1
    local expect_any=${2:-false}
    local max_attempts=30
    local attempt=1

    echo -e "${BLUE}⏳ Waiting for service at $url...${NC}"

    while [ $attempt -le $max_attempts ]; do
        if [ "$expect_any" = "true" ]; then
            # Accept any HTTP response (server is up)
            if curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -qE '^[0-9]+$'; then
                echo -e "${GREEN}✅ Service is ready!${NC}"
                return 0
            fi
        else
            # Expect 2xx response
            if curl -sf "$url" > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Service is ready!${NC}"
                return 0
            fi
        fi
        echo -e "   Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e "${RED}❌ Service failed to become ready${NC}"
    return 1
}

# Step 1: Build and start containers
echo -e "${BLUE}📦 Step 1: Building and starting containers...${NC}"
docker-compose -f "$COMPOSE_FILE" build
docker-compose -f "$COMPOSE_FILE" up -d

# Step 2: Wait for Semaphore to be ready
echo -e "\n${BLUE}📦 Step 2: Waiting for Semaphore...${NC}"
wait_for_service "http://localhost:3000/api/ping"

# Step 3: Generate API token
echo -e "\n${BLUE}🔑 Step 3: Generating API token...${NC}"
sleep 2  # Give Semaphore a moment to fully initialize

# Create a temp file for cookies
COOKIE_FILE=$(mktemp)
trap "rm -f $COOKIE_FILE" EXIT

# Login to get session cookie
LOGIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -c "$COOKIE_FILE" -X POST http://localhost:3000/api/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"auth\": \"$SEMAPHORE_ADMIN_NAME\", \"password\": \"$SEMAPHORE_ADMIN_PASSWORD\"}")

if [ "$LOGIN_STATUS" != "204" ]; then
    echo -e "${RED}❌ Failed to login to Semaphore (HTTP $LOGIN_STATUS)${NC}"
    docker-compose -f "$COMPOSE_FILE" logs semaphore
    exit 1
fi

echo -e "${GREEN}✅ Login successful${NC}"

# Create API token using session cookie
TOKEN_RESPONSE=$(curl -s -b "$COOKIE_FILE" -X POST http://localhost:3000/api/user/tokens \
    -H "Content-Type: application/json" \
    || echo "")

if [ -z "$TOKEN_RESPONSE" ]; then
    echo -e "${RED}❌ Failed to create API token${NC}"
    exit 1
fi

# Extract token ID from response
SEMAPHORE_API_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$SEMAPHORE_API_TOKEN" ]; then
    echo -e "${RED}❌ Failed to extract API token from response${NC}"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ API token generated${NC}"

# Step 4: Restart MCP server with token
echo -e "\n${BLUE}🔄 Step 4: Restarting MCP server with token...${NC}"
docker-compose -f "$COMPOSE_FILE" stop semaphore-mcp
export SEMAPHORE_API_TOKEN
docker-compose -f "$COMPOSE_FILE" up -d semaphore-mcp

# Wait for MCP server (accepts any HTTP response, including 404 on root)
wait_for_service "$MCP_SERVER_URL" true

# Step 5: Install Node.js dependencies (for MCP Inspector)
echo -e "\n${BLUE}📦 Step 5: Installing MCP Inspector...${NC}"
if ! command -v npx &> /dev/null; then
    echo -e "${RED}❌ npx not found. Please install Node.js${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npx available${NC}"

# Step 6: Run tests
echo -e "\n${BLUE}🧪 Step 6: Running E2E Tests...${NC}"
echo -e "${BLUE}========================================${NC}"

export MCP_SERVER_URL

# Give the server a moment to fully initialize
sleep 3

# Verify MCP server is responding
echo -e "${BLUE}Verifying MCP server connectivity...${NC}"
if ! curl -sf "$MCP_SERVER_URL" > /dev/null 2>&1 && ! curl -s -o /dev/null -w "%{http_code}" "$MCP_SERVER_URL" | grep -qE '^[0-9]+$'; then
    echo -e "${RED}❌ MCP server not responding${NC}"
    exit 1
fi
echo -e "${GREEN}✅ MCP server is responding${NC}"

# Determine Python command (prefer uv run if available)
if command -v uv &> /dev/null && [ -f "pyproject.toml" ]; then
    PYTHON_CMD="uv run python3"
    PYTEST_CMD="uv run pytest"
else
    PYTHON_CMD="python3"
    PYTEST_CMD="python3 -m pytest"
fi

# Test 1: Tool Registration
echo -e "\n${YELLOW}Test 1: Tool Registration${NC}"
$PYTHON_CMD tests/e2e/test_tool_registration.py
TEST1_STATUS=$?

# Test 2: Per-category workflow tests (using pytest)
echo -e "\n${YELLOW}Test 2: Project & Environment Workflow Tests${NC}"
$PYTEST_CMD tests/e2e/test_projects_e2e.py tests/e2e/test_environments_e2e.py -v --tb=short
TEST2_STATUS=$?

# Test 3: Comprehensive Scenario (optional - requires full project setup)
echo -e "\n${YELLOW}Test 3: Comprehensive Scenario${NC}"
# python3 tests/e2e/test_comprehensive_scenario.py
# TEST3_STATUS=$?
TEST3_STATUS=0  # Skip for now - requires template/repository setup
echo -e "${YELLOW}⚠️  Comprehensive scenario skipped (requires full project setup)${NC}"

# Step 7: Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"

TOTAL_TESTS=2
PASSED_TESTS=0

[ $TEST1_STATUS -eq 0 ] && PASSED_TESTS=$((PASSED_TESTS + 1))
[ $TEST2_STATUS -eq 0 ] && PASSED_TESTS=$((PASSED_TESTS + 1))
# [ $TEST3_STATUS -eq 0 ] && PASSED_TESTS=$((PASSED_TESTS + 1))

echo -e "Tool Registration:       $([ $TEST1_STATUS -eq 0 ] && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}")"
echo -e "Workflow Tests:          $([ $TEST2_STATUS -eq 0 ] && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}")"
# echo -e "Comprehensive Scenario:  $([ $TEST3_STATUS -eq 0 ] && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}")"

echo -e "\n${BLUE}========================================${NC}"
if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}✅ All tests passed! ($PASSED_TESTS/$TOTAL_TESTS)${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}❌ Some tests failed ($PASSED_TESTS/$TOTAL_TESTS passed)${NC}"
    EXIT_CODE=1
fi
echo -e "${BLUE}========================================${NC}"

# Show logs on failure
if [ $EXIT_CODE -ne 0 ]; then
    echo -e "\n${YELLOW}📋 Container Logs:${NC}"
    echo -e "${YELLOW}--- Semaphore Logs ---${NC}"
    docker-compose -f "$COMPOSE_FILE" logs --tail=50 semaphore
    echo -e "\n${YELLOW}--- MCP Server Logs ---${NC}"
    docker-compose -f "$COMPOSE_FILE" logs --tail=50 semaphore-mcp
fi

exit $EXIT_CODE
