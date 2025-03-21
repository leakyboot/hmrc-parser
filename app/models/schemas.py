from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Token(BaseModel):
    """OAuth2 token response model."""
    access_token: str
    token_type: str = Field("bearer", description="Type of token (always 'bearer')")
    role: Optional[str] = Field(None, description="User role (admin, user, or readonly)")

class TokenData(BaseModel):
    """Token data model."""
    username: str = Field(..., description="Username from the token")
    role: str = Field(..., description="User role from the token")
    exp: Optional[datetime] = Field(None, description="Token expiration timestamp")

class DocumentResponse(BaseModel):
    """Response model for document processing."""
    status: str = Field(..., description="Processing status of the document")
    document_id: str = Field(..., description="Unique identifier for the document")
    data: Optional[Dict[str, Any]] = Field(None, description="Extracted data from the document")

class DocumentStatus(BaseModel):
    """Document status response model."""
    status: str = Field(..., description="Current status of document processing")
    document_id: str = Field(..., description="Unique identifier for the document")
    last_updated: datetime = Field(..., description="Timestamp of last status update")

class DocumentData(BaseModel):
    """Document data response model."""
    document_id: str = Field(..., description="Unique identifier for the document")
    tax_year: str = Field(..., description="Tax year of the document")
    total_income: str = Field(..., description="Total income reported")
    tax_paid: str = Field(..., description="Total tax paid")
    ni_number: Optional[str] = Field(None, description="National Insurance number")
    employer_name: Optional[str] = Field(None, description="Employer name")

class DeleteResponse(BaseModel):
    """Response model for document deletion."""
    status: str = Field(..., description="Status of deletion operation")

class HealthCheck(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Current health status of the API")
