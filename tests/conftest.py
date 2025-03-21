import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator, Dict
import os
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.models.database import Base
from app.core.security import SECRET_KEY, ALGORITHM

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client() -> Generator:
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user() -> Dict[str, str]:
    return {
        "username": "testuser",
        "email": "test@example.com",
        "role": "user"
    }

@pytest.fixture
def token(test_user: Dict[str, str]) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {
        "sub": test_user["username"],
        "exp": expire,
        "role": test_user["role"]
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@pytest.fixture
def authorized_client(client: TestClient, token: str) -> TestClient:
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_document_data() -> bytes:
    # Create a small test image with some text
    from PIL import Image, ImageDraw
    import io
    
    # Create a new image with white background
    img = Image.new('RGB', (200, 100), color='white')
    d = ImageDraw.Draw(img)
    
    # Add some test text
    d.text((10, 10), "Tax Year: 2024/25", fill='black')
    d.text((10, 30), "Employer: Test Corp Ltd", fill='black')
    d.text((10, 50), "Total Income: £45,000", fill='black')
    d.text((10, 70), "Tax Paid: £9,000", fill='black')
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
