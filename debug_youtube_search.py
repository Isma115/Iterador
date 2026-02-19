from ddgs import DDGS
import json

def test_keys(query):
    print(f"Testing DDGS keys for '{query}'...")
    try:
        with DDGS() as ddgs:
            gen = ddgs.videos(query, max_results=1)
            results = list(gen)
            if results:
                r = results[0]
                print(f"Keys found: {list(r.keys())}")
                print(json.dumps(r, indent=2))
            else:
                print("No results found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_keys("Python tutorial")
