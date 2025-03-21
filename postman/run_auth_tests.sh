#!/bin/bash

# Authentication test runner for UK Tax Parser API
echo "Starting authentication tests..."

# Set up test environment
export BASE_URL=http://localhost:8000
export TEST_USERNAME=testuser
export TEST_PASSWORD=testpass

# First, ensure the FastAPI server is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "Error: API server is not running. Please start the server first."
    exit 1
fi

# Create a temporary file to store auth tests
echo "Setting up test environment..."
TEMP_DIR=$(mktemp -d)
cp auth_tests.js "$TEMP_DIR/auth_tests.js"

# Run the auth test collection
newman run UK_Tax_Parser_Auth_Tests.postman_collection.json \
    -e test_environment.json \
    --env-var "username=$TEST_USERNAME" \
    --env-var "password=$TEST_PASSWORD" \
    --globals "$TEMP_DIR/auth_tests.js" \
    --reporters cli,json \
    --reporter-json-export auth-test-results.json \
    --bail

TEST_EXIT_CODE=$?

# Cleanup
rm -rf "$TEMP_DIR"

# Check test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "Authentication tests completed successfully!"
    echo "Test results saved to auth-test-results.json"
else
    echo "Some authentication tests failed. Check auth-test-results.json for details."
    exit 1
fi
