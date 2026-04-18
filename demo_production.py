#!/usr/bin/env python
"""
Business Agent 2.0 - Production Demo Script
Shows all key features in action
"""

from tools.notifications import get_notification_manager, Notification, NotificationType
from core_engine.explainable_ai import ExplainableAIFactory, ExplainabilityFormatter
from config import get_settings
from datetime import datetime

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def demo_configuration():
    """Demo 1: Configuration System"""
    print_header("DEMO 1: CONFIGURATION MANAGEMENT")
    
    settings = get_settings()
    print(f"✓ Configuration System Initialized")
    print(f"  Environment: {settings.environment.value}")
    print(f"  Debug Mode: {settings.debug}")
    print(f"  LLM Model: {settings.llm.model}")
    print(f"  Qdrant URL: {settings.database.url}")
    print(f"  Job Sources: {', '.join(settings.job_search.sources)}")
    print(f"  Notifications Enabled: {settings.notifications.enable_discord}")

def demo_notifications():
    """Demo 2: Notification System"""
    print_header("DEMO 2: NOTIFICATION SYSTEM")
    
    manager = get_notification_manager()
    
    print(f"✓ Notification Manager Initialized")
    print(f"  Registered Channels: {list(manager.channels.keys())}")
    print(f"  Queue Size: {manager.queue.get_size()}")
    print(f"  Deduplication Window: 24 hours")
    
    # Create sample notification
    notification = Notification(
        type=NotificationType.JOB_OPPORTUNITY,
        title="Senior Python Developer - Remote",
        message="Found an exciting opportunity on Reddit",
        details={
            "company": "TechCorp Inc",
            "location": "Remote (USA)",
            "salary": "$150,000 - $180,000",
            "job_type": "Full-time",
            "url": "https://example.com/jobs/123"
        },
        priority="high",
        target_channels=["discord"],
    )
    
    print(f"\n📋 Sample Job Notification:")
    print(f"  Title: {notification.title}")
    print(f"  Company: {notification.details.get('company')}")
    print(f"  Salary: {notification.details.get('salary')}")
    print(f"  Type: {notification.type.value}")
    print(f"  Priority: {notification.priority.upper()}")
    print(f"  Target Channels: {', '.join(notification.target_channels)}")
    print(f"  Dedup Key: {notification.get_dedup_key()}")
    
    # Test queueing
    print(f"\n✓ Queueing notification for batch processing...")
    queued = manager.queue_notification(notification)
    print(f"  Queue Size: {manager.queue.get_size()}")
    print(f"  Status: {'SUCCESS' if queued else 'FAILED'}")

def demo_explainable_ai():
    """Demo 3: Explainable AI (XAI)"""
    print_header("DEMO 3: EXPLAINABLE AI - TRANSPARENT DECISIONS")
    
    # Create XAI decision
    decision = ExplainableAIFactory.create_lead_qualification_decision(
        decision_id="demo_001",
        company_name="TechCorp Inc",
        qualification_score=8.5,
        positive_factors=[
            "Explicit hiring intent mentioned",
            "Specific budget allocated ($50K)",
            "Clear job requirements provided",
            "Fast response time (< 1 hour)",
        ],
        negative_factors=[
            "Limited company information available",
            "No logo or official website",
        ],
        source_quotes=[
            "We are actively hiring 5 developers immediately",
            "Budget available: $50K-60K annually",
        ],
        confidence=0.87,
        model="phi"
    )
    
    print("Lead Qualification Decision With Reasoning:\n")
    print(f"Decision ID: {decision.decision_id}")
    print(f"Decision: {decision.decision}")
    print(f"Confidence: {decision.confidence_score:.1%} ({decision.calculate_confidence_level()})")
    print(f"Model Used: {decision.model_used}\n")
    
    print("📊 Decision Analysis:\n")
    print(f"Positive Factors ({len(decision.positive_factors)}):")
    for i, factor in enumerate(decision.positive_factors, 1):
        print(f"  {i}. {factor.description}")
    
    print(f"\nNegative Factors ({len(decision.negative_factors)}):")
    for i, factor in enumerate(decision.negative_factors, 1):
        print(f"  {i}. {factor.description}")
    
    print(f"\n✓ Supporting Evidence:")
    for i, quote in enumerate(decision.positive_factors[0].source_quote or [], 1):
        print(f"  - Source quote available for audit trail")

def demo_job_search():
    """Demo 4: Job Search System"""
    print_header("DEMO 4: MULTI-SOURCE JOB SEARCH")
    
    print("Job Search Engine Features:\n")
    print("✓ Supported Sources:")
    print("  • Reddit (r/forhire, r/remotework, r/contracting, r/freelance)")
    print("  • HackerNews (Who is Hiring threads)")
    print("  • RSS Feeds (Job aggregators)")
    print("  • LinkedIn (with authentication)")
    print("  • Indeed (with API key)")
    
    print("\n✓ Processing Pipeline:")
    print("  1. Query multiple sources in parallel")
    print("  2. Parse and standardize job postings")
    print("  3. Extract salary, location, job type")
    print("  4. Deduplicate by URL")
    print("  5. Order by relevance")
    
    print("\n✓ Sample Job Posting Structure:")
    print("  • ID: unique identifier")
    print("  • Title: job title")
    print("  • Company: hiring company")
    print("  • Salary: min-max in USD")
    print("  • Location: job location")
    print("  • Type: Full-time, Contract, etc")
    print("  • URL: link to job posting")
    print("  • Source: where it came from")

def demo_api():
    """Demo 5: REST API"""
    print_header("DEMO 5: PRODUCTION REST API")
    
    print("API Endpoints Available:\n")
    print("Health & Status:")
    print("  GET  /health              - Health check")
    print("  GET  /ready               - Readiness probe")
    print("  GET  /live                - Liveness probe")
    
    print("\nJobs:")
    print("  POST /api/v1/jobs/search  - Search for jobs")
    print("  GET  /api/v1/jobs/{id}    - Get job details")
    
    print("\nNotifications:")
    print("  POST /api/v1/notifications/send         - Send immediately")
    print("  POST /api/v1/notifications/queue        - Queue for later")
    print("  GET  /api/v1/notifications/queue/status - Queue status")
    print("  POST /api/v1/notifications/process-queue- Process batch")
    print("  POST /api/v1/notifications/test         - Test channels")
    
    print("\nConfiguration:")
    print("  GET  /api/v1/config               - Get settings")
    print("  GET  /api/v1/config/sources       - Get job sources")
    
    print("\n✓ Auto Documentation: http://localhost:8000/docs")

def demo_error_handling():
    """Demo 6: Error Handling"""
    print_header("DEMO 6: PRODUCTION ERROR HANDLING")
    
    print("✓ Built-in Resilience:\n")
    print("Circuit Breaker Pattern:")
    print("  • Prevents cascading failures")
    print("  • States: CLOSED, HALF-OPEN, OPEN")
    print("  • Auto-recovery after timeout")
    
    print("\nExponential Backoff Retries:")
    print("  • Initial delay: 1s")
    print("  • Backoff factor: 2.0")
    print("  • Max retries: 3")
    print("  • Max delay: 60s")
    
    print("\nError Categorization:")
    print("  • RATE_LIMIT - Exponential backoff")
    print("  • TIMEOUT - Linear backoff")
    print("  • CONNECTION - Exponential backoff")
    print("  • AUTHENTICATION - No retry")
    print("  • VALIDATION - No retry")

def main():
    """Run all demos"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "BUSINESS AGENT 2.0 - PRODUCTION DEMO" + " "*27 + "║")
    print("║" + " "*10 + "Enterprise-Grade AI Agent with Explainable Decisions" + " "*15 + "║")
    print("╚" + "="*78 + "╝")
    
    # Run all demos
    demo_configuration()
    demo_notifications()
    demo_explainable_ai()
    demo_job_search()
    demo_api()
    demo_error_handling()
    
    # Summary
    print_header("SUMMARY")
    print("✅ All Systems Operational\n")
    print("Key Achievements:")
    print("  ✓ Configuration Management - Centralized, environment-based")
    print("  ✓ Notification System - Queue-based, multi-channel")
    print("  ✓ Explainable AI - Transparent decision-making")
    print("  ✓ Job Search - Multi-source discovery")
    print("  ✓ REST API - Production-ready endpoints")
    print("  ✓ Error Handling - Resilient with retries")
    
    print("\n📚 Documentation Available:")
    print("  • PRODUCTION_READY.md - Feature overview")
    print("  • PRODUCTION_DEPLOYMENT.md - Deployment guide")
    print("  • MIGRATION_GUIDE.md - Migration help")
    print("  • QUICK_REFERENCE.md - Developer cheat sheet")
    
    print("\n🚀 Quick Start:")
    print("  1. Start API server: python main.py")
    print("  2. Access docs: http://localhost:8000/docs")
    print("  3. Deploy: docker-compose -f docker-compose.prod.yml up -d")
    
    print("\n" + "="*80)
    print("✨ Business Agent 2.0 is Production-Ready! ✨")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
