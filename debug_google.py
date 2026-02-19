from googlesearch import search

print("Testing Google Search...")
try:
    results = list(search("NASA Mars mission site:nasa.gov", num_results=3, advanced=True))
    print(f"Results: {len(results)}")
    for r in results:
        print(f"Title: {r.title}")
        print(f"URL: {r.url}")
        print(f"Description: {r.description}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
