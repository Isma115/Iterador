import concurrent.futures
from ddgs import DDGS
from sources import TRUSTED_SOURCES

def test_source(source):
    domain = source['domain']
    name = source['name']
    query = f"test site:{domain}"
    try:
        # We just need to see if it returns *something* or at least doesn't crash
        # Since "test" might not appear on every site, we use a very common term or the site name itself
        query = f"science OR data OR news site:{domain}"
        results = list(DDGS().text(query, max_results=1))
        return {
            "name": name,
            "domain": domain,
            "status": "OK" if results else "NO RESULTS",
            "count": len(results)
        }
    except Exception as e:
        return {
            "name": name,
            "domain": domain,
            "status": f"ERROR: {str(e)}",
            "count": 0
        }

print(f"Verifying {len(TRUSTED_SOURCES)} sources...")

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_source = {executor.submit(test_source, s): s for s in TRUSTED_SOURCES}
    for future in concurrent.futures.as_completed(future_to_source):
        res = future.result()
        results.append(res)
        print(f"[{res['status']}] {res['name']} ({res['domain']})")

print("\nSummary:")
ok_count = sum(1 for r in results if r['status'] == "OK")
print(f"Working: {ok_count}/{len(TRUSTED_SOURCES)}")

print("\nFailed/No Results:")
for r in results:
    if r['status'] != "OK":
        print(f" - {r['name']}: {r['status']}")
