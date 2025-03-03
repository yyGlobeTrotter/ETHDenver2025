#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Testing VinRouge Dexy Bot API =====${NC}"

# Install required packages for testing
echo -e "\n${YELLOW}Installing required packages...${NC}"
pip install -r api/requirements.txt
pip install requests

# Ask if the user wants to run the manual test
echo -e "\n${YELLOW}Do you want to run the manual API test? (y/n)${NC}"
read -r run_manual

if [ "$run_manual" = "y" ] || [ "$run_manual" = "Y" ]; then
    # Test 1: Basic Flask API
    echo -e "\n${YELLOW}Running basic Flask API test...${NC}"
    echo -e "${YELLOW}Press Ctrl+C when you're done testing the endpoints.${NC}"
    python test_api_local.py
else
    echo -e "\n${YELLOW}Skipping manual API test.${NC}"
fi

# Test 2: Automated API tests
echo -e "\n${YELLOW}Running automated API tests...${NC}"
python test_api_automated.py
API_TEST_RESULT=$?

# Test 3: Vercel handler tests
echo -e "\n${YELLOW}Running Vercel handler tests...${NC}"
python test_vercel_handler.py
HANDLER_TEST_RESULT=$?

# Print final results
echo -e "\n${YELLOW}===== Test Results Summary =====${NC}"
if [ $API_TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ API Tests: PASSED${NC}"
else
    echo -e "${RED}✗ API Tests: FAILED${NC}"
fi

if [ $HANDLER_TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Handler Tests: PASSED${NC}"
else
    echo -e "${RED}✗ Handler Tests: FAILED${NC}"
fi

if [ $API_TEST_RESULT -eq 0 ] && [ $HANDLER_TEST_RESULT -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! Your API is ready for deployment to Vercel.${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed. Please fix the issues before deploying to Vercel.${NC}"
    exit 1
fi 