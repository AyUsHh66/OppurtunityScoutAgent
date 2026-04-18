"""
Show all leads/cards in Trello with detailed information
"""
import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def extract_lead_details(card_name, description):
    """Extract lead details from card name and description"""
    details = {
        'title': card_name,
        'company': 'Unknown',
        'score': 'N/A',
        'confidence': 'N/A',
        'justification': '',
        'reasoning': '',
        'key_factors': [],
        'full_description': description
    }
    
    # Try to extract company from title
    company_patterns = [
        r'New Lead:\s*(.+?)(?:\s*-|$)',
        r'(?:\d+/\d+\s*-\s*)?(.+?)(?:\s*-|$)',
        r'🌟\s*EXCELLENT\s*\[\d+/\d+\]\s*(.+?)(?:\s*-|$)',
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, card_name)
        if match:
            company = match.group(1).strip()
            if company and company.lower() not in ['unknown', 'unknown lead', '']:
                details['company'] = company
                break
    
    # Extract details from description
    if description:
        # Try to parse JSON in description
        json_match = re.search(r'\{[^}]*"score"[^}]*\}', description, re.DOTALL)
        if json_match:
            try:
                # Try to extract complete JSON object
                json_text = json_match.group(0)
                # Expand search to capture full JSON
                start = description.find('{')
                if start != -1:
                    brace_count = 0
                    end = start
                    for i in range(start, len(description)):
                        if description[i] == '{':
                            brace_count += 1
                        elif description[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end = i + 1
                                break
                    json_text = description[start:end]
                
                data = json.loads(json_text)
                details['score'] = data.get('score', 'N/A')
                if 'company_name' in data and data['company_name']:
                    details['company'] = data['company_name']
                if 'justification' in data:
                    details['justification'] = data['justification']
                if 'reasoning_trace' in data:
                    details['reasoning'] = data['reasoning_trace']
            except:
                pass
        
        # Extract justification with quotes pattern
        just_match = re.search(r'"justification":\s*"([^"]+)"', description, re.DOTALL)
        if just_match and not details['justification']:
            details['justification'] = just_match.group(1)
        
        # Extract reasoning trace
        reasoning_match = re.search(r'\*\*🧠 Reasoning:\*\*\s*(.+?)(?:\n\n|\*\*)', description, re.DOTALL)
        if reasoning_match and not details['reasoning']:
            details['reasoning'] = reasoning_match.group(1).strip()
        
        # Look for score patterns
        score_patterns = [
            r'Score:\s*(\d+)/10',
            r'"score":\s*(\d+)',
            r'Quality Score:\s*(\d+)',
            r'\[(\d+)/10\]',
        ]
        for pattern in score_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                details['score'] = f"{match.group(1)}/10"
                break
        
        # Look for confidence
        conf_match = re.search(r'Confidence[:\s]*(\w+)', description, re.IGNORECASE)
        if conf_match:
            details['confidence'] = conf_match.group(1)
        
        # Extract company from description
        company_patterns_desc = [
            r'\*\*Company:\*\*\s*(.+?)(?:\n|$)',
            r'company_name":\s*"(.+?)"',
        ]
        for pattern in company_patterns_desc:
            match = re.search(pattern, description)
            if match:
                company = match.group(1).strip()
                if company and company.lower() not in ['unknown', 'unknown lead', '']:
                    details['company'] = company
                    break
        
        # Extract key positive factors
        factors_match = re.search(r'\*\*✅ Key Positive Factors:\*\*\s*(.+?)(?:\n\n|\*\*)', description, re.DOTALL)
        if factors_match:
            factors_text = factors_match.group(1).strip()
            details['key_factors'] = [f.strip('- ').strip() for f in factors_text.split('\n') if f.strip()]
    
    return details

print("\n" + "="*80)
print("  🗂️  YOUR BUSINESS LEADS - DETAILED VIEW")
print("="*80 + "\n")

try:
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    list_id = os.getenv("TRELLO_LIST_ID")
    
    # Get all cards
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    params = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code == 200:
        cards = response.json()
        
        print(f"📊 Total Leads Found: {len(cards)}\n")
        print("="*80 + "\n")
        
        for i, card in enumerate(cards, 1):
            card_name = card.get('name', 'Untitled')
            card_url = card.get('shortUrl', 'No URL')
            description = card.get('desc', '')
            
            # Extract detailed information
            details = extract_lead_details(card_name, description)
            
            # Display lead information
            print(f"{'='*80}")
            print(f"LEAD #{i}")
            print(f"{'='*80}")
            print(f"📋 Title: {details['title']}")
            print(f"🏢 Company: {details['company']}")
            print(f"⭐ Score: {details['score']}")
            if details['confidence'] != 'N/A':
                print(f"🎯 Confidence: {details['confidence']}")
            print(f"🔗 Trello Link: {card_url}")
            print()
            
            # Show justification if available
            if details['justification']:
                print(f"📝 JUSTIFICATION:")
                print(f"{details['justification']}")
                print()
            
            # Show reasoning if available
            if details['reasoning']:
                print(f"🧠 REASONING:")
                print(f"{details['reasoning']}")
                print()
            
            # Show key factors if available
            if details['key_factors']:
                print(f"✅ KEY POSITIVE FACTORS:")
                for factor in details['key_factors']:
                    print(f"  • {factor}")
                print()
            
            # If no structured data, show raw description excerpt
            if not details['justification'] and not details['reasoning'] and description:
                print(f"📄 FULL DETAILS:")
                # Show description in a formatted way
                desc_lines = description.split('\n')
                for line in desc_lines[:30]:  # Show first 30 lines
                    print(f"  {line}")
                if len(desc_lines) > 30:
                    print(f"  ... ({len(desc_lines) - 30} more lines)")
                print()
            
            print()
        
        print("="*80)
        print(f"\n✅ You have {len(cards)} qualified leads ready for outreach!")
        print("💡 Click any link to view full details in Trello")
        
    else:
        print(f"⚠️  Could not fetch cards (Status: {response.status_code})")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80 + "\n")
