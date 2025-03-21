"""Core functionality for the UK Tax Document Parser API."""

from app.core.security import SecurityManager, RBACManager, TEST_USERS
from app.core.document_processor import DocumentProcessor
from app.core.data_extractor import DataExtractor

__all__ = [
    'SecurityManager',
    'RBACManager',
    'TEST_USERS',
    'DocumentProcessor',
    'DataExtractor'
]
