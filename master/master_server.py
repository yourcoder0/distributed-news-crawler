# master/master_server.py

import grpc
import crawler_pb2
import crawler_pb2_grpc
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO, format='[MASTER] %(asctime)s - %(levelname)s - %(message)s')

# List of URLs to crawl
URLS_TO_CRAWL = [
    "https://techcrunch.com",
    "https://news.ycombinator.com",
    "https://thenextweb.com",
    "https://www.bbc.com/news/technology"
]

# Define the worker address (assuming it's on the same machine)
WORKER_ADDRESS = 'localhost:50051'

def fetch_from_worker(url):
    try:
        with grpc.insecure_channel(WORKER_ADDRESS) as channel:
            stub = crawler_pb2_grpc.CrawlerStub(channel)
            request = crawler_pb2.URLRequest(url=url)
            response = stub.FetchPage(request)
            logging.info(f"Received {len(response.titles)} titles from {url}")
            return url, list(zip(response.titles, response.links))
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return url, []

def main():
    results = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(fetch_from_worker, url): url for url in URLS_TO_CRAWL}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                site_url, data = future.result()
                results[site_url] = data
            except Exception as exc:
                logging.error(f"{url} generated an exception: {exc}")

    # Print Results (Structured)
    for site, items in results.items():
        print(f"\n🔗 Results from {site}:")
        for title, link in items[:10]:  # Show only top 10 for brevity
            print(f" - {title} → {link}")

if __name__ == '__main__':
    main()
