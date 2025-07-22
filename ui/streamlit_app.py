# ui/streamlit_app.py

import streamlit as st
import grpc
import sys
import os

# ✅ Ensure Python can find proto files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import crawler_pb2
import crawler_pb2_grpc

# gRPC server address
WORKER_ADDRESS = "localhost:50051"

def crawl_url(url):
    try:
        with grpc.insecure_channel(WORKER_ADDRESS) as channel:
            stub = crawler_pb2_grpc.CrawlerStub(channel)
            request = crawler_pb2.URLRequest(url=url)
            response = stub.FetchPage(request)
            return list(zip(response.titles, response.links))
    except Exception as e:
        return f"Error: {e}"

# 🌐 Streamlit App
st.set_page_config(page_title="Distributed News Crawler", layout="centered")

st.title("🕸️ Distributed News Crawler")
st.caption("Built with Python + gRPC + Streamlit")

url = st.text_input("Enter a news website URL to crawl:", "https://techcrunch.com")

if st.button("Crawl"):
    with st.spinner("Fetching articles..."):
        result = crawl_url(url)

    if isinstance(result, str):
        st.error(result)
    elif result:
        st.success(f"Top {min(10, len(result))} articles from {url}:")
        for title, link in result[:10]:
            st.markdown(f"- [{title}]({link})")
    else:
        st.warning("No articles found or failed to fetch.")
