import os
import pytesseract
from PIL import Image, UnidentifiedImageError
import boto3
from io import BytesIO
from typing import Optional, List, Set
import json
import logging
from pdf2image import convert_from_bytes
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    # Supported file extensions
    ALLOWED_EXTENSIONS: Set[str] = {"pdf", "png", "jpg", "jpeg"}

    def __init__(self):
        """Initialize document processor with configurable OCR engine."""
        self.ocr_engine = os.getenv("OCR_ENGINE", "tesseract")
        logger.debug(f"Initialized DocumentProcessor with OCR engine: {self.ocr_engine}")
        if self.ocr_engine == "textract":
            self.textract = boto3.client('textract')

    async def process_document(self, file_content: bytes, file_type: str = None) -> str:
        """Process document using configured OCR engine."""
        if not file_type:
            raise ValueError("File type must be provided")

        file_type = file_type.lower()
        logger.debug(f"Processing document with file type: {file_type}")

        if file_type not in self.ALLOWED_EXTENSIONS:
            logger.error(f"Invalid file type: {file_type}. Allowed extensions: {self.ALLOWED_EXTENSIONS}")
            raise ValueError(f"Unsupported file type: {file_type}")

        if self.ocr_engine == "textract" and os.getenv("AWS_ACCESS_KEY_ID"):
            try:
                return await self._process_with_textract(file_content)
            except Exception as e:
                logger.warning(f"Textract error: {e}, falling back to Tesseract")
                return await self._process_with_tesseract(file_content, file_type)
        else:
            return await self._process_with_tesseract(file_content, file_type)

    async def _process_with_tesseract(self, file_content: bytes, file_type: str) -> str:
        """Process document using Tesseract OCR."""
        try:
            # Handle PDFs differently
            if file_type == 'pdf':
                logger.debug("Processing PDF document with Tesseract")
                try:
                    logger.debug("Converting PDF to images")
                    # Use dpi=200 for better quality
                    images = convert_from_bytes(
                        file_content,
                        dpi=200,
                        fmt='jpeg',  # Use JPEG format for converted images
                        grayscale=True,  # Convert to grayscale for better OCR
                        size=(2000, None)  # Limit width to 2000px, maintain aspect ratio
                    )
                    logger.debug(f"Successfully converted PDF to {len(images)} images")
                except Exception as e:
                    logger.error(f"Error converting PDF to images: {str(e)}")
                    raise ValueError(f"Error converting PDF to images: {str(e)}")

                # Process each page and combine the text
                text_parts = []
                for i, image in enumerate(images):
                    logger.debug(f"Processing PDF page {i+1}")
                    try:
                        # Ensure image is in the right format for Tesseract
                        if image.mode not in ('L', 'RGB'):
                            image = image.convert('RGB')
                        
                        # Use Tesseract with specific configuration
                        page_text = pytesseract.image_to_string(
                            image,
                            config='--psm 1'  # Automatic page segmentation with OSD
                        )
                        
                        if page_text.strip():
                            text_parts.append(page_text.strip())
                            logger.debug(f"Successfully extracted text from page {i+1}")
                        else:
                            logger.warning(f"No text extracted from page {i+1}")
                    except Exception as e:
                        logger.error(f"Error processing page {i+1}: {str(e)}")
                        continue

                if not text_parts:
                    logger.error("No text was extracted from any PDF pages")
                    raise ValueError("No text was extracted from the PDF")
                
                logger.debug(f"Successfully processed {len(text_parts)} pages")
                return "\n\n".join(text_parts)
            else:
                logger.debug("Processing image document with Tesseract")
                # Handle image files
                image_data = BytesIO(file_content)
                try:
                    image = Image.open(image_data)
                    if image.mode not in ('L', 'RGB'):
                        image = image.convert('RGB')
                except UnidentifiedImageError:
                    logger.error(f"Could not identify image format for file type: {file_type}")
                    raise ValueError(f"Could not identify image format for file type: {file_type}")

                text = pytesseract.image_to_string(
                    image,
                    config='--psm 1'  # Automatic page segmentation with OSD
                )
                
                if not text.strip():
                    logger.error("No text was extracted from the image")
                    raise ValueError("No text was extracted from the image")
                
                logger.debug("Successfully extracted text from image")
                return text.strip()
        except Exception as e:
            logger.error(f"Error processing document with Tesseract: {str(e)}")
            raise Exception(f"Error processing document with Tesseract: {str(e)}")

    async def _process_with_textract(self, file_content: bytes) -> str:
        """Process document using AWS Textract."""
        try:
            response = self.textract.detect_document_text(Document={'Bytes': file_content})
            text = " ".join([block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE'])
            if not text.strip():
                logger.error("No text was extracted from the document")
                raise ValueError("No text was extracted from the document")
            return text.strip()
        except Exception as e:
            logger.error(f"Error processing document with Textract: {str(e)}")
            raise Exception(f"Error processing document with Textract: {str(e)}")

    @staticmethod
    def validate_file_type(filename: str) -> bool:
        """Validate if file type is supported."""
        logger.debug(f"Validating file type for: {filename}")
        if not filename:
            logger.error("No filename provided")
            return False
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        is_valid = ext in DocumentProcessor.ALLOWED_EXTENSIONS
        logger.debug(f"File extension '{ext}' is {'valid' if is_valid else 'invalid'}")
        return is_valid
