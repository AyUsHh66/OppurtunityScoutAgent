print("--- Starting Newspaper3k Direct Test ---")
try:
    from newspaper import Article
    print("SUCCESS: Imported 'Article' from 'newspaper' library.")

    # A valid article URL to test with
    url = 'https://techcrunch.com/2024/09/05/with-a-new-10m-fund-footprint-coalition-looks-to-back-more-startups-tackling-the-climate-crisis/'

    print(f"\nAttempting to process URL: {url}")
    article = Article(url)

    print("Downloading article content...")
    article.download()
    print("-> Download complete.")

    print("Parsing article content...")
    article.parse()
    print("-> Parse complete.")

    print("\n--- Article Title ---")
    print(article.title)
    print("---------------------\n")

    print("✅✅✅ ULTIMATE SUCCESS: newspaper3k is installed and works perfectly.")

except ImportError as e:
    print(f"\n❌❌❌ ULTIMATE FAILURE: Could not import newspaper. Error: {e}")
    print("This indicates a catastrophic problem with the Python environment itself.")

except Exception as e:
    print(f"\n❌❌❌ ULTIMATE FAILURE: newspaper imported but failed during execution. Error: {e}")
    print("This likely points to a network issue or a problem with a core dependency.")

print("\n--- Test Complete ---")