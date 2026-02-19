try:
    from duckduckgo_search import DDGS
    print("Imported DDGS successfully from duckduckgo_search")
except ImportError:
    print("Could not import DDGS from duckduckgo_search")

print("Testing simple search 'NASA'...")
try:
    with DDGS() as ddgs:
        results = list(ddgs.text("NASA", max_results=3))
        print(f"Results: {len(results)}")
        for r in results:
            print(r.get('title'))
except Exception as e:
    print(f"Error: {e}")
