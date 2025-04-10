# src/data_acquisition.py

import requests
import feedparser
import json
import os

def query_arxiv(search_query, start=0, max_results=5):
    """
    Query the arXiv API with a search query, starting at 'start' and returning up to max_results.
    """
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
    """
    Process feed entries by extracting title, summary (as text), PDF link, and authors.
    """
    documents = []
    for entry in entries:
        # Concatenate title and summary as the document text.
        text = entry.title + ". " + entry.summary
        # Construct PDF link by replacing 'abs' with 'pdf' and appending '.pdf'
        pdf_link = entry.id.replace("abs", "pdf") + ".pdf"
        documents.append({
            'title': entry.title,
            'text': text,
            'pdf_link': pdf_link,
            'authors': [author.name for author in entry.authors]
        })
    return documents

def query_arxiv_paginated(search_query, total_results=50, batch_size=5):
    """
    Query the arXiv API in batches (pagination) until we collect total_results.
    """
    all_entries = []
    for start in range(0, total_results, batch_size):
        # Fetch a batch of results
        entries = query_arxiv(search_query, start=start, max_results=batch_size)
        all_entries.extend(entries)
    return all_entries

def download_and_save_topic(topic, total_results=50, batch_size=5):
    """
    Download papers for a given topic and save them to a JSON file.
    """
    print(f"\nDownloading papers for topic: '{topic}'")
    entries = query_arxiv_paginated(topic, total_results=total_results, batch_size=batch_size)
    docs = process_entries(entries)
    # Create a filename that reflects the topic, e.g., data/raw/arxiv_deep_learning_documents.json
    filename = os.path.join("data", "raw", f"arxiv_{topic.replace(' ', '_')}_documents.json")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(docs, f, indent=2)
    print(f"Saved {len(docs)} documents to {filename}")
    return docs

if __name__ == "__main__":
    # Define the topics you want to cover.
    topics = ["deep learning", "machine learning", "neural networks"]
    
    all_docs = []
    for topic in topics:
        docs = download_and_save_topic(topic, total_results=50, batch_size=5)
        all_docs.extend(docs)
    
    # Save the combined dataset for use in your retrieval pipeline.
    combined_filename = os.path.join("data", "raw", "arxiv_combined_documents.json")
    with open(combined_filename, 'w', encoding='utf-8') as f:
        json.dump(all_docs, f, indent=2)
    print(f"\nSaved combined dataset with {len(all_docs)} documents to {combined_filename}")
