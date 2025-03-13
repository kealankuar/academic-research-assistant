# src/data_acquisition.py
import requests
import feedparser
import json
import os

def query_arxiv(search_query, start=0, max_results=5):
    base_url = "http://export.arxiv.org/api/query?"
    query = f"search_query=all:{search_query}&start={start}&max_results={max_results}"
    url = base_url + query
    print("Querying:", url)

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error querying arXiv API: {response.status_code}")

    feed = feedparser.parse(response.text)
    return feed.entries

def process_entries(entries):
    documents = []
    for entry in entries:
        text = entry.title + ". " + entry.summary
        pdf_link = entry.id.replace("abs", "pdf") + ".pdf"
        documents.append({
            'title': entry.title,
            'text': text,
            'pdf_link': pdf_link,
            'authors': [author.name for author in entry.authors]
        })
    return documents

def save_documents(documents, filename="../data/raw/arxiv_documents.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2)
    print(f"Saved {len(documents)} documents to {filename}")

if __name__ == "__main__":
    # Example usage: query papers on "deep learning"
    entries = query_arxiv("deep learning", max_results=50)
    docs = process_entries(entries)
    save_documents(docs)