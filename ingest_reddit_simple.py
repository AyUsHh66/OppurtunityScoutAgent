"""
Simple script to ingest real leads from Reddit
"""
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from langchain_community.document_loaders import RedditPostsLoader
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import Qdrant
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

print("\n" + "="*80)
print("  📥 INGESTING REAL LEADS FROM REDDIT")
print("="*80 + "\n")

# Subreddits to search
subreddits = ["forhire", "freelance", "hiring"]
print(f"Fetching from: {', '.join(subreddits)}")
print("Getting 25 most recent posts from each...\n")

try:
    # Load Reddit posts
    loader = RedditPostsLoader(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        search_queries=subreddits,
        mode="subreddit",
        categories=["new"],
        number_posts=25,
    )
    
    print("⏳ Fetching posts from Reddit...")
    documents = loader.load()
    
    if not documents:
        print("❌ No documents found")
        sys.exit(1)
    
    print(f"✅ Loaded {len(documents)} posts from Reddit\n")
    
    # Clean and add metadata (remove non-serializable objects)
    for doc in documents:
        # Remove problematic metadata fields
        if 'author' in doc.metadata:
            doc.metadata['author'] = str(doc.metadata['author'])
        
        # Remove any other reddit objects
        cleaned_metadata = {}
        for key, value in doc.metadata.items():
            if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                cleaned_metadata[key] = value
            else:
                cleaned_metadata[key] = str(value)
        
        doc.metadata = cleaned_metadata
        doc.metadata["ingest_timestamp"] = time.time()
        doc.metadata["source_type"] = "reddit"
    
    # Split into chunks
    print("📄 Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunked_docs = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunked_docs)} chunks\n")
    
    # Initialize embeddings
    print("🧠 Initializing embeddings...")
    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_MODEL"),
        base_url=os.getenv("OLLAMA_BASE_URL")
    )
    
    # Store in Qdrant
    print("💾 Storing in Qdrant vector database...")
    qdrant = Qdrant.from_documents(
        documents=chunked_docs,
        embedding=embeddings,
        url=os.getenv("QDRANT_URL"),
        collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
        force_recreate=False,  # Add to existing collection
    )
    
    print(f"\n✅ Successfully added {len(chunked_docs)} chunks to Qdrant!")
    print(f"   Collection: {os.getenv('QDRANT_COLLECTION_NAME')}")
    
    # Show sample of what was ingested
    print("\n" + "="*80)
    print("  📋 SAMPLE OF INGESTED POSTS")
    print("="*80 + "\n")
    
    for i, doc in enumerate(documents[:5], 1):
        title = doc.metadata.get('title', 'No title')
        print(f"{i}. {title[:70]}")
    
    print("\n" + "="*80)
    print("  🎉 INGESTION COMPLETE!")
    print("="*80)
    print("\nNext step: Run the agent to process these new leads!")
    print("  python core_engine/agent.py\n")
    
except Exception as e:
    print(f"\n❌ Error during ingestion: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
