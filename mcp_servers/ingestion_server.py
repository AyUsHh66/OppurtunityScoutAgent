"""
MCP Server for Data Ingestion
Provides tools for ingesting data from various sources and storing in Qdrant.
"""

import os
import time
import json
from typing import Any
from dotenv import load_dotenv

from langchain_community.document_loaders import RSSFeedLoader, RedditPostsLoader, RecursiveUrlLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import Qdrant
from bs4 import BeautifulSoup as Soup

load_dotenv()

# MCP Server Setup
import mcp.server.stdio
from mcp.types import TextContent, Tool
import mcp.types as types


class IngestionServer:
    def __init__(self):
        self.server = mcp.server.stdio.StdioServer()
        self.setup_routes()

    def setup_routes(self):
        """Setup MCP tools and handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                types.Tool(
                    name="ingest_rss_feeds",
                    description="Ingest documents from RSS feed URLs and store in Qdrant vector database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of RSS feed URLs to ingest"
                            }
                        },
                        "required": ["urls"]
                    }
                ),
                types.Tool(
                    name="ingest_reddit",
                    description="Ingest posts from Reddit subreddits and store in Qdrant",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "subreddits": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of subreddit names to ingest"
                            }
                        },
                        "required": ["subreddits"]
                    }
                ),
                types.Tool(
                    name="scrape_website",
                    description="Recursively scrape a website and store content in Qdrant",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The starting URL to scrape"
                            },
                            "max_depth": {
                                "type": "integer",
                                "description": "Maximum crawl depth (default: 2)",
                                "default": 2
                            }
                        },
                        "required": ["url"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> Any:
            if name == "ingest_rss_feeds":
                return await self._ingest_rss_feeds(arguments["urls"])
            elif name == "ingest_reddit":
                return await self._ingest_reddit(arguments["subreddits"])
            elif name == "scrape_website":
                max_depth = arguments.get("max_depth", 2)
                return await self._scrape_website(arguments["url"], max_depth)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _ingest_rss_feeds(self, urls: list[str]) -> dict:
        """Ingest RSS feeds"""
        try:
            print(f"Ingesting from RSS feeds: {urls}")
            loader = RSSFeedLoader(urls=urls, continue_on_failure=True)
            documents = loader.load()
            
            if not documents:
                return {"status": "error", "message": "No documents found in RSS feeds"}
            
            for doc in documents:
                doc.metadata["ingest_timestamp"] = time.time()
                doc.metadata["source_type"] = "rss"
            
            self._process_and_store_documents(documents)
            return {
                "status": "success",
                "message": f"Successfully ingested {len(documents)} documents from RSS feeds",
                "document_count": len(documents)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _ingest_reddit(self, subreddits: list[str]) -> dict:
        """Ingest Reddit posts"""
        try:
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
                return {"status": "error", "message": "No documents found in Reddit"}
            
            for doc in documents:
                doc.metadata["ingest_timestamp"] = time.time()
                doc.metadata["source_type"] = "reddit"
            
            self._process_and_store_documents(documents)
            return {
                "status": "success",
                "message": f"Successfully ingested {len(documents)} documents from Reddit",
                "document_count": len(documents)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _scrape_website(self, url: str, max_depth: int = 2) -> dict:
        """Scrape website"""
        try:
            print(f"Scraping website: {url}")
            loader = RecursiveUrlLoader(
                url=url,
                max_depth=max_depth,
                extractor=self._custom_html_extractor,
                prevent_outside=True,
                continue_on_failure=True,
            )
            documents = loader.load()
            
            if not documents:
                return {"status": "error", "message": f"No documents found at {url}"}
            
            for doc in documents:
                doc.metadata["ingest_timestamp"] = time.time()
                doc.metadata["source_type"] = "website"
            
            self._process_and_store_documents(documents)
            return {
                "status": "success",
                "message": f"Successfully ingested {len(documents)} documents from {url}",
                "document_count": len(documents)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _process_and_store_documents(self, documents: list):
        """Process documents and store in Qdrant"""
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
        
        embeddings = OllamaEmbeddings(
            model=os.getenv("OLLAMA_MODEL"),
            base_url=os.getenv("OLLAMA_BASE_URL")
        )
        
        qdrant = Qdrant.from_documents(
            documents=chunked_docs,
            embedding=embeddings,
            url=os.getenv("QDRANT_URL"),
            collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
            force_recreate=False,
        )
        
        print(f"Successfully added {len(chunked_docs)} chunks to Qdrant.")

    def _custom_html_extractor(self, html: str) -> str:
        """Extract text from HTML"""
        soup = Soup(html, "lxml")
        body = soup.find("body")
        if body:
            return body.get_text(separator=" ", strip=True)
        return ""

    async def run(self):
        """Run the MCP server"""
        async with self.server:
            pass


if __name__ == "__main__":
    import asyncio
    server = IngestionServer()
    asyncio.run(server.run())
