"""
Quick script to show where to find your Trello cards and Discord notifications
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("  📍 WHERE TO SEE YOUR PROOF")
print("="*80 + "\n")

# Trello
trello_list_id = os.getenv("TRELLO_LIST_ID")
trello_api_key = os.getenv("TRELLO_API_KEY")

print("🗂️  TRELLO:")
print(f"   List ID: {trello_list_id}")
print(f"   Direct link: https://trello.com/")
print(f"   ")
print(f"   👉 Go to Trello.com and look for a new card in your list!")
print(f"   Card should be titled: 'Follow up: digitalagency - Score: 8/10'")

# Discord
discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
discord_webhook = os.getenv("Discord_WEBHOOK_URL", "")

print("\n💬 DISCORD:")
print(f"   Channel ID: {discord_channel_id}")
if discord_webhook:
    print(f"   Webhook configured: Yes")
print(f"   ")
print(f"   👉 Check your Discord server for a notification message!")
print(f"   Message contains: Lead qualified with score 8/10")

# Get actual links using API
print("\n" + "="*80)
print("  🔍 FETCHING ACTUAL LINKS...")
print("="*80 + "\n")

try:
    import requests
    
    # Get Trello card
    url = f"https://api.trello.com/1/lists/{trello_list_id}/cards"
    params = {
        'key': trello_api_key,
        'token': os.getenv("TRELLO_TOKEN"),
        'limit': 5
    }
    response = requests.get(url, params=params, timeout=5)
    if response.status_code == 200:
        cards = response.json()
        print("✅ RECENT TRELLO CARDS:")
        for i, card in enumerate(cards[:5], 1):
            print(f"   {i}. {card['name']}")
            print(f"      Link: {card['shortUrl']}")
        if cards:
            print(f"\n   👉 Latest card: {cards[0]['shortUrl']}")
    else:
        print(f"⚠️  Couldn't fetch Trello cards (API response: {response.status_code})")
except Exception as e:
    print(f"⚠️  Error fetching Trello data: {e}")

print("\n" + "="*80)
print("  💡 TIP: The agent just created these a moment ago!")
print("="*80 + "\n")
