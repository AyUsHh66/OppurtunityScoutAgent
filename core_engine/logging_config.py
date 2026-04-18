"""
Structured logging configuration for Business Agent 2.0
Provides rotating file handlers, console output, and traceable logging
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional
from config import get_settings


class ContextFilter(logging.Filter):
    """Add contextual information like trace IDs to log records"""
    
    def __init__(self, trace_id: Optional[str] = None):
        super().__init__()
        self.trace_id = trace_id or "NO_TRACE"

    def filter(self, record):
        record.trace_id = self.trace_id
        return True


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
    }
    RESET = '\033[0m'

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logging(name: Optional[str] = None, trace_id: Optional[str] = None) -> logging.Logger:
    """
    Configure logging with rotating file handlers and console output
    
    Args:
        name: Logger name (usually __name__)
        trace_id: Optional trace ID for tracking requests
    
    Returns:
        Configured logger instance
    """
    settings = get_settings()
    logger = logging.getLogger(name or "business_agent")
    
    # Set logger level
    logger.setLevel(settings.logging.level.value)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.logging.file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Remove existing handlers to prevent duplicates
    logger.handlers.clear()
    
    # Create formatters
    if settings.logging.include_trace_id:
        file_format = "%(asctime)s - %(name)s - [%(trace_id)s] - %(levelname)s - %(message)s"
        console_format = "%(asctime)s - %(name)s - [%(trace_id)s] - %(levelname)s - %(message)s"
    else:
        file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    file_formatter = logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
    console_formatter = ColoredFormatter(console_format, datefmt="%H:%M:%S")
    
    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.logging.file_path,
            maxBytes=settings.logging.max_file_size_mb * 1024 * 1024,
            backupCount=settings.logging.backup_count
        )
        file_handler.setLevel(settings.logging.level.value)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file logging: {e}")
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.logging.level.value)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Add context filter
    context_filter = ContextFilter(trace_id)
    for handler in logger.handlers:
        handler.addFilter(context_filter)
    
    return logger


def get_logger(name: Optional[str] = None, trace_id: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance"""
    return setup_logging(name, trace_id)


# Create module-level logger
_module_logger = setup_logging(__name__)


def log_info(message: str, **kwargs):
    """Log info message"""
    _module_logger.info(message, **kwargs)


def log_error(message: str, exception: Optional[Exception] = None, **kwargs):
    """Log error message with optional exception"""
    if exception:
        _module_logger.error(f"{message}: {str(exception)}", exc_info=True, **kwargs)
    else:
        _module_logger.error(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log warning message"""
    _module_logger.warning(message, **kwargs)


def log_debug(message: str, **kwargs):
    """Log debug message"""
    _module_logger.debug(message, **kwargs)
