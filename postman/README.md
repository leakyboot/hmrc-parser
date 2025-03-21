# UK Tax Parser API - Postman Collection

This Postman collection provides a comprehensive set of API requests for testing the UK Tax Parser API. The collection includes authentication, document processing, and system health check endpoints.

## Setup Instructions

1. Import the Collection:
   - Open Postman
   - Click "Import" -> "Upload Files"
   - Select both `UK_Tax_Parser_API.postman_collection.json` and `UK_Tax_Parser_API.postman_environment.json`

2. Configure Environment:
   - Select the "UK Tax Parser API - Local" environment from the environment dropdown
   - The default configuration is set for local development:
     - base_url: `http://localhost:8000`
     - username: `testuser`
     - password: `testpass`

## Collection Features

### Authentication
- Automatic token management
- Token is stored in environment variables
- All subsequent requests use the stored token

### Request Categories

1. **Authentication**
   - Get Access Token (POST `/token`)
   - Automatically saves token for other requests

2. **Documents**
   - Upload Document (POST `/upload`)
   - Get Document Status (GET `/status/{document_id}`)
   - Get Document Data (GET `/data/{document_id}`)
   - Delete Document (DELETE `/document/{document_id}`)

3. **System**
   - Health Check (GET `/health`)

### Test Scripts

Each request includes test scripts that:
- Validate response status codes
- Check for required response fields
- Store important values (document_id, token) in variables
- Verify data types and formats

## Usage Examples

1. **Authentication Flow**:
   ```
   POST /token
   Content-Type: application/x-www-form-urlencoded
   
   username=testuser&password=testpass
   ```

2. **Document Upload**:
   ```
   POST /upload
   Authorization: Bearer {{access_token}}
   Content-Type: multipart/form-data
   
   file: <your-tax-document.pdf>
   ```

3. **Get Document Data**:
   ```
   GET /data/{{document_id}}
   Authorization: Bearer {{access_token}}
   ```

## Environment Variables

- `base_url`: API base URL
- `username`: Test user username
- `password`: Test user password
- `access_token`: JWT token (automatically set after login)
- `document_id`: Current document ID (set after upload)

## Testing Flow

1. Run "Get Access Token" request
2. Upload a document using "Upload Document"
3. Check processing status with "Get Document Status"
4. Retrieve extracted data using "Get Document Data"
5. Clean up using "Delete Document"

## OCR Engine Configuration

The API is configured to use Tesseract OCR by default for local testing. AWS Textract is available as an optional backend if AWS credentials are configured.

## Supported File Types

- PDF (`.pdf`)
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)

## Error Handling

The collection includes tests for common error scenarios:
- Invalid file types
- Missing authentication
- Invalid document IDs
- Server errors

## Security Notes

- All endpoints (except `/health`) require authentication
- Tokens expire after 30 minutes
- Use environment variables for sensitive data
- Don't commit real credentials to version control
