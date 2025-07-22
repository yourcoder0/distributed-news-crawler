# client/run_crawl.py

import sys
import os

# ✅ Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import grpc
import crawler_pb2
import crawler_pb2_grpc

def run_crawl(url):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = crawler_pb2_grpc.CrawlerStub(channel)
        request = crawler_pb2.URLRequest(url=url)
        response = stub.FetchPage(request)
        print(f"\n🔍 Results from {url}:")
        for title, link in zip(response.titles[:10], response.links[:10]):
            print(f" - {title} → {link}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python run_crawl.py <url>")
        sys.exit(1)

    target_url = sys.argv[1]
    run_crawl(target_url)
