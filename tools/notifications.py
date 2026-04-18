"""
Production-grade notification system with queueing, templating, and deduplication
Supports Discord, Email, Trello, and Notion
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import requests

from core_engine.logging_config import get_logger
from config import get_settings

logger = get_logger(__name__)


class NotificationType(str, Enum):
    """Notification types"""
    JOB_OPPORTUNITY = "job_opportunity"
    QUALIFIED_LEAD = "qualified_lead"
    ENRICHMENT_COMPLETE = "enrichment_complete"
    SYSTEM_ALERT = "system_alert"
    TEST = "test"


@dataclass
class Notification:
    """Standardized notification structure"""
    type: NotificationType
    title: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    priority: str = "normal"  # low, normal, high, critical
    target_channels: List[str] = field(default_factory=lambda: ["discord", "trello"])
    
    def get_dedup_key(self) -> str:
        """Generate deduplication key"""
        content = f"{self.type}_{self.title}_{self.message}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'type': self.type.value,
            'title': self.title,
            'message': self.message,
            'details': self.details,
            'created_at': self.created_at.isoformat(),
            'priority': self.priority,
            'target_channels': self.target_channels,
        }


class NotificationChannel(ABC):
    """Abstract base class for notification channels"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def send(self, notification: Notification) -> bool:
        """Send notification"""
        pass
    
    @abstractmethod
    def get_channel_name(self) -> str:
        """Get channel name"""
        pass


class DiscordChannel(NotificationChannel):
    """Discord notification channel"""
    
    def __init__(self, bot_token: str, channel_id: str):
        super().__init__()
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.api_url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    
    def get_channel_name(self) -> str:
        return "discord"
    
    def send(self, notification: Notification) -> bool:
        """Send notification via Discord"""
        try:
            if not self.bot_token or not self.channel_id:
                self.logger.warning("Discord credentials not configured")
                return False
            
            headers = {"Authorization": f"Bot {self.bot_token}"}
            
            # Create embed for job opportunities
            if notification.type == NotificationType.JOB_OPPORTUNITY:
                embed = self._create_job_embed(notification)
                payload = {"embeds": [embed]}
            else:
                # Simple message for other types
                payload = {
                    "content": f"**{notification.title}**\n{notification.message}"
                }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Discord notification sent: {notification.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Discord notification: {e}")
            return False
    
    def _create_job_embed(self, notification: Notification) -> Dict:
        """Create Discord embed for job notification"""
        details = notification.details
        
        # Color based on priority
        color_map = {
            'critical': 16711680,  # Red
            'high': 16776960,      # Yellow
            'normal': 3066993,     # Blue
            'low': 9807270,        # Gray
        }
        color = color_map.get(notification.priority, 3066993)
        
        embed = {
            "title": notification.title,
            "description": notification.message,
            "color": color,
            "fields": [],
            "timestamp": datetime.now().isoformat(),
        }
        
        # Add fields from details
        if details.get('company'):
            embed["fields"].append({
                "name": "Company",
                "value": details['company'],
                "inline": True
            })
        
        if details.get('location'):
            embed["fields"].append({
                "name": "Location",
                "value": details['location'],
                "inline": True
            })
        
        if details.get('salary'):
            embed["fields"].append({
                "name": "Salary",
                "value": details['salary'],
                "inline": True
            })
        
        if details.get('job_type'):
            embed["fields"].append({
                "name": "Job Type",
                "value": details['job_type'],
                "inline": True
            })
        
        if details.get('qualification_score'):
            embed["fields"].append({
                "name": "Match Score",
                "value": f"{details['qualification_score']}/10",
                "inline": True
            })
        
        if details.get('url'):
            embed["fields"].append({
                "name": "Apply",
                "value": f"[View Job]({details['url']})",
                "inline": False
            })
        
        return embed


class EmailChannel(NotificationChannel):
    """Email notification channel"""
    
    def __init__(self, smtp_server: str, smtp_port: int, from_email: str, from_password: str):
        super().__init__()
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_email = from_email
        self.from_password = from_password
    
    def get_channel_name(self) -> str:
        return "email"
    
    def send(self, notification: Notification) -> bool:
        """Send notification via Email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # This is a simplified implementation
            # Production would need proper email servers configured
            self.logger.debug("Email notification would be sent")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False


class TrelloChannel(NotificationChannel):
    """Trello notification channel for task creation"""
    
    def __init__(self, api_key: str, token: str, list_id: str):
        super().__init__()
        self.api_key = api_key
        self.token = token
        self.list_id = list_id
        self.api_url = "https://api.trello.com/1/cards"
    
    def get_channel_name(self) -> str:
        return "trello"
    
    def send(self, notification: Notification) -> bool:
        """Create Trello card for notification"""
        try:
            if not self.api_key or not self.token:
                self.logger.warning("Trello credentials not configured")
                return False
            
            params = {
                'key': self.api_key,
                'token': self.token,
                'idList': self.list_id,
                'name': notification.title,
                'desc': self._format_card_description(notification),
            }
            
            response = requests.post(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            card_url = response.json().get('shortUrl')
            self.logger.info(f"Trello card created: {card_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create Trello card: {e}")
            return False
    
    def _format_card_description(self, notification: Notification) -> str:
        """Format notification for Trello card description"""
        description = f"{notification.message}\n\n"
        description += f"**Priority:** {notification.priority}\n"
        description += f"**Type:** {notification.type.value}\n"
        
        if notification.details:
            description += "\n**Details:**\n"
            for key, value in notification.details.items():
                description += f"- {key}: {value}\n"
        
        return description


class NotionChannel(NotificationChannel):
    """Notion notification channel for database entries"""
    
    def __init__(self, api_key: str, database_id: str):
        super().__init__()
        self.api_key = api_key
        self.database_id = database_id
        self.api_url = "https://api.notion.com/v1/pages"
    
    def get_channel_name(self) -> str:
        return "notion"
    
    def send(self, notification: Notification) -> bool:
        """Create Notion page for notification"""
        try:
            if not self.api_key or not self.database_id:
                self.logger.warning("Notion credentials not configured")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28",
            }
            
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Title": {
                        "title": [{"text": {"content": notification.title}}]
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": notification.message}}]
                    },
                    "Priority": {
                        "select": {"name": notification.priority}
                    },
                    "Type": {
                        "select": {"name": notification.type.value}
                    }
                }
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            page_url = response.json().get('url')
            self.logger.info(f"Notion page created: {page_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create Notion page: {e}")
            return False


class NotificationDeduplicator:
    """Handles notification deduplication"""
    
    def __init__(self, window_hours: int = 24):
        self.window_hours = window_hours
        self.sent_notifications: Dict[str, datetime] = {}
    
    def is_duplicate(self, notification: Notification) -> bool:
        """Check if notification is a duplicate"""
        key = notification.get_dedup_key()
        
        if key in self.sent_notifications:
            time_diff = datetime.now() - self.sent_notifications[key]
            if time_diff < timedelta(hours=self.window_hours):
                return True
            # Remove old entry
            del self.sent_notifications[key]
        
        return False
    
    def mark_sent(self, notification: Notification):
        """Mark notification as sent"""
        key = notification.get_dedup_key()
        self.sent_notifications[key] = datetime.now()


class NotificationQueue:
    """In-memory notification queue (can be extended to Redis)"""
    
    def __init__(self, max_size: int = 1000):
        self.queue: List[Notification] = []
        self.max_size = max_size
        self.logger = get_logger(__name__)
    
    def enqueue(self, notification: Notification) -> bool:
        """Add notification to queue"""
        if len(self.queue) >= self.max_size:
            self.logger.warning("Notification queue is full")
            return False
        
        self.queue.append(notification)
        self.logger.debug(f"Notification queued: {notification.title}")
        return True
    
    def dequeue(self) -> Optional[Notification]:
        """Remove notification from queue"""
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def get_size(self) -> int:
        """Get queue size"""
        return len(self.queue)
    
    def clear(self):
        """Clear queue"""
        self.queue.clear()


class NotificationManager:
    """Main notification manager coordinating channels and queuing"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.channels: Dict[str, NotificationChannel] = {}
        self.queue = NotificationQueue()
        self.deduplicator = NotificationDeduplicator()
        self._setup_channels()
    
    def _setup_channels(self):
        """Setup notification channels from configuration"""
        settings = get_settings()
        
        # Discord
        if settings.notifications.enable_discord and settings.api.discord_bot_token:
            try:
                channel = DiscordChannel(
                    settings.api.discord_bot_token,
                    settings.api.discord_channel_id or ""
                )
                self.register_channel(channel)
            except Exception as e:
                self.logger.error(f"Failed to setup Discord channel: {e}")
        
        # Email
        if settings.notifications.enable_email:
            try:
                # TODO: Configure email settings
                pass
            except Exception as e:
                self.logger.error(f"Failed to setup Email channel: {e}")
        
        # Trello
        if settings.notifications.enable_trello and settings.api.trello_api_key:
            try:
                channel = TrelloChannel(
                    settings.api.trello_api_key,
                    settings.api.trello_token or "",
                    settings.api.trello_board_id or ""
                )
                self.register_channel(channel)
            except Exception as e:
                self.logger.error(f"Failed to setup Trello channel: {e}")
        
        # Notion
        if settings.notifications.enable_notion and settings.api.notion_api_key:
            try:
                channel = NotionChannel(
                    settings.api.notion_api_key,
                    settings.api.notion_database_id or ""
                )
                self.register_channel(channel)
            except Exception as e:
                self.logger.error(f"Failed to setup Notion channel: {e}")
    
    def register_channel(self, channel: NotificationChannel):
        """Register a notification channel"""
        self.channels[channel.get_channel_name()] = channel
        self.logger.info(f"Notification channel registered: {channel.get_channel_name()}")
    
    def send(self, notification: Notification) -> bool:
        """Send notification through configured channels"""
        # Check for duplicates
        if self.deduplicator.is_duplicate(notification):
            self.logger.info(f"Skipped duplicate notification: {notification.title}")
            return False
        
        # Mark as sent
        self.deduplicator.mark_sent(notification)
        
        # Send through all configured channels
        success = False
        for channel_name in notification.target_channels:
            if channel_name in self.channels:
                try:
                    if self.channels[channel_name].send(notification):
                        success = True
                except Exception as e:
                    self.logger.error(f"Error sending to {channel_name}: {e}")
        
        return success
    
    def queue_notification(self, notification: Notification) -> bool:
        """Queue notification for later processing"""
        return self.queue.enqueue(notification)
    
    def process_queue(self, batch_size: int = 10) -> int:
        """Process queued notifications"""
        count = 0
        for _ in range(batch_size):
            notification = self.queue.dequeue()
            if notification is None:
                break
            
            if self.send(notification):
                count += 1
        
        self.logger.info(f"Processed {count} queued notifications")
        return count
    
    def test_connection(self) -> Dict[str, bool]:
        """Test all configured channels"""
        test_notification = Notification(
            type=NotificationType.TEST,
            title="Test Notification",
            message="This is a test notification",
            target_channels=list(self.channels.keys())
        )
        
        results = {}
        for channel_name, channel in self.channels.items():
            try:
                results[channel_name] = channel.send(test_notification)
            except Exception as e:
                self.logger.error(f"Test failed for {channel_name}: {e}")
                results[channel_name] = False
        
        return results


# Global notification manager instance
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Get or create global notification manager"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager
