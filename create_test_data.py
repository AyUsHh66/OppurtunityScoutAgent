"""
Script to create test data that will actually match the hiring goal
"""
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import Qdrant
from langchain_core.documents import Document
from qdrant_client import QdrantClient

load_dotenv()

# Sample hiring posts that should score high
hiring_posts = [
    Document(
        page_content="""
        Title: Looking for a React Developer - Budget $5000
        
        Hi everyone! Our startup is urgently looking to hire a skilled React developer 
        for a 3-month project. We need someone who can build a modern e-commerce platform 
        with payment integration.
        
        Requirements:
        - 3+ years React experience
        - Knowledge of Node.js and MongoDB
        - Available to start immediately
        
        Budget: $5000-$7000 depending on experience
        Timeline: 3 months
        
        Please DM me if interested! We're ready to hire ASAP.
        """,
        metadata={
            "source": "reddit.com/r/forhire",
            "title": "Looking for React Developer",
            "company": "TechStartup Inc",
            "budget": "$5000-$7000",
            "ingest_timestamp": 1767107299.5071783
        }
    ),
    Document(
        page_content="""
        [HIRING] Full-Stack Web Developer Needed - $80/hour
        
        We're a growing digital agency looking for a talented full-stack developer
        to join our team on a contract basis.
        
        Project Details:
        - Build 3 client websites over the next 2 months
        - Tech stack: React, Next.js, TypeScript, PostgreSQL
        - Must have portfolio of previous work
        
        Rate: $80/hour, approximately 20 hours per week
        Location: Remote
        Start Date: Immediately
        
        This could turn into a long-term partnership for the right person!
        Email: hiring@digitalagency.com
        """,
        metadata={
            "source": "freelancer.com",
            "title": "Full-Stack Developer Position",
            "company": "Digital Agency Co",
            "rate": "$80/hour",
            "ingest_timestamp": 1767107299.5071783
        }
    ),
    Document(
        page_content="""
        URGENT: Need WordPress Developer This Week!
        
        Hey folks, I run a small marketing agency and we desperately need help
        with a WordPress site for a client. The previous developer disappeared
        and we need someone reliable.
        
        What we need:
        - Fix current WordPress site (theme customization issues)
        - Add e-commerce functionality with WooCommerce
        - Mobile responsiveness improvements
        
        Budget: $2000 for this project, but we have 5 more clients lined up
        if you do good work.
        
        Must be available to start THIS WEEK. Please reply with your portfolio!
        """,
        metadata={
            "source": "upwork.com",
            "title": "Urgent WordPress Developer",
            "company": "Marketing Solutions LLC",
            "budget": "$2000+",
            "urgency": "immediate",
            "ingest_timestamp": 1767107299.5071783
        }
    ),
    Document(
        page_content="""
        Web Development Project - E-learning Platform
        
        Our education company is looking for an experienced web developer to build
        a custom e-learning platform from scratch.
        
        Project Scope:
        - User authentication and profiles
        - Video course hosting and streaming
        - Payment processing (subscriptions)
        - Admin dashboard for content management
        
        Preferred Tech: Python/Django or Node.js backend, React frontend
        
        Budget: $15,000 - $20,000
        Timeline: 4-5 months
        
        We have funding secured and are ready to start immediately.
        Please send your proposal and previous work examples to: projects@edutech.com
        """,
        metadata={
            "source": "freelancer.com",
            "title": "E-learning Platform Development",
            "company": "EduTech Solutions",
            "budget": "$15,000-$20,000",
            "project_type": "full platform",
            "ingest_timestamp": 1767107299.5071783
        }
    )
]

# Create embeddings
embeddings = OllamaEmbeddings(
    model=os.getenv("OLLAMA_MODEL"),
    base_url=os.getenv("OLLAMA_BASE_URL")
)

# Connect to Qdrant and recreate collection
client = QdrantClient(url=os.getenv("QDRANT_URL"))
collection_name = os.getenv("QDRANT_COLLECTION_NAME")

# Delete existing collection
try:
    client.delete_collection(collection_name)
    print(f"✅ Deleted existing collection: {collection_name}")
except Exception as e:
    print(f"Collection doesn't exist or error: {e}")

# Create new collection with documents
print(f"\n📥 Creating collection with {len(hiring_posts)} hiring posts...")

qdrant = Qdrant.from_documents(
    hiring_posts,
    embeddings,
    url=os.getenv("QDRANT_URL"),
    collection_name=collection_name,
    force_recreate=True
)

print(f"✅ Successfully created collection with hiring-focused test data!")
print(f"\n📋 Test data includes:")
for i, doc in enumerate(hiring_posts, 1):
    print(f"  {i}. {doc.metadata.get('title')} - {doc.metadata.get('company')}")
print(f"\n🎯 Run the agent now to see high-scoring leads!")
