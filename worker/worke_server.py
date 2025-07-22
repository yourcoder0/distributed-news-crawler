# worker/worker_server.py

import grpc
from concurrent import futures
import time
import requests
from bs4 import BeautifulSoup
import logging

import crawler_pb2
import crawler_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO, format='[WORKER] %(asctime)s - %(levelname)s - %(message)s')

class CrawlerServicer(crawler_pb2_grpc.CrawlerServicer):
    def FetchPage(self, request, context):
        url = request.url
        logging.info(f"Received request to fetch: {url}")
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract article titles and links (simple example for all <a> tags)
            titles = []
            links = []
            for tag in soup.find_all('a', href=True):
                text = tag.get_text(strip=True)
                href = tag['href']
                if text:
                    titles.append(text)
                    links.append(href)

            logging.info(f"Extracted {len(titles)} titles from {url}")
            return crawler_pb2.PageResponse(titles=titles, links=links)
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return crawler_pb2.PageResponse(titles=[], links=[])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    crawler_pb2_grpc.add_CrawlerServicer_to_server(CrawlerServicer(), server)
    server.add_insecure_port('[::]:50051')
    logging.info("Worker server starting on port 50051...")
    server.start()
    try:
        while True:
            time.sleep(86400)  # 1 day
    except KeyboardInterrupt:
        logging.info("Shutting down worker server...")
        server.stop(0)

if __name__ == '__main__':
    serve()
