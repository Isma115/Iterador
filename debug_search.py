from duckduckgo_search import DDGS

print("Testing simple search...")
try:
    results = list(DDGS().text("NASA Mars mission site:nasa.gov", max_results=3))
    print(f"Results for 'NASA Mars mission site:nasa.gov': {len(results)}")
    for r in results:
        print(r.get('title'))
        print(r.get('href'))
except Exception as e:
    print(f"Error: {e}")

print("\nTesting without site filter...")
try:
    results = list(DDGS().text("NASA Mars mission", max_results=3))
    print(f"Results for 'NASA Mars mission': {len(results)}")
except Exception as e:
    print(f"Error: {e}")
