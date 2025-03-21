import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import json
from unittest.mock import patch
import io

class TestAPI:
    def test_upload_document_unauthorized(self, client):
        """Test document upload without authentication"""
        files = {"file": ("test.png", b"test content", "image/png")}
        response = client.post("/upload", files=files)
        assert response.status_code == 401
        assert "Not authenticated" in response.text

    def test_upload_document_invalid_type(self, authorized_client):
        """Test document upload with invalid file type"""
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = authorized_client.post("/upload", files=files)
        assert response.status_code == 400
        assert "Invalid file format" in response.json()["detail"]

    def test_upload_document_success(self, authorized_client, test_document_data):
        """Test successful document upload"""
        files = {"file": ("test.png", test_document_data, "image/png")}
        response = authorized_client.post("/upload", files=files)
        assert response.status_code == 200
        assert "doc_id" in response.json()
        assert response.json()["status"] == "success"

    def test_get_status_unauthorized(self, client):
        """Test status check without authentication"""
        response = client.get("/status/test_id")
        assert response.status_code == 401
        assert "Not authenticated" in response.text

    def test_get_status_success(self, authorized_client):
        """Test successful status check"""
        response = authorized_client.get("/status/test_id")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_get_data_unauthorized(self, client):
        """Test data retrieval without authentication"""
        response = client.get("/data/test_id")
        assert response.status_code == 401
        assert "Not authenticated" in response.text

    @patch("app.models.database.get_db")
    def test_get_data_success(self, mock_get_db, authorized_client, db_session):
        """Test successful data retrieval"""
        # Mock database response
        mock_get_db.return_value = db_session
        
        response = authorized_client.get("/data/test_id")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_delete_document_unauthorized(self, client):
        """Test document deletion without authentication"""
        response = client.delete("/delete/test_id")
        assert response.status_code == 401
        assert "Not authenticated" in response.text

    @patch("app.models.database.get_db")
    def test_delete_document_success(self, mock_get_db, authorized_client, db_session):
        """Test successful document deletion"""
        # Mock database response
        mock_get_db.return_value = db_session
        
        response = authorized_client.delete("/delete/test_id")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
