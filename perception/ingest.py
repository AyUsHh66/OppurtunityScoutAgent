import os
import time
from dotenv import load_dotenv
from typing import List

from langchain_community.document_loaders import RSSFeedLoader, RedditPostsLoader
# --- NEW: Import the RecursiveUrlLoader and BeautifulSoup ---
from langchain_community.document_loaders import RecursiveUrlLoader
from bs4 import BeautifulSoup as Soup
# --- END NEW ---

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import Qdrant

# Load environment variables from.env file
load_dotenv()

# --- NEW: Custom extractor function for the web scraper ---
def custom_html_extractor(html: str) -> str:
    """
    A custom extractor that uses BeautifulSoup to parse the HTML
    and return only the text from the main content of the page.
    """
    soup = Soup(html, "lxml")
    # This is a generic approach. For specific sites, you might need to
    # inspect the HTML and find a more specific tag/class for the main content.
    # For example, look for <main>, <article>, or <div class="content">.
    body = soup.find("body")
    if body:
        return body.get_text(separator=" ", strip=True)
    return ""
# --- END NEW ---

def _get_embeddings_model() -> OllamaEmbeddings:
    """Initializes and returns the OllamaEmbeddings model."""
    return OllamaEmbeddings(
        model=os.getenv("OLLAMA_MODEL"),
        base_url=os.getenv("OLLAMA_BASE_URL")
    )

def process_and_store_documents(documents: List):
    """
    Processes and stores a list of documents in the Qdrant vector store.
    """
    if not documents:
        print("No new documents to process.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunked_docs = text_splitter.split_documents(documents)
    
    print(f"Generated {len(chunked_docs)} chunks from {len(documents)} documents.")

    embeddings = _get_embeddings_model()

    qdrant = Qdrant.from_documents(
        documents=chunked_docs,
        embedding=embeddings,
        url=os.getenv("QDRANT_URL"),
        collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
        force_recreate=False,
    )
    
    print(f"Successfully added {len(chunked_docs)} chunks to the '{os.getenv('QDRANT_COLLECTION_NAME')}' collection.")

def ingest_rss_feeds(urls: List[str]):
    """
    Loads documents from a list of RSS feeds, then processes and stores them.
    """
    print(f"Ingesting from RSS feeds: {urls}")
    loader = RSSFeedLoader(urls=urls, continue_on_failure=True)
    documents = loader.load()
    
    if not documents:
        print("No documents found in the RSS feeds.")
        return
        
    print(f"Loaded {len(documents)} documents from RSS feeds.")
    
    for doc in documents:
        doc.metadata["ingest_timestamp"] = time.time()
        
    process_and_store_documents(documents)

def ingest_reddit_posts(subreddits: List[str]):
    """
    Loads posts from a list of subreddits, then processes and stores them.
    """
    print(f"Ingesting from subreddits: {subreddits}")
    
    loader = RedditPostsLoader(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        search_queries=subreddits,
        mode="subreddit",
        categories=["new"],
        number_posts=25,
    )
    documents = loader.load()

    if not documents:
        print("No documents found in the specified subreddits.")
        return

    print(f"Loaded {len(documents)} documents from Reddit.")
    
    for doc in documents:
        doc.metadata["ingest_timestamp"] = time.time()
        
    process_and_store_documents(documents)

# --- NEW: Function specifically for scraping websites ---
def scrape_website(url: str):
    """
    Recursively scrapes a website starting from the given URL,
    then processes and stores the content.
    """
    print(f"Scraping website: {url}")
    loader = RecursiveUrlLoader(
        url=url,
        max_depth=2,  # How deep to crawl from the root URL
        extractor=custom_html_extractor,
        prevent_outside=True,  # Don't crawl links to other domains
        continue_on_failure=True,
    )
    documents = loader.load()

    if not documents:
        print(f"No documents found at {url}.")
        return

    print(f"Loaded {len(documents)} documents from {url}.")
    
    for doc in documents:
        doc.metadata["ingest_timestamp"] = time.time()
        
    process_and_store_documents(documents)
# --- END NEW ---


# --- UPDATED: Main block now calls the new scraping function for testing ---
if __name__ == "__main__":
    print("Running web scraping script for testing...")
    
    # Example blog post. Replace with a target URL for your use case.
    test_url = "https://lilianweng.github.io/posts/2023-06-23-agent/"
    
    scrape_website(test_url)
    
    print("Test web scraping complete.")
# --- END UPDATE ---