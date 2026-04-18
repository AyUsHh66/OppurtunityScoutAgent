"""
Security tests for Business Agent 2.0
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.security
class TestAPIKeyValidation:
    """Test API key validation"""
    
    def test_api_key_validator_valid_key(self):
        """Test validation of valid API key"""
        from middleware.security import APIKeyValidator
        
        validator = APIKeyValidator()
        
        # Create a valid key (32+ characters)
        valid_key = "x" * 32
        
        assert validator.validate_key(valid_key) is True
    
    def test_api_key_validator_invalid_short_key(self):
        """Test validation of short API key"""
        from middleware.security import APIKeyValidator
        
        validator = APIKeyValidator()
        invalid_key = "short"
        
        assert validator.validate_key(invalid_key) is False
    
    def test_api_key_validator_admin_key(self):
        """Test admin key bypasses validation"""
        from middleware.security import APIKeyValidator
        
        admin_key = "my-admin-key"
        validator = APIKeyValidator(admin_key=admin_key)
        
        assert validator.validate_key(admin_key) is True
    
    def test_api_key_validator_empty_key(self):
        """Test validation of empty API key"""
        from middleware.security import APIKeyValidator
        
        validator = APIKeyValidator()
        
        assert validator.validate_key("") is False
        assert validator.validate_key(None) is False


@pytest.mark.security
class TestRateLimiting:
    """Test rate limiting"""
    
    def test_rate_limiter_allows_under_limit(self):
        """Test rate limiter allows requests under limit"""
        from middleware.security import RateLimiter
        
        limiter = RateLimiter()
        client_id = "test-client"
        
        # First 60 requests should be allowed (default limit)
        for i in range(60):
            assert limiter.is_allowed(client_id, limit=60, window=60) is True
    
    def test_rate_limiter_blocks_over_limit(self):
        """Test rate limiter blocks requests over limit"""
        from middleware.security import RateLimiter
        
        limiter = RateLimiter()
        client_id = "test-client"
        
        # Use up limit
        for i in range(5):
            limiter.is_allowed(client_id, limit=5, window=60)
        
        # 6th request should be blocked
        assert limiter.is_allowed(client_id, limit=5, window=60) is False
    
    def test_rate_limiter_different_clients(self):
        """Test rate limiter tracks different clients separately"""
        from middleware.security import RateLimiter
        
        limiter = RateLimiter()
        
        # Use up limit for client 1
        for i in range(5):
            limiter.is_allowed("client-1", limit=5, window=60)
        
        # Client 2 should still have allowance
        assert limiter.is_allowed("client-2", limit=5, window=60) is True


@pytest.mark.security
class TestInputValidation:
    """Test input validation"""
    
    def test_job_search_input_validation(self):
        """Test job search input validation"""
        from models.schemas import JobSearchRequest
        from pydantic import ValidationError
        
        # Valid input
        request = JobSearchRequest(
            query="Python",
            source="reddit",
            limit=10,
        )
        assert request.query == "Python"
        
        # Invalid limit
        with pytest.raises(ValidationError):
            JobSearchRequest(
                query="Python",
                limit=1000,  # Over max
            )
    
    def test_notification_input_validation(self):
        """Test notification input validation"""
        from models.schemas import NotificationRequest
        from pydantic import ValidationError
        
        # Valid input
        request = NotificationRequest(
            type="job_opportunity",
            title="Test",
            message="Test message",
        )
        assert request.type == "job_opportunity"
        
        # Invalid type
        with pytest.raises(ValidationError):
            NotificationRequest(
                type="invalid_type",
                title="Test",
                message="Test message",
            )
    
    def test_notification_channel_validation(self):
        """Test notification channel validation"""
        from models.schemas import NotificationRequest
        from pydantic import ValidationError
        
        # Valid channels
        request = NotificationRequest(
            type="job_opportunity",
            title="Test",
            message="Test message",
            target_channels=["discord", "email"],
        )
        assert len(request.target_channels) == 2
        
        # Invalid channel
        with pytest.raises(ValidationError):
            NotificationRequest(
                type="job_opportunity",
                title="Test",
                message="Test message",
                target_channels=["invalid_channel"],
            )


@pytest.mark.security
class TestSecurityHeaders:
    """Test security headers"""
    
    def test_request_id_generation(self):
        """Test request ID generation"""
        from middleware.security import SecurityMiddleware
        from unittest.mock import Mock
        
        request = Mock()
        request.method = "GET"
        request.url.path = "/test"
        request.client = Mock(host="127.0.0.1")
        
        request_id = SecurityMiddleware._generate_request_id(request)
        
        # Should be 16 character hex string
        assert len(request_id) == 16
        assert all(c in "0123456789abcdef" for c in request_id)
    
    def test_request_id_uniqueness(self):
        """Test request IDs are unique"""
        from middleware.security import SecurityMiddleware
        from unittest.mock import Mock
        import time
        
        ids = set()
        
        for _ in range(10):
            request = Mock()
            request.method = "GET"
            request.url.path = "/test"
            request.client = Mock(host="127.0.0.1")
            
            request_id = SecurityMiddleware._generate_request_id(request)
            ids.add(request_id)
            time.sleep(0.001)  # Small delay for uniqueness
        
        assert len(ids) == 10  # All unique


@pytest.mark.security
class TestEnvironmentSecurity:
    """Test environment variable security"""
    
    def test_settings_validation(self, mock_settings):
        """Test settings validation"""
        # Should not raise
        mock_settings.validate()
    
    def test_sensitive_settings_not_logged(self, mock_settings):
        """Test sensitive settings are not logged"""
        settings_dict = mock_settings.to_dict()
        
        # API keys should not be in plain text
        assert "api_key" not in str(settings_dict).lower() or \
               all("***" in str(v) or v is None for v in settings_dict.values())
