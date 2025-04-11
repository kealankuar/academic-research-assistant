# src/data_acquisition.py

import requests
import feedparser
import os
from data_access import add_document
from db import get_session

def query_arxiv(search_query, start=0, max_results=5):
    """
    Query the arXiv API with a search query starting at a given index,
    returning up to max_results entries.
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
    Process arXiv API feed entries into a list of document dictionaries.
    Each document contains a title, combined text (title + summary),
    PDF link, and list of authors.
    """
    documents = []
    for entry in entries:
        # Concatenate title and summary for full context.
        text = entry.title + ". " + entry.summary
        # Construct the PDF link by replacing 'abs' with 'pdf' and appending '.pdf'
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
    Retrieve entries from the arXiv API using pagination until we reach total_results.
    """
    all_entries = []
    for start in range(0, total_results, batch_size):
        entries = query_arxiv(search_query, start=start, max_results=batch_size)
        all_entries.extend(entries)
    return all_entries

def download_and_save_topic_to_db(topic, total_results=50, batch_size=5):
    """
    Fetch documents for the given topic via the arXiv API and insert them
    into the PostgreSQL database. Uses the add_document function for insertion.
    
    Returns the list of processed document dictionaries.
    """
    # Open a new session.
    session = get_session()
    
    print(f"\nFetching documents for topic: '{topic}' ...")
    # Retrieve entries using pagination.
    entries = query_arxiv_paginated(topic, total_results=total_results, batch_size=batch_size)
    docs = process_entries(entries)
    
    # For each document, insert it into the database.
    for doc in docs:
        # Convert the list of authors to a comma-separated string.
        authors_str = ", ".join(doc['authors'])
        add_document(
            session,
            topic_name=topic,
            title=doc['title'],
            text=doc['text'],
            pdf_link=doc['pdf_link'],
            authors=authors_str
        )
    
    session.close()
    print(f"Stored documents for topic: '{topic}' in the database.")
    return docs

if __name__ == "__main__":
    # Example: Fetch and store documents for multiple topics.
    topics = ["deep learning", "machine learning", "neural networks"]
    for topic in topics:
        download_and_save_topic_to_db(topic, total_results=20, batch_size=5)
