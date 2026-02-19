from ddgs import DDGS

print("Testing search with 'from ddgs import DDGS'...")

try:
    with DDGS() as ddgs:
        print("Searching for 'NASA Mars logic'...")
        results = list(ddgs.text("NASA Mars logic", max_results=3))
        print(f"Results: {len(results)}")
        for r in results:
            print(f" - {r.get('title')} ({r.get('href')})")
            
        print("\nSearching for 'site:nasa.gov Mars'...")
        results_site = list(ddgs.text("site:nasa.gov Mars", max_results=3))
        print(f"Results with site filter: {len(results_site)}")
        for r in results_site:
            print(f" - {r.get('title')} ({r.get('href')})")

except Exception as e:
    print(f"Error: {e}")
