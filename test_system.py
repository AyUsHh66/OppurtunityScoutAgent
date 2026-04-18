"""
Quick Test Script - Verify System Functionality
================================================
This script runs quick tests to ensure all components are working.  
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def test_ollama():
    """Test Ollama connection"""
    print("\n🧪 Testing Ollama...")
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            configured_model = os.getenv('OLLAMA_MODEL')
            
            print(f"✅ Ollama is running")
            print(f"   Available models: {', '.join(model_names[:5])}")
            print(f"   Configured model: {configured_model}")
            
            if configured_model in model_names or f"{configured_model}:latest" in model_names:
                print(f"   ✅ Configured model is available")
                return True
            else:
                print(f"   ⚠️  Configured model '{configured_model}' not found")
                print(f"   Run: ollama pull {configured_model}")
                return False
        else:
            print("❌ Ollama not responding properly")
            return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_qdrant():
    """Test Qdrant connection"""
    print("\n🧪 Testing Qdrant...")
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=os.getenv('QDRANT_URL'))
        collections = client.get_collections()
        collection_name = os.getenv('QDRANT_COLLECTION_NAME')
        
        print(f"✅ Qdrant is running")
        print(f"   URL: {os.getenv('QDRANT_URL')}")
        
        # Check if our collection exists
        collection_names = [c.name for c in collections.collections]
        if collection_name in collection_names:
            info = client.get_collection(collection_name)
            print(f"   ✅ Collection '{collection_name}' exists")
            print(f"   Documents: {info.points_count}")
            return True
        else:
            print(f"   ⚠️  Collection '{collection_name}' not found")
            print(f"   Run: python create_test_data.py")
            return False
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        print("   Run: docker-compose up -d")
        return False

def test_embeddings():
    """Test embedding generation"""
    print("\n🧪 Testing Embeddings...")
    try:
        from langchain_ollama import OllamaEmbeddings
        embeddings = OllamaEmbeddings(
            model=os.getenv('OLLAMA_MODEL'),
            base_url=os.getenv('OLLAMA_BASE_URL')
        )
        result = embeddings.embed_query("test query")
        print(f"✅ Embeddings working")
        print(f"   Dimension: {len(result)}")
        return True
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")
        return False

def test_retrieval():
    """Test document retrieval"""
    print("\n🧪 Testing Retrieval...")
    try:
        from langchain_qdrant import Qdrant
        from langchain_ollama import OllamaEmbeddings
        
        embeddings = OllamaEmbeddings(
            model=os.getenv('OLLAMA_MODEL'),
            base_url=os.getenv('OLLAMA_BASE_URL')
        )
        qdrant = Qdrant.from_existing_collection(
            embedding=embeddings,
            collection_name=os.getenv('QDRANT_COLLECTION_NAME'),
            url=os.getenv('QDRANT_URL'),
        )
        
        docs = qdrant.similarity_search("hire web developer", k=2)
        print(f"✅ Retrieval working")
        print(f"   Found {len(docs)} documents")
        if docs:
            print(f"   Top match: {docs[0].page_content[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        return False

def test_llm():
    """Test LLM inference"""
    print("\n🧪 Testing LLM Inference...")
    try:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            model=os.getenv('OLLAMA_MODEL'),
            base_url=os.getenv('OLLAMA_BASE_URL'),
            temperature=0
        )
        response = llm.invoke("Say 'Hello, I am working!' in exactly those words.")
        print(f"✅ LLM is working")
        print(f"   Response: {response.content[:100]}")
        return True
    except Exception as e:
        print(f"❌ LLM inference failed: {e}")
        return False

def test_api_keys():
    """Test API key configuration"""
    print("\n🧪 Testing API Keys...")
    
    keys = {
        'HUNTER_API_KEY': 'Hunter.io (enrichment)',
        'TRELLO_API_KEY': 'Trello (task management)',
        'DISCORD_BOT_TOKEN': 'Discord (notifications)',
        'REDDIT_CLIENT_ID': 'Reddit (data ingestion)',
    }
    
    configured = 0
    for key, desc in keys.items():
        value = os.getenv(key)
        if value and value != f"your_{key.lower()}":
            print(f"   ✅ {desc}")
            configured += 1
        else:
            print(f"   ⚠️  {desc} - not configured")
    
    print(f"\n   {configured}/{len(keys)} services configured")
    return configured > 0

def main():
    print("="*80)
    print("  🧪 BUSINESS AGENT 2.0 - SYSTEM TEST")
    print("="*80)
    
    tests = [
        ("Ollama", test_ollama),
        ("Qdrant", test_qdrant),
        ("Embeddings", test_embeddings),
        ("Retrieval", test_retrieval),
        ("LLM", test_llm),
        ("API Keys", test_api_keys),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*80)
    print("  📊 RESULTS SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n  Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All systems operational! Ready to run the agent.")
        print("\n  Next steps:")
        print("    1. Run: python run.py")
        print("    2. Or: python core_engine/agent.py")
    else:
        print("\n  ⚠️  Some systems need attention. Check errors above.")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
