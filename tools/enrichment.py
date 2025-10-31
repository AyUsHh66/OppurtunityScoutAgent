# In tools/enrichment.py
import os
import requests
from langchain_core.tools import tool

@tool
def find_company_info(company_name: str) -> dict:
    """
    Finds company information and contact details for a given company name.
    Uses the Hunter.io Company Enrichment API.
    """
    api_key = os.getenv("HUNTER_API_KEY")
    if not api_key:
        return {"error": "Hunter API key is not set."}

    # Hunter's API is often more effective with a domain name.
    # This is a simple heuristic; a real system might use a search engine to find the domain.
    domain = f"{company_name.lower().replace(' ', '')}.com"
    
    url = f"https://api.hunter.io/v2/company-enrichment?domain={domain}&api_key={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json().get("data", {})
    except requests.exceptions.RequestException as e:
        return {"error": f"Could not retrieve company information: {e}"}