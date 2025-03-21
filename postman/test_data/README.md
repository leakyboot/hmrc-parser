# Test Data for UK Tax Parser API

This directory contains sample tax documents for testing the API. These documents are designed to test various scenarios and document formats.

## Sample Documents

1. `p60_sample.pdf`: Sample P60 document with complete tax year information
2. `p45_sample.pdf`: Sample P45 document with leaving date
3. `invalid_format.txt`: Invalid file format for testing error handling

## Document Requirements

For successful OCR processing:
- Clear, readable text
- Standard UK tax document format
- Supported file types (PDF, PNG, JPEG)
- File size under 10MB

## Testing Scenarios

1. **Happy Path**:
   - Use `p60_sample.pdf` for basic document processing
   - Contains all required fields
   - Clear text formatting

2. **Edge Cases**:
   - `p45_sample.pdf` tests additional field extraction
   - Tests date format handling
   - Tests employer information extraction

3. **Error Cases**:
   - `invalid_format.txt` for testing file type validation
   - Tests error handling
   - Tests response format for failures

## OCR Considerations

- Using Tesseract OCR in test environment
- No AWS credentials required
- Optimized for standard UK tax document formats
