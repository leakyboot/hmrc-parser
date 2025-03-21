import pytest
from PIL import Image
import io
import os
from app.core.document_processor import DocumentProcessor
from unittest.mock import patch, MagicMock

@pytest.fixture
def document_processor():
    return DocumentProcessor()

@pytest.fixture
def sample_image():
    """Create a sample image with text for testing."""
    img = Image.new('RGB', (100, 30), color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr.read()

class TestDocumentProcessor:
    @pytest.mark.asyncio
    async def test_process_with_tesseract(self, document_processor, sample_image):
        """Test document processing with Tesseract OCR."""
        with patch('pytesseract.image_to_string', return_value='Test Document'):
            result = await document_processor.process_document(sample_image)
            assert result == 'Test Document'

    @pytest.mark.asyncio
    async def test_process_with_invalid_image(self, document_processor):
        """Test processing with invalid image data."""
        with pytest.raises(Exception) as exc_info:
            await document_processor.process_document(b'invalid image data')
        assert "Error processing document" in str(exc_info.value)

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("AWS_ACCESS_KEY_ID"), reason="AWS credentials not configured")
    async def test_process_with_textract(self, document_processor, sample_image):
        """Test document processing with AWS Textract when credentials are available."""
        # Only run if OCR_ENGINE is set to textract
        if os.getenv("OCR_ENGINE") != "textract":
            pytest.skip("Textract not configured as OCR engine")

        mock_response = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'Test'},
                {'BlockType': 'LINE', 'Text': 'Document'}
            ]
        }
        
        with patch.object(document_processor, 'textract') as mock_textract:
            mock_textract.detect_document_text.return_value = mock_response
            result = await document_processor.process_document(sample_image)
            assert result == 'Test Document'

    def test_validate_file_type(self, document_processor):
        """Test file type validation."""
        assert document_processor.validate_file_type('test.pdf') is True
        assert document_processor.validate_file_type('test.png') is True
        assert document_processor.validate_file_type('test.jpg') is True
        assert document_processor.validate_file_type('test.txt') is False
