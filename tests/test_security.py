import pytest
from datetime import datetime, timedelta
from app.core.security import SecurityManager, RBACManager
from jose import jwt
import os

class TestSecurityManager:
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password123"
        hashed = SecurityManager.get_password_hash(password)
        
        # Verify the hash is different from the original password
        assert hashed != password
        
        # Verify the password against its hash
        assert SecurityManager.verify_password(password, hashed) is True
        assert SecurityManager.verify_password("wrong_password", hashed) is False

    def test_token_creation(self):
        """Test JWT token creation"""
        test_data = {"sub": "testuser", "role": "user"}
        token = SecurityManager.create_access_token(test_data)
        
        # Verify token is a string
        assert isinstance(token, str)
        
        # Decode and verify token contents
        decoded = jwt.decode(
            token,
            os.getenv("SECRET_KEY", "your-secret-key-here"),
            algorithms=["HS256"]
        )
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "user"
        assert "exp" in decoded

    @pytest.mark.asyncio
    async def test_token_expiration(self):
        """Test token expiration"""
        test_data = {"sub": "testuser"}
        # Create token with very short expiration
        token = SecurityManager.create_access_token(
            test_data,
            expires_delta=timedelta(microseconds=1)
        )
        
        # Wait for token to expire
        import time
        time.sleep(0.1)
        
        # Verify token
        with pytest.raises(Exception):
            await SecurityManager.verify_token(token)

    @pytest.mark.asyncio
    async def test_verify_token(self):
        """Test token verification"""
        test_data = {"sub": "testuser", "role": "user"}
        token = SecurityManager.create_access_token(test_data)
        
        # Verify valid token
        payload = await SecurityManager.verify_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "user"
        
        # Test invalid token
        with pytest.raises(Exception):
            await SecurityManager.verify_token("invalid_token")

class TestRBACManager:
    def test_check_permission(self):
        """Test RBAC permission checking"""
        test_cases = [
            # (role, permission, expected_result)
            ("admin", "upload", True),
            ("admin", "manage_users", True),
            ("user", "upload", True),
            ("user", "manage_users", False),
            ("readonly", "read", True),
            ("readonly", "upload", False),
            ("invalid_role", "upload", False),
        ]
        
        for role, permission, expected in test_cases:
            assert RBACManager.check_permission(role, permission) == expected

    @pytest.mark.asyncio
    async def test_verify_permission(self):
        """Test RBAC permission verification with tokens"""
        # Create tokens for different roles
        tokens = {
            "admin": SecurityManager.create_access_token({"sub": "admin", "role": "admin"}),
            "user": SecurityManager.create_access_token({"sub": "user", "role": "user"}),
            "readonly": SecurityManager.create_access_token({"sub": "guest", "role": "readonly"})
        }
        
        test_cases = [
            # (role, permission, expected_result)
            ("admin", "manage_users", True),
            ("user", "upload", True),
            ("user", "manage_users", False),
            ("readonly", "read", True),
            ("readonly", "upload", False),
        ]
        
        for role, permission, expected in test_cases:
            result = await RBACManager.verify_permission(tokens[role], permission)
            assert result == expected
