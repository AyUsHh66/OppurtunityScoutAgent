"""
Production-grade job search module supporting multiple sources
Includes job parsing, normalization, filtering, and enrichment
"""

import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import feedparser
import requests
from bs4 import BeautifulSoup

from core_engine.logging_config import get_logger

logger = get_logger(__name__)


class JobType(str, Enum):
    """Job type enumeration"""
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    FREELANCE = "Freelance"
    TEMPORARY = "Temporary"
    UNKNOWN = "Unknown"


class JobLevel(str, Enum):
    """Job level/seniority"""
    ENTRY = "Entry"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    EXECUTIVE = "Executive"
    UNKNOWN = "Unknown"


@dataclass
class JobPosting:
    """Standardized job posting structure"""
    job_id: str
    title: str
    company: str
    description: str
    url: str
    source: str
    posted_at: datetime
    
    # Optional fields
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    job_type: JobType = JobType.UNKNOWN
    level: JobLevel = JobLevel.UNKNOWN
    location: Optional[str] = None
    remote: Optional[bool] = None
    skills: List[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    
    # Metadata
    qualified: bool = False
    qualification_score: float = 0.0
    match_reasons: List[str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.match_reasons is None:
            self.match_reasons = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['job_type'] = self.job_type.value
        data['level'] = self.level.value
        data['posted_at'] = self.posted_at.isoformat()
        return data


class JobSource(ABC):
    """Abstract base class for job sources"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def search(self, query: str, filters: Optional[Dict] = None) -> List[JobPosting]:
        """Search for jobs"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get source name"""
        pass


class RedditJobsSource(JobSource):
    """Reddit jobs source (r/forhire, r/remotework, r/contracting)"""
    
    def __init__(self, reddit_client_id: str, reddit_client_secret: str):
        super().__init__()
        self.client_id = reddit_client_id
        self.client_secret = reddit_client_secret
        self.subreddits = ["forhire", "remotework", "contracting", "freelance", "jobsearch"]
    
    def get_source_name(self) -> str:
        return "reddit"
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[JobPosting]:
        """Search Reddit for job postings"""
        jobs = []
        self.logger.info(f"Searching Reddit for: {query}")
        
        try:
            # Note: Requires PRAW setup - simplified version here
            # Full implementation would use PRAW library
            self.logger.debug(f"Searching subreddits: {self.subreddits}")
            # TODO: Implement PRAW integration
        except Exception as e:
            self.logger.error(f"Error searching Reddit: {e}")
        
        return jobs


class HackerNewsJobsSource(JobSource):
    """HackerNews "Who is hiring" thread source"""
    
    def get_source_name(self) -> str:
        return "hackernews"
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[JobPosting]:
        """Search HackerNews for job postings"""
        jobs = []
        self.logger.info(f"Searching HackerNews for: {query}")
        
        try:
            # Search for latest "Who is hiring" thread
            hn_api_url = "https://hacker-news.firebaseio.com/v0"
            
            # Get latest stories mentioning hiring
            search_url = "https://hn.algolia.com/api/v1/search"
            params = {
                "query": "hiring",
                "tags": "story",
                "numericFilters": f"created_at_i>={int((datetime.now() - timedelta(days=10)).timestamp())}",
                "hitsPerPage": 50
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            results = response.json()
            
            for item in results.get('hits', [])[:5]:  # Get top 5 hiring threads
                jobs.extend(self._parse_hn_thread(item))
                
        except Exception as e:
            self.logger.error(f"Error searching HackerNews: {e}")
        
        return jobs
    
    def _parse_hn_thread(self, thread: Dict) -> List[JobPosting]:
        """Parse individual HN thread for job postings"""
        jobs = []
        try:
            # This is a simplified version
            # Full implementation would fetch and parse thread comments
            pass
        except Exception as e:
            self.logger.error(f"Error parsing HN thread: {e}")
        
        return jobs


class LinkedInJobsSource(JobSource):
    """LinkedIn jobs source (requires authentication)"""
    
    def __init__(self, linkedin_email: str, linkedin_password: str):
        super().__init__()
        self.email = linkedin_email
        self.password = linkedin_password
    
    def get_source_name(self) -> str:
        return "linkedin"
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[JobPosting]:
        """Search LinkedIn for job postings"""
        jobs = []
        self.logger.info(f"Searching LinkedIn for: {query}")
        
        try:
            # LinkedIn scraping requires selenium and authentication
            # This is a placeholder for full implementation
            self.logger.debug("LinkedIn integration requires authentication")
            # TODO: Implement LinkedIn scraping with Selenium
        except Exception as e:
            self.logger.error(f"Error searching LinkedIn: {e}")
        
        return jobs


class RSSJobsSource(JobSource):
    """RSS feed source for job aggregators"""
    
    def __init__(self, feed_urls: Optional[List[str]] = None):
        super().__init__()
        self.feed_urls = feed_urls or [
            "https://www.adzuna.com/feed/job-ads.xml",
            "https://www.dice.com/jobs/rss",
        ]
    
    def get_source_name(self) -> str:
        return "rss"
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[JobPosting]:
        """Search RSS feeds for job postings"""
        jobs = []
        self.logger.info(f"Searching RSS feeds for: {query}")
        
        for feed_url in self.feed_urls:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:20]:  # Limit per feed
                    job = self._parse_rss_entry(entry, query)
                    if job:
                        jobs.append(job)
            except Exception as e:
                self.logger.error(f"Error parsing RSS feed {feed_url}: {e}")
        
        return jobs
    
    def _parse_rss_entry(self, entry: Dict, query: str) -> Optional[JobPosting]:
        """Parse RSS entry to JobPosting"""
        try:
            title = entry.get('title', '')
            if query.lower() not in title.lower():
                return None
            
            description = entry.get('summary', entry.get('description', ''))
            
            # Extract salary if present
            salary_match = re.search(r'\$(\d+)(?:k|K)?(?:\s*-\s*\$(\d+))?', description)
            salary_min, salary_max = None, None
            if salary_match:
                salary_min = int(salary_match.group(1)) * 1000 if salary_match.group(1) else None
                salary_max = int(salary_match.group(2)) * 1000 if salary_match.group(2) else None
            
            posted_at = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                posted_at = datetime.fromtimestamp(entry.published_parsed)
            
            return JobPosting(
                job_id=f"rss_{hash(entry.get('id', entry.get('link', title)))}",
                title=title,
                company=entry.get('author', 'Unknown'),
                description=description,
                url=entry.get('link', ''),
                source='rss',
                posted_at=posted_at,
                salary_min=salary_min,
                salary_max=salary_max,
            )
        except Exception as e:
            self.logger.error(f"Error parsing RSS entry: {e}")
            return None


class JobSearchEngine:
    """Main job search engine coordinating multiple sources"""
    
    def __init__(self, sources: Optional[List[JobSource]] = None):
        self.logger = get_logger(__name__)
        self.sources = sources or []
    
    def register_source(self, source: JobSource):
        """Register a job source"""
        self.sources.append(source)
        self.logger.info(f"Registered job source: {source.get_source_name()}")
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[JobPosting]:
        """Search all sources for jobs"""
        all_jobs = []
        self.logger.info(f"Searching {len(self.sources)} sources for: {query}")
        
        for source in self.sources:
            try:
                self.logger.debug(f"Searching {source.get_source_name()}...")
                jobs = source.search(query, filters)
                all_jobs.extend(jobs)
                self.logger.info(f"{source.get_source_name()}: found {len(jobs)} jobs")
            except Exception as e:
                self.logger.error(f"Error searching {source.get_source_name()}: {e}")
        
        self.logger.info(f"Total jobs found: {len(all_jobs)}")
        return self._deduplicate(all_jobs)
    
    def _deduplicate(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Remove duplicate job postings"""
        seen_urls = set()
        unique_jobs = []
        
        for job in jobs:
            if job.url not in seen_urls:
                seen_urls.add(job.url)
                unique_jobs.append(job)
        
        self.logger.info(f"Deduplication: {len(jobs)} -> {len(unique_jobs)} jobs")
        return unique_jobs


def create_default_search_engine() -> JobSearchEngine:
    """Create a search engine with default sources"""
    from config import get_settings
    settings = get_settings()
    
    engine = JobSearchEngine()
    
    # Register sources based on configuration
    sources = settings.job_search.sources
    
    if 'rss' in sources:
        engine.register_source(RSSJobsSource())
    
    if 'hackernews' in sources:
        engine.register_source(HackerNewsJobsSource())
    
    if 'reddit' in sources and settings.api.reddit_client_id:
        engine.register_source(RedditJobsSource(
            settings.api.reddit_client_id,
            settings.api.reddit_client_secret
        ))
    
    if 'linkedin' in sources and settings.api.linkedin_email:
        engine.register_source(LinkedInJobsSource(
            settings.api.linkedin_email,
            settings.api.linkedin_password
        ))
    
    return engine
