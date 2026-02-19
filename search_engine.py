# search_engine.py
import requests
import trafilatura
# from ddgs import DDGS # Import inside method to be safe or keep global if patched
from sources import TRUSTED_SOURCES
import concurrent.futures
import ssl
import sys

# --- AGGRESSIVE SSL PATCHING ---
# This is required for environments with intercepting proxies or broken local cert chains (common on macOS Python)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
    if hasattr(ssl, 'create_default_context'):
        ssl.create_default_context = _create_unverified_https_context

# Also try to patch requests/urllib3 if possible in main logic or via arguments

class TrustedSearcher:
    def __init__(self):
        # We will initialize search engines lazily or handle imports here
        pass

    def search_generator(self, query, max_results=30):
        print(f"[DEBUG] Starting search generator for '{query}' with max_results={max_results}")
        
        # Collect seen links across both phases to avoid duplicates
        seen_links = set()
        
        # Phase 1: General Google search (no domain restriction, 12 results, orange)
        try:
            print("[DEBUG] Starting general Google search (no site filter)...")
            for batch in self._search_google_general_generator(query, max_results=12, seen_links=seen_links):
                yield batch
        except Exception as e:
            print(f"[DEBUG] Google general search failed: {e}")
            
        # Phase 2: Trusted-source search (DDGS, fallback to Google with site: filter)
        try:
            print("[DEBUG] Attempting search with DuckDuckGo (ddgs)...")
            for batch in self._search_ddgs_generator(query, max_results):
                filtered_batch = []
                for r in batch:
                    if r['link'] not in seen_links:
                        seen_links.add(r['link'])
                        filtered_batch.append(r)
                if filtered_batch:
                    yield filtered_batch
        except Exception as e:
            print(f"[DEBUG] DDGS failed completely: {e}")
            print("[DEBUG] Falling back to Google Search (googlesearch-python)...")
            for batch in self._search_google_generator(query, max_results):
                filtered_batch = []
                for r in batch:
                    if r['link'] not in seen_links:
                        seen_links.add(r['link'])
                        filtered_batch.append(r)
                if filtered_batch:
                    yield filtered_batch

    def search(self, query, max_results=30):
        # Backward compatibility wrapper
        all_results = []
        for batch in self.search_generator(query, max_results):
            all_results.extend(batch)
        return all_results

    def _search_ddgs_generator(self, query, max_results):
        from ddgs import DDGS
        domains = [s['domain'] for s in TRUSTED_SOURCES]
        chunk_size = 4
        chunks = [domains[i:i + chunk_size] for i in range(0, len(domains), chunk_size)]
        
        print(f"[DEBUG] Processing {len(chunks)} chunks of domains via DDGS.")
        
        seen_links = set()
        total_found = 0
        
        for i, chunk in enumerate(chunks):
            if total_found >= max_results:
                break
                
            site_filter = " OR ".join([f"site:{d}" for d in chunk])
            full_query = f"{query} ({site_filter})"
            
            chunk_results = []
            try:
                # We interpret max_results per chunk as 5 to get a steady stream
                with DDGS() as ddgs:
                    res_gen = ddgs.text(full_query, max_results=5)
                    if res_gen:
                        chunk_raw = list(res_gen)
                        print(f"[DEBUG] Chunk {i+1} returned {len(chunk_raw)} raw results.")
                        for res in chunk_raw:
                            link = res.get('href', '')
                            if link not in seen_links:
                                source_name = self._get_source_name(link)
                                if source_name != "Unknown Trusted Source":
                                    seen_links.add(link)
                                    chunk_results.append({
                                        'title': res.get('title'),
                                        'link': link,
                                        'snippet': res.get('body'),
                                        'source': source_name
                                    })
            except Exception as e:
                print(f"[DEBUG] Chunk {i+1} error: {e}")
                if "SSL" in str(e) or "Certificate" in str(e):
                    raise e 
            
            if chunk_results:
                total_found += len(chunk_results)
                yield chunk_results

    def _search_google_generator(self, query, max_results):
        from googlesearch import search
        domains = [s['domain'] for s in TRUSTED_SOURCES]
        chunk_size = 3
        chunks = [domains[i:i + chunk_size] for i in range(0, len(domains), chunk_size)]
        
        seen_links = set()
        total_found = 0
        
        for i, chunk in enumerate(chunks):
            if total_found >= max_results:
                break
                
            site_filter = " OR ".join([f"site:{d}" for d in chunk])
            full_query = f"{query} ({site_filter})"
            
            chunk_results = []
            try:
                raw_results = list(search(full_query, num_results=5, advanced=True, sleep_interval=1))
                for res in raw_results:
                    if res.url not in seen_links:
                        source_name = self._get_source_name(res.url)
                        if source_name != "Unknown Trusted Source":
                            seen_links.add(res.url)
                            chunk_results.append({
                                'title': res.title,
                                'link': res.url,
                                'snippet': res.description,
                                'source': source_name
                            })
            except Exception as e:
                print(f"[DEBUG] Google chunk error: {e}")
            
            if chunk_results:
                total_found += len(chunk_results)
                yield chunk_results

    def _search_google_general_generator(self, query, max_results=12, seen_links=None):
        """General search WITHOUT site: filter using DDGS. Results are flagged for orange display."""
        from ddgs import DDGS
        if seen_links is None:
            seen_links = set()
        
        print(f"[DEBUG] General search: searching '{query}' for up to {max_results} results...")
        
        chunk_results = []
        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=max_results))
            print(f"[DEBUG] General search returned {len(raw_results)} raw results.")
            for res in raw_results:
                link = res.get('href', '')
                if link and link not in seen_links:
                    seen_links.add(link)
                    # Check if it happens to match a trusted source
                    source_name = self._get_source_name(link)
                    if source_name == "Unknown Trusted Source":
                        source_name = "Google"
                    chunk_results.append({
                        'title': res.get('title', ''),
                        'link': link,
                        'snippet': res.get('body', ''),
                        'source': source_name,
                        'is_google_general': True
                    })
        except Exception as e:
            print(f"[DEBUG] General search error: {e}")
        
        if chunk_results:
            yield chunk_results

    def search_youtube_generator(self, query, max_results=5):
        """
        Searches for YouTube videos using DDGS and yields results with transcripts.
        """
        from ddgs import DDGS
        from youtube_transcript import get_transcript
        
        print(f"[DEBUG] Starting YouTube search for '{query}'...")
        
        try:
            with DDGS() as ddgs:
                # Use videos() method to find videos
                # Note: ddgs.videos returns a generator
                video_gen = ddgs.videos(query, max_results=max_results)
                
                for video_res in video_gen:
                    video_url = video_res.get('content') # Based on debug, 'content' holds the URL
                    if not video_url:
                        video_url = video_res.get('embed_url') # Fallback
                        
                    if video_url:
                        title = video_res.get('title', 'Video sin título')
                        print(f"[DEBUG] Found video: {title} ({video_url})")
                        
                        try:
                            # Extract transcript immediately
                            print(f"[DEBUG] Attempting to extract transcript for {video_url}...")
                            transcript_data = get_transcript(video_url)
                            print(f"[DEBUG] Transcript extraction successful for {video_url}!")
                            
                            # Override title with video title from search if transcript title is refreshing
                            if transcript_data:
                                # Start yielding separate results immediately 
                                # (yield as a list of 1 to behave like other generators)
                                print(f"[DEBUG] Yielding transcript result for {video_url}...")
                                yield [transcript_data]
                                print(f"[DEBUG] Yield complete for {video_url}.")
                        except Exception as e:
                            print(f"[DEBUG] Failed to get transcript for {video_url}: {e}")
                            pass
                            
        except Exception as e:
            print(f"[DEBUG] YouTube search error: {e}")

    # REMOVING OLD SEARCH METHODS TO AVOID CONFLICT
    def _search_ddgs_OLD(self, query, max_results):
        pass # Placeholder to ensure clean replacement if logic matched poorly


    def _search_google(self, query, max_results):
        from googlesearch import search
        all_results = []
        
        # Google search supports "OR", but query length limits are strict.
        # We might need to use a simpler strategy or iterate chunks carefully.
        # Let's try to search broadly with "site:domain" iterative approach but only for top sources if needed?
        # Or better: search the query and FILTER results by domain?
        # No, Google restricts result count.
        
        # We will try the chunk approach but Google bans fast.
        # Safer approach: "query (site:a.com OR site:b.com ...)"
        
        domains = [s['domain'] for s in TRUSTED_SOURCES]
        chunk_size = 3 # Smaller chunks for Google
        chunks = [domains[i:i + chunk_size] for i in range(0, len(domains), chunk_size)]
        
        print(f"[DEBUG] Processing {len(chunks)} chunks of domains via Google.")

        for i, chunk in enumerate(chunks):
            site_filter = " OR ".join([f"site:{d}" for d in chunk])
            full_query = f"{query} ({site_filter})"
            print(f"[DEBUG] Querying Google chunk {i+1}...")
            
            try:
                # advanced=True returns objects with title/desc
                # num_results applies per search
                results = list(search(full_query, num_results=5, advanced=True, sleep_interval=1)) 
                print(f"[DEBUG] Chunk {i+1} returned {len(results)}.")
                
                for res in results:
                    # Filter again just in case
                    source_name = self._get_source_name(res.url)
                    if source_name != "Unknown Trusted Source":
                        all_results.append({
                            'title': res.title,
                            'link': res.url,
                            'snippet': res.description,
                            'source': source_name
                        })
            except Exception as e:
                print(f"[DEBUG] Google chunk error: {e}")
                # Google often throws 429 Too Many Requests
                if "429" in str(e):
                    print("[DEBUG] Google blocking requests. Stopping.")
                    break
            
            if len(all_results) >= max_results * 1.5:
                break
                
        return self._deduplicate(all_results, max_results)

    def _deduplicate(self, results, max_results):
        seen_links = set()
        unique_results = []
        for r in results:
            if r['link'] not in seen_links:
                unique_results.append(r)
                seen_links.add(r['link'])
        print(f"[DEBUG] Final unique results: {len(unique_results)}")
        return unique_results[:max_results]

    def _get_source_name(self, link):
        for s in TRUSTED_SOURCES:
            if s['domain'] in link:
                return s['name']
        return "Unknown Trusted Source"

    def fetch_full_content(self, results):
        """
        Fetches text content.
        """
        print(f"[DEBUG] Fetching content for {len(results)} URLs...")
        detailed_results = []
        
        # Ensure SSL patch logic is active in threads
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_to_url = {executor.submit(self._scrape_url, r): r for r in results}
            for future in concurrent.futures.as_completed(future_to_url):
                orig_result = future_to_url[future]
                try:
                    content = future.result()
                    if content:
                        print(f"[DEBUG] Scraped: {orig_result['link']}")
                        orig_result['content'] = content
                        detailed_results.append(orig_result)
                    else:
                        print(f"[DEBUG] Empty/Fail: {orig_result['link']}")
                except Exception as e:
                    print(f"[DEBUG] Error scraping {orig_result['link']}: {e}")
        
        return detailed_results

    def _scrape_url(self, result_dict):
        url = result_dict['link']
        try:
            # Using requests directly to enforce verify=False
            response = requests.get(url, timeout=10, verify=False, headers={'User-Agent': 'Mozilla/5.0'})
            
            content_type = response.headers.get('Content-Type', '').lower()
            
            # --- PDF HANDLING ---
            if 'application/pdf' in content_type:
                print(f"[DEBUG] Detected PDF: {url}")
                try:
                    import io
                    from pypdf import PdfReader
                    
                    f = io.BytesIO(response.content)
                    reader = PdfReader(f)
                    text = ""
                    # Extract text from up to 10 pages to avoid hanging on massive docs
                    max_pages = min(len(reader.pages), 10)
                    for i in range(max_pages):
                        text += reader.pages[i].extract_text() + "\n"
                    
                    if len(text) < 100:
                        return None
                        
                    return text
                except Exception as e:
                    print(f"[DEBUG] PDF Extraction failed for {url}: {e}")
                    return None

            # --- REGULAR HTML HANDLING ---
            # If it's not text/html, be careful
            if 'text' not in content_type and 'html' not in content_type and 'json' not in content_type:
                 print(f"[DEBUG] Skipping unknown content-type '{content_type}': {url}")
                 return None

            if response.status_code != 200:
                return None
            
            if len(response.text) < 500: # Skip very small pages
                return None

            result_text = trafilatura.extract(
                response.text, 
                include_comments=False, 
                include_tables=False, 
                no_fallback=True
            )
            
            if not result_text or len(result_text) < 200:
                return None
                
            return result_text
            
        except Exception:
            return None

if __name__ == "__main__":
    # Test
    ts = TrustedSearcher()
    res = ts.search("Mars landing")
    print(f"Found {len(res)} results.")
    full = ts.fetch_full_content(res[:2])
    for i in full:
        print(f"--- {i['source']} ---\n{i['content'][:100]}...\n")
