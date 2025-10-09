"""
Tests for authentication services.

Testing the core authentication functionality:
- Password hashing and verification
- JWT token creation and validation
- Edge cases and error handling
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from faproject.services.auth import JWTManager, PasswordManager


class TestPasswordManager:
    """Test password hashing and verification service."""

    def test_hash_password_basic(self):
        """Test basic password hashing."""
        password_manager = PasswordManager()
        plain_password = "testpassword123"

        hashed = password_manager.hash_password(plain_password)

        # Check that hash is created and different from original
        assert hashed != plain_password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

        # Check bcrypt hash format
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password_manager = PasswordManager()
        plain_password = "testpassword123"

        hashed = password_manager.hash_password(plain_password)
        result = password_manager.verify_password(plain_password, hashed)

        assert result is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password_manager = PasswordManager()
        plain_password = "testpassword123"
        wrong_password = "wrongpassword"

        hashed = password_manager.hash_password(plain_password)
        result = password_manager.verify_password(wrong_password, hashed)

        assert result is False

    def test_hash_same_password_different_results(self):
        """Test that hashing same password produces different results (salt)."""
        password_manager = PasswordManager()
        password = "testpassword123"

        hash1 = password_manager.hash_password(password)
        hash2 = password_manager.hash_password(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify correctly
        assert password_manager.verify_password(password, hash1) is True
        assert password_manager.verify_password(password, hash2) is True

    def test_hash_empty_password(self):
        """Test hashing empty password."""
        password_manager = PasswordManager()

        hashed = password_manager.hash_password("")

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert password_manager.verify_password("", hashed) is True

    def test_hash_unicode_password(self):
        """Test hashing password with unicode characters."""
        password_manager = PasswordManager()
        unicode_password = "пароль123🔒"

        hashed = password_manager.hash_password(unicode_password)

        assert isinstance(hashed, str)
        assert password_manager.verify_password(unicode_password, hashed) is True

    def test_verify_password_with_invalid_hash(self):
        """Test verification with invalid hash format."""
        password_manager = PasswordManager()

        # Should handle invalid hash gracefully
        result = password_manager.verify_password("password", "invalid_hash")
        assert result is False

    def test_hash_very_long_password(self):
        """Test hashing very long password."""
        password_manager = PasswordManager()
        long_password = "a" * 1000

        hashed = password_manager.hash_password(long_password)

        assert isinstance(hashed, str)
        assert password_manager.verify_password(long_password, hashed) is True


class TestJWTManager:
    """Test JWT token creation and verification service."""

    def test_create_access_token_basic(self):
        """Test basic access token creation."""
        jwt_manager = JWTManager()
        data = {"sub": "123", "email": "test@example.com"}

        token = jwt_manager.create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count(".") == 2  # JWT has 3 parts separated by dots

    def test_create_refresh_token_basic(self):
        """Test basic refresh token creation."""
        jwt_manager = JWTManager()
        data = {"sub": "123", "email": "test@example.com"}

        token = jwt_manager.create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count(".") == 2

    def test_verify_access_token_valid(self):
        """Test verification of valid access token."""
        jwt_manager = JWTManager()
        original_data = {"sub": "123", "email": "test@example.com", "role": "user"}

        token = jwt_manager.create_access_token(original_data)
        decoded_data = jwt_manager.verify_token(token)

        assert decoded_data["sub"] == "123"
        assert decoded_data["email"] == "test@example.com"
        assert decoded_data["role"] == "user"

        # Should have standard JWT claims
        assert "iat" in decoded_data  # issued at
        assert "exp" in decoded_data  # expires at

    def test_verify_refresh_token_valid(self):
        """Test verification of valid refresh token."""
        jwt_manager = JWTManager()
        original_data = {"sub": "123", "email": "test@example.com"}

        token = jwt_manager.create_refresh_token(original_data)
        decoded_data = jwt_manager.verify_token(token, is_refresh_token=True)

        assert decoded_data["sub"] == "123"
        assert decoded_data["email"] == "test@example.com"

    def test_verify_token_invalid_signature(self):
        """Test verification of token with invalid signature."""
        jwt_manager = JWTManager()

        # Create a token and modify it
        original_data = {"sub": "123", "email": "test@example.com"}
        token = jwt_manager.create_access_token(original_data)

        # Tamper with the token
        tampered_token = token[:-5] + "XXXXX"

        with pytest.raises(Exception):
            jwt_manager.verify_token(tampered_token)

    def test_verify_token_malformed(self):
        """Test verification of malformed token."""
        jwt_manager = JWTManager()

        malformed_tokens = [
            "not.a.jwt",
            "too.few.parts",
            "invalid_token_format",
            "",
            "a.b.c.d",  # Too many parts
        ]

        for token in malformed_tokens:
            with pytest.raises(Exception):
                jwt_manager.verify_token(token)

    def test_access_token_expiration_time(self):
        """Test that access tokens have correct expiration time."""
        jwt_manager = JWTManager()
        data = {"sub": "123"}

        before_creation = datetime.now(timezone.utc)
        token = jwt_manager.create_access_token(data)
        after_creation = datetime.now(timezone.utc)

        decoded = jwt_manager.verify_token(token)

        # Check that expiration is set correctly
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)

        # Should expire in approximately 30 minutes (default)
        expected_exp = before_creation + timedelta(minutes=30)

        # Allow some tolerance (±1 minute)
        assert abs((exp_datetime - expected_exp).total_seconds()) < 60

    def test_refresh_token_expiration_time(self):
        """Test that refresh tokens have correct expiration time."""
        jwt_manager = JWTManager()
        data = {"sub": "123"}

        before_creation = datetime.now(timezone.utc)
        token = jwt_manager.create_refresh_token(data)
        after_creation = datetime.now(timezone.utc)

        decoded = jwt_manager.verify_token(token, is_refresh_token=True)

        # Check that expiration is set correctly
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)

        # Should expire in approximately 7 days (default)
        expected_exp = before_creation + timedelta(days=7)

        # Allow some tolerance (±1 hour)
        assert abs((exp_datetime - expected_exp).total_seconds()) < 3600

    def test_token_with_custom_expiration(self):
        """Test creating token with custom expiration time."""
        jwt_manager = JWTManager()
        data = {"sub": "123"}
        custom_expiry = timedelta(minutes=5)

        before_creation = datetime.now(timezone.utc)
        token = jwt_manager.create_access_token(data, expires_delta=custom_expiry)

        decoded = jwt_manager.verify_token(token)

        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)

        expected_exp = before_creation + custom_expiry

        # Should be approximately 5 minutes from creation
        assert abs((exp_datetime - expected_exp).total_seconds()) < 60

    @patch('faproject.services.auth.datetime')
    def test_verify_expired_token(self, mock_datetime):
        """Test verification of expired token."""
        jwt_manager = JWTManager()

        # Create a token
        data = {"sub": "123"}
        token = jwt_manager.create_access_token(data)

        # Mock datetime to simulate time passing
        future_time = datetime.now(timezone.utc) + timedelta(hours=2)
        mock_datetime.now.return_value = future_time
        mock_datetime.fromtimestamp = datetime.fromtimestamp

        # Token should be expired
        with pytest.raises(Exception):
            jwt_manager.verify_token(token)

    def test_token_contains_issued_at(self):
        """Test that tokens contain issued at claim."""
        jwt_manager = JWTManager()
        data = {"sub": "123"}

        before_creation = datetime.now(timezone.utc)
        token = jwt_manager.create_access_token(data)
        after_creation = datetime.now(timezone.utc)

        decoded = jwt_manager.verify_token(token)

        assert "iat" in decoded

        iat_timestamp = decoded["iat"]
        iat_datetime = datetime.fromtimestamp(iat_timestamp, timezone.utc)

        # Should be between before and after creation
        assert before_creation <= iat_datetime <= after_creation

    def test_token_data_preservation(self):
        """Test that all provided data is preserved in token."""
        jwt_manager = JWTManager()
        data = {
            "sub": "123",
            "email": "test@example.com",
            "role": "admin",
            "username": "testuser",
            "custom_field": "custom_value"
        }

        token = jwt_manager.create_access_token(data)
        decoded = jwt_manager.verify_token(token)

        # All original data should be preserved
        for key, value in data.items():
            assert decoded[key] == value

    def test_different_tokens_for_same_data(self):
        """Test that creating tokens with same data produces different tokens."""
        jwt_manager = JWTManager()
        data = {"sub": "123", "email": "test@example.com"}

        token1 = jwt_manager.create_access_token(data)
        token2 = jwt_manager.create_access_token(data)

        # Tokens should be different due to different iat (issued at) times
        assert token1 != token2

        # But both should decode to similar data (except timestamps)
        decoded1 = jwt_manager.verify_token(token1)
        decoded2 = jwt_manager.verify_token(token2)

        assert decoded1["sub"] == decoded2["sub"]
        assert decoded1["email"] == decoded2["email"]

    def test_verify_access_token_as_refresh_token(self):
        """Test that access tokens cannot be verified as refresh tokens."""
        jwt_manager = JWTManager()
        data = {"sub": "123"}

        access_token = jwt_manager.create_access_token(data)

        # Should fail when trying to verify as refresh token
        with pytest.raises(Exception):
            jwt_manager.verify_token(access_token, is_refresh_token=True)

    def test_verify_refresh_token_as_access_token(self):
        """Test that refresh tokens cannot be verified as access tokens."""
        jwt_manager = JWTManager()
        data = {"sub": "123"}

        refresh_token = jwt_manager.create_refresh_token(data)

        # Should fail when trying to verify as access token
        with pytest.raises(Exception):
            jwt_manager.verify_token(refresh_token, is_refresh_token=False)