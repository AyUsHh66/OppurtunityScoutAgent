"""
Pytest configuration and fixtures for Business Agent 2.0
"""

import pytest
import os
from typing import Generator
from unittest.mock import AsyncMock, Mock

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "true"


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    from config import Settings, Environment, LLMConfig, DatabaseConfig
    
    return Settings(
        environment=Environment.DEVELOPMENT,
        debug=True,
        llm=LLMConfig(
            model="phi",
            base_url="http://localhost:11434",
            timeout=10,
        ),
        database=DatabaseConfig(
            url="http://localhost:6333",
            collection_name="test_collection",
        ),
    )


@pytest.fixture
def mock_notification_manager():
    """Mock notification manager"""
    manager = Mock()
    manager.send = AsyncMock(return_value=True)
    manager.queue_notification = Mock()
    manager.process_queue = Mock(return_value=0)
    manager.notification_queue = []
    return manager


@pytest.fixture
def api_key():
    """Test API key"""
    return "test-api-key-" + "x" * 32


@pytest.fixture
def auth_headers(api_key):
    """Auth headers for API requests"""
    return {"X-API-Key": api_key}


@pytest.fixture
def test_job_data():
    """Sample job data for testing"""
    return {
        "title": "Senior Python Developer",
        "company": "TechCorp",
        "description": "Looking for experienced Python developer",
        "salary_min": 100000,
        "salary_max": 150000,
        "url": "https://example.com/jobs/123",
        "posted_at": "2026-04-18T10:00:00Z",
    }


@pytest.fixture
def test_notification_data():
    """Sample notification data for testing"""
    return {
        "type": "job_opportunity",
        "title": "Senior Python Developer",
        "message": "Found matching job opportunity",
        "details": {
            "company": "TechCorp",
            "salary": "$100-150K",
        },
        "priority": "high",
    }


@pytest.fixture
def test_lead_data():
    """Sample lead data for testing"""
    return {
        "title": "Looking for web developer",
        "description": "Startup seeking experienced React developer",
        "company": "StartupXYZ",
        "source": "reddit",
    }
