#!/bin/bash

# Test runner script for UK Tax Parser API Postman collection
# This script runs the Postman collection using Newman

# Check if Newman is installed
if ! command -v newman &> /dev/null; then
    echo "Newman is not installed. Installing..."
    npm install -g newman
fi

# Set environment variables
export OCR_ENGINE=tesseract
export BASE_URL=http://localhost:8000

# Run the collection
echo "Running UK Tax Parser API tests..."
newman run UK_Tax_Parser_API.postman_collection.json \
    -e UK_Tax_Parser_API.postman_environment.json \
    --folder Authentication \
    --folder Documents \
    --folder System \
    --reporters cli,json \
    --reporter-json-export test-results.json

# Check test results
if [ $? -eq 0 ]; then
    echo "All tests passed successfully!"
else
    echo "Some tests failed. Check test-results.json for details."
    exit 1
fi
