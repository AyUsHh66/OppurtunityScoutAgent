"""
Production-grade configuration management for Business Agent 2.0
Supports environment-based configuration with validation
"""

import os
from typing import Optional
from enum import Enum
from dotenv import load_dotenv
from dataclasses import dataclass, field

# Load environment variables
load_dotenv()


class Environment(str, Enum):
    """Application environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LLMConfig:
    """LLM Configuration"""
    model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "phi"))
    base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    timeout: int = 300
    temperature: float = 0.7
    top_p: float = 0.9

    def validate(self):
        """Validate LLM configuration"""
        if not self.model:
            raise ValueError("OLLAMA_MODEL is required")
        if not self.base_url:
            raise ValueError("OLLAMA_BASE_URL is required")


@dataclass
class DatabaseConfig:
    """Vector Database Configuration"""
    url: str = field(default_factory=lambda: os.getenv("QDRANT_URL", "http://localhost:6333"))
    collection_name: str = field(default_factory=lambda: os.getenv("QDRANT_COLLECTION_NAME", "opportunity_scout_collection"))
    timeout: int = 30
    max_retries: int = 3

    def validate(self):
        """Validate database configuration"""
        if not self.url:
            raise ValueError("QDRANT_URL is required")
        if not self.collection_name:
            raise ValueError("QDRANT_COLLECTION_NAME is required")


@dataclass
class APIConfig:
    """External API Configuration"""
    hunter_api_key: Optional[str] = field(default_factory=lambda: os.getenv("HUNTER_API_KEY"))
    reddit_client_id: Optional[str] = field(default_factory=lambda: os.getenv("REDDIT_CLIENT_ID"))
    reddit_client_secret: Optional[str] = field(default_factory=lambda: os.getenv("REDDIT_CLIENT_SECRET"))
    reddit_user_agent: str = "BusinessAgent2.0 (by your_username)"
    
    # Trello
    trello_api_key: Optional[str] = field(default_factory=lambda: os.getenv("TRELLO_API_KEY"))
    trello_token: Optional[str] = field(default_factory=lambda: os.getenv("TRELLO_TOKEN"))
    trello_board_id: Optional[str] = field(default_factory=lambda: os.getenv("TRELLO_BOARD_ID"))
    
    # Notion
    notion_api_key: Optional[str] = field(default_factory=lambda: os.getenv("NOTION_API_KEY"))
    notion_database_id: Optional[str] = field(default_factory=lambda: os.getenv("NOTION_DATABASE_ID"))
    
    # Discord
    discord_bot_token: Optional[str] = field(default_factory=lambda: os.getenv("DISCORD_BOT_TOKEN"))
    discord_channel_id: Optional[str] = field(default_factory=lambda: os.getenv("DISCORD_CHANNEL_ID"))
    
    # LinkedIn (for job scraping)
    linkedin_email: Optional[str] = field(default_factory=lambda: os.getenv("LINKEDIN_EMAIL"))
    linkedin_password: Optional[str] = field(default_factory=lambda: os.getenv("LINKEDIN_PASSWORD"))
    
    # Indeed
    indeed_api_key: Optional[str] = field(default_factory=lambda: os.getenv("INDEED_API_KEY"))

    # API Rate Limits
    api_timeout: int = 30
    api_retries: int = 3
    api_backoff_factor: float = 1.5


@dataclass
class NotificationConfig:
    """Notification System Configuration"""
    # Queue settings
    queue_backend: str = field(default_factory=lambda: os.getenv("QUEUE_BACKEND", "memory"))  # memory, redis
    redis_url: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_URL"))
    
    # Notification settings
    enable_discord: bool = field(default_factory=lambda: os.getenv("ENABLE_DISCORD", "true").lower() == "true")
    enable_email: bool = field(default_factory=lambda: os.getenv("ENABLE_EMAIL", "false").lower() == "true")
    enable_trello: bool = field(default_factory=lambda: os.getenv("ENABLE_TRELLO", "true").lower() == "true")
    enable_notion: bool = field(default_factory=lambda: os.getenv("ENABLE_NOTION", "false").lower() == "true")
    
    # Rate limiting
    notifications_per_hour: int = 100
    dedup_window_hours: int = 24
    
    # Batch settings
    batch_size: int = 10
    batch_timeout_seconds: int = 60


@dataclass
class JobSearchConfig:
    """Job Search Configuration"""
    # Sources to search
    sources: list = field(default_factory=lambda: os.getenv("JOB_SOURCES", "reddit,rss,hackernews").split(","))
    
    # Search filters
    min_salary: int = 50000
    location_preference: Optional[str] = field(default_factory=lambda: os.getenv("JOB_LOCATION"))
    job_types: list = field(default_factory=lambda: ["Remote", "Full-time", "Contract"])
    
    # Enrichment
    enrich_with_hunter: bool = field(default_factory=lambda: os.getenv("ENRICH_WITH_HUNTER", "true").lower() == "true")
    enrich_with_clearbit: bool = field(default_factory=lambda: os.getenv("ENRICH_WITH_CLEARBIT", "false").lower() == "true")
    
    # Polling
    poll_interval_minutes: int = 30
    max_results_per_search: int = 50


@dataclass
class LoggingConfig:
    """Logging Configuration"""
    level: LogLevel = field(default_factory=lambda: LogLevel(os.getenv("LOG_LEVEL", "INFO")))
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = field(default_factory=lambda: os.getenv("LOG_FILE", "logs/business_agent.log"))
    max_file_size_mb: int = 100
    backup_count: int = 10
    include_trace_id: bool = True


@dataclass
class CommonConfig:
    """Common Configuration Across Settings"""
    include_trace_id: bool = True


@dataclass
class Settings:
    """Main Settings Class - Singleton pattern"""
    
    environment: Environment = field(default_factory=lambda: Environment(os.getenv("ENVIRONMENT", "development")))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    # Sub-configurations
    llm: LLMConfig = field(default_factory=LLMConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    job_search: JobSearchConfig = field(default_factory=JobSearchConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def __post_init__(self):
        """Validate all configurations after initialization"""
        self.validate()

    def validate(self):
        """Validate all sub-configurations"""
        self.llm.validate()
        self.database.validate()
        # Add more validations as needed

    def to_dict(self) -> dict:
        """Convert settings to dictionary (safe for logging)"""
        return {
            "environment": self.environment.value,
            "debug": self.debug,
            "llm_model": self.llm.model,
            "database_url": self.database.url,
            "job_sources": self.job_search.sources,
            "notifications_enabled": {
                "discord": self.notifications.enable_discord,
                "email": self.notifications.enable_email,
                "trello": self.notifications.enable_trello,
                "notion": self.notifications.enable_notion,
            }
        }


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from environment"""
    global _settings
    _settings = Settings()
    return _settings
