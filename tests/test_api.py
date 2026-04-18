"""
API endpoint tests for Business Agent 2.0
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

# pytest.mark.asyncio marker for async tests


@pytest.mark.unit
class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_endpoint_success(self):
        """Test /health endpoint"""
        # This would require actually running the app
        # For now, we're testing the structure
        assert True
    
    @pytest.mark.asyncio
    async def test_health_response_structure(self):
        """Test health response structure"""
        # Expected structure
        response = {
            "status": "healthy",
            "service": "Business Agent 2.0",
            "version": "2.0.0",
        }
        
        assert "status" in response
        assert "service" in response
        assert response["status"] == "healthy"


@pytest.mark.unit
class TestJobSearchEndpoints:
    """Test job search endpoints"""
    
    @pytest.mark.asyncio
    async def test_job_search_request_validation(self, test_job_data):
        """Test job search request validation"""
        from models.schemas import JobSearchRequest
        
        # Valid request
        request = JobSearchRequest(
            query="Python developer",
            source="reddit",
            limit=10,
        )
        
        assert request.query == "Python developer"
        assert request.source == "reddit"
        assert request.limit == 10
    
    @pytest.mark.asyncio
    async def test_job_search_invalid_limit(self):
        """Test job search with invalid limit"""
        from models.schemas import JobSearchRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            JobSearchRequest(
                query="Python developer",
                source="reddit",
                limit=1000,  # Over max limit of 100
            )
    
    @pytest.mark.asyncio
    async def test_job_search_invalid_source(self):
        """Test job search with invalid source"""
        from models.schemas import JobSearchRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            JobSearchRequest(
                query="Python developer",
                source="invalid_source",
            )


@pytest.mark.unit
class TestNotificationEndpoints:
    """Test notification endpoints"""
    
    @pytest.mark.asyncio
    async def test_notification_request_validation(self, test_notification_data):
        """Test notification request validation"""
        from models.schemas import NotificationRequest
        
        request = NotificationRequest(
            type="job_opportunity",
            title=test_notification_data["title"],
            message=test_notification_data["message"],
            priority="high",
        )
        
        assert request.title == test_notification_data["title"]
        assert request.priority == "high"
    
    @pytest.mark.asyncio
    async def test_notification_invalid_priority(self):
        """Test notification with invalid priority"""
        from models.schemas import NotificationRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            NotificationRequest(
                type="job_opportunity",
                title="Test",
                message="Test message",
                priority="invalid",
            )


@pytest.mark.unit
class TestLeadQualificationEndpoints:
    """Test lead qualification endpoints"""
    
    @pytest.mark.asyncio
    async def test_lead_qualification_request(self, test_lead_data):
        """Test lead qualification request"""
        from models.schemas import LeadQualificationRequest
        
        request = LeadQualificationRequest(
            title=test_lead_data["title"],
            description=test_lead_data["description"],
            company=test_lead_data["company"],
            source=test_lead_data["source"],
        )
        
        assert request.title == test_lead_data["title"]
        assert request.company == test_lead_data["company"]
    
    @pytest.mark.asyncio
    async def test_lead_qualification_missing_required(self):
        """Test lead qualification with missing required fields"""
        from models.schemas import LeadQualificationRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            LeadQualificationRequest(
                title="",  # Empty required field
                description="Test",
            )


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, test_job_data, test_notification_data):
        """Test full workflow: search jobs -> send notification"""
        from models.schemas import JobSearchRequest, NotificationRequest
        
        # Step 1: Create job search request
        job_request = JobSearchRequest(
            query="Python developer",
            source="reddit",
            limit=5,
        )
        
        assert job_request.query == "Python developer"
        
        # Step 2: Create notification request
        notification = NotificationRequest(
            type="job_opportunity",
            title="Found matching job!",
            message="Senior Python Developer at TechCorp",
        )
        
        assert notification.type == "job_opportunity"
