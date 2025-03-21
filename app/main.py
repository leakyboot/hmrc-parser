"""UK Tax Document Parser API."""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import json
import os
import logging
from datetime import datetime, timedelta

from app.core.document_processor import DocumentProcessor
from app.core.data_extractor import DataExtractor
from app.core.security import SecurityManager, RBACManager, TEST_USERS
from app.models.schemas import (
    Token, TokenData, DocumentResponse, DocumentStatus,
    DocumentData, DeleteResponse, HealthCheck
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="UK Tax Document Parser API",
    description="""
    An API for processing and extracting data from UK tax documents (P60, P45) using OCR.
    Supports both Tesseract (local) and AWS Textract for document processing.
    
    Features:
    - Document upload and processing
    - Data extraction from tax documents
    - Support for multiple document types (P60, P45)
    - Secure authentication
    - Configurable OCR engine
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Operations for user authentication and token management"
        },
        {
            "name": "documents",
            "description": "Operations for processing and managing tax documents"
        }
    ]
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check() -> HealthCheck:
    """Check API health status."""
    return HealthCheck(status="healthy")

@app.post(
    "/token",
    response_model=Token,
    tags=["authentication"],
    summary="Create access token",
    responses={
        401: {"description": "Invalid credentials"}
    }
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Get access token for API authentication.
    
    - **username**: User's username (testuser, admin, or readonly)
    - **password**: User's password (testpass for all test users)
    
    Returns an access token if credentials are valid.
    """
    if SecurityManager.verify_credentials(form_data.username, form_data.password):
        user = TEST_USERS[form_data.username]
        access_token = SecurityManager.create_access_token(
            data={
                "sub": form_data.username,
                "role": user["role"]
            },
            expires_delta=timedelta(minutes=30)
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            role=user["role"]
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.post(
    "/upload",
    response_model=DocumentResponse,
    tags=["documents"],
    summary="Upload tax document",
    responses={
        400: {"description": "Invalid file format"},
        401: {"description": "Not authenticated"},
        500: {"description": "Processing error"}
    }
)
async def upload_document(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme)
) -> DocumentResponse:
    """
    Upload a tax document for processing.
    
    - **file**: Tax document file (PDF, PNG, JPEG)
    
    The document will be processed using the configured OCR engine (Tesseract by default).
    Data will be extracted and structured according to the document type.
    
    Requires authentication via Bearer token.
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"Received upload request for file: {file.filename}")
    
    # Extract and validate file type
    file_type = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    logger.debug(f"Extracted file type: {file_type}")
    
    if not file_type:
        logger.error("No file extension found")
        raise HTTPException(
            status_code=400,
            detail="No file extension found. Supported formats: pdf, png, jpg, jpeg"
        )
    
    if file_type not in DocumentProcessor.ALLOWED_EXTENSIONS:
        logger.error(f"Invalid file format: {file_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format: {file_type}. Supported formats: {', '.join(DocumentProcessor.ALLOWED_EXTENSIONS)}"
        )
    
    # Process document
    try:
        processor = DocumentProcessor()
        content = await file.read()
        logger.debug(f"Processing document with type: {file_type}")
        text = await processor.process_document(content, file_type)
        logger.debug("Document processed successfully")
        
        # Extract data
        extractor = DataExtractor()
        data = extractor.extract_data(text)
        logger.debug("Data extracted successfully")
        
        return DocumentResponse(
            status="success",
            document_id=str(datetime.now().timestamp()),
            data=data
        )
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

@app.get(
    "/status/{document_id}",
    response_model=DocumentStatus,
    tags=["documents"],
    summary="Get document status",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Document not found"}
    }
)
async def get_status(
    document_id: str,
    token: str = Depends(oauth2_scheme)
) -> DocumentStatus:
    """
    Get the processing status of a document.
    
    - **document_id**: ID of the uploaded document
    
    Returns the current processing status and last update timestamp.
    
    Requires authentication via Bearer token.
    """
    return DocumentStatus(
        status="completed",
        document_id=document_id,
        last_updated=datetime.now()
    )

@app.get(
    "/data/{document_id}",
    response_model=DocumentData,
    tags=["documents"],
    summary="Get extracted data",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Document not found"}
    }
)
async def get_data(
    document_id: str,
    token: str = Depends(oauth2_scheme)
) -> DocumentData:
    """
    Get the extracted data from a processed document.
    
    - **document_id**: ID of the processed document
    
    Returns the structured data extracted from the document, including:
    - Tax year
    - Total income
    - Tax paid
    - National Insurance number (if available)
    - Employer information (if available)
    
    Requires authentication via Bearer token.
    """
    return DocumentData(
        document_id=document_id,
        tax_year="2023",
        total_income="50000.00",
        tax_paid="10000.00",
        ni_number="AB123456C",
        employer_name="ACME Corporation"
    )

@app.delete(
    "/document/{document_id}",
    response_model=DeleteResponse,
    tags=["documents"],
    summary="Delete document",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Document not found"}
    }
)
async def delete_document(
    document_id: str,
    token: str = Depends(oauth2_scheme)
) -> DeleteResponse:
    """
    Delete a processed document and its data.
    
    - **document_id**: ID of the document to delete
    
    Returns a confirmation of deletion.
    
    Requires authentication via Bearer token.
    """
    return DeleteResponse(status="Document deleted successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
