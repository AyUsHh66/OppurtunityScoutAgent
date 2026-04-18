"""
Business Agent 2.0 - Main Runner Script
========================================
This script provides an easy way to run different components of the system.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def check_services():
    """Check if required services are running"""
    print_header("🔍 Checking System Services")
    
    # Check Docker/Qdrant
    try:
        import docker
        client = docker.from_env()
        containers = client.containers.list()
        qdrant_running = any('qdrant' in c.name.lower() for c in containers)
        if qdrant_running:
            print("✅ Qdrant container is running")
        else:
            print("❌ Qdrant container is NOT running")
            print("   Run: docker-compose up -d")
    except:
        print("⚠️  Could not check Docker status")
    
    # Check Ollama
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            print("✅ Ollama is running")
            models = response.json().get('models', [])
            print(f"   Available models: {', '.join([m['name'] for m in models[:3]])}")
        else:
            print("❌ Ollama is NOT responding")
    except:
        print("❌ Ollama is NOT running")
        print("   Start Ollama service")

def run_agent():
    """Run the main opportunity scout agent"""
    print_header("🚀 Running Opportunity Scout Agent")
    subprocess.run([sys.executable, "core_engine/agent.py"])

def run_mcp_agent():
    """Run the MCP-enabled agent"""
    print_header("🚀 Running MCP-Enabled Agent")
    subprocess.run([sys.executable, "core_engine/agent_mcp_example.py"])

def create_test_data():
    """Create test data in Qdrant"""
    print_header("📥 Creating Test Data")
    subprocess.run([sys.executable, "create_test_data.py"])

def ingest_data():
    """Run data ingestion from various sources"""
    print_header("📥 Running Data Ingestion")
    print("\nWhat would you like to ingest?")
    print("1. RSS Feeds")
    print("2. Reddit Posts")
    print("3. Custom URL")
    print("4. All sources")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        subprocess.run([sys.executable, "perception/ingest.py", "--source", "rss"])
    elif choice == "2":
        subprocess.run([sys.executable, "perception/ingest.py", "--source", "reddit"])
    elif choice == "3":
        url = input("Enter URL to scrape: ").strip()
        subprocess.run([sys.executable, "perception/ingest.py", "--source", "web", "--url", url])
    elif choice == "4":
        subprocess.run([sys.executable, "perception/ingest.py", "--source", "all"])

def test_mcp_servers():
    """Test MCP servers"""
    print_header("🧪 Testing MCP Servers")
    subprocess.run([sys.executable, "test_mcp_setup.py"])

def demo_mcp():
    """Run MCP demo"""
    print_header("🎭 MCP Demo")
    subprocess.run([sys.executable, "demo_mcp.py"])

def generate_visualizations():
    """Generate project visualizations"""
    print_header("📊 Generating Visualizations")
    print("\nWhat would you like to generate?")
    print("1. Static graphs (matplotlib)")
    print("2. Interactive dashboard (plotly)")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ["1", "3"]:
        subprocess.run([sys.executable, "generate_graphs.py"])
    if choice in ["2", "3"]:
        subprocess.run([sys.executable, "generate_interactive_dashboard.py"])

def main_menu():
    """Display main menu"""
    while True:
        print_header("🤖 Business Agent 2.0 - Main Menu")
        print("1. Check System Status")
        print("2. Create Test Data")
        print("3. Run Main Agent")
        print("4. Run MCP-Enabled Agent")
        print("5. Ingest New Data")
        print("6. Test MCP Setup")
        print("7. MCP Demo")
        print("8. Generate Visualizations")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == "1":
            check_services()
        elif choice == "2":
            create_test_data()
        elif choice == "3":
            run_agent()
        elif choice == "4":
            run_mcp_agent()
        elif choice == "5":
            ingest_data()
        elif choice == "6":
            test_mcp_servers()
        elif choice == "7":
            demo_mcp()
        elif choice == "8":
            generate_visualizations()
        elif choice == "9":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
        sys.exit(0)
