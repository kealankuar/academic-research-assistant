# src/cache_utils.py
import time
from data_acquisition import query_arxiv_paginated, process_entries, download_and_save_topic_to_db
from data_access import add_document
from db import get_session
from data_acquisition import query_arxiv  # if needed for individual calls

# Global in-memory cache for fetched topics.
# Format: { normalized_topic: (timestamp, [list_of_documents], count) }
FETCH_CACHE = {}

def normalize_topic(topic):
    """Simple normalization: lowercase and trim whitespace."""
    return topic.strip().lower()

def cached_fetch_topic(topic, total_requested, fetch_interval=3600):
    """
    Fetch documents for the given topic using an incremental caching mechanism.

    Args:
        topic (str): The topic to fetch documents for.
        total_requested (int): The total number of documents the user is requesting.
        fetch_interval (int): The minimum time (in seconds) to wait before re-fetching.
    
    Returns:
        Tuple: (data, from_cache) where data is the list of documents and
               from_cache is True if the data came from the cache.
    
    Behavior:
        - If the topic is not in cache or the cache is too old, fetch fresh data.
        - If the topic is cached but the cached count is less than total_requested,
          fetch only the missing documents (starting from the current offset).
        - If cached data meets the requested count and is fresh, return cached data.
    """
    normalized_topic = normalize_topic(topic)
    current_time = time.time()
    session = None

    # Check if we have cached data for this topic.
    if normalized_topic in FETCH_CACHE:
        last_fetch, data, count = FETCH_CACHE[normalized_topic]
        # If the cache is fresh:
        if current_time - last_fetch < fetch_interval:
            if count >= total_requested:
                # Enough data is in the cache.
                return data, True
            else:
                # Determine how many more documents are needed.
                missing = total_requested - count
                # Fetch additional documents starting from the current offset.
                new_entries = query_arxiv_paginated(topic, total_results=missing, batch_size=5, start=count)
                new_docs = process_entries(new_entries)
                # Insert the new documents into the database.
                session = get_session()
                for doc in new_docs:
                    add_document(session,
                                 topic_name=topic,
                                 title=doc['title'],
                                 text=doc['text'],
                                 pdf_link=doc['pdf_link'],
                                 authors=", ".join(doc['authors']))
                if session:
                    session.close()
                # Update our cached data.
                data.extend(new_docs)
                new_total = count + len(new_docs)
                FETCH_CACHE[normalized_topic] = (current_time, data, new_total)
                return data, False
        # If the cache is too old, fall through to re-fetch fresh data.
    
    # If there's no cache or it's expired, perform a full fetch.
    # For a full fetch, fetch the total_requested number of documents.
    new_data = download_and_save_topic_to_db(topic, total_results=total_requested, batch_size=5)
    # Create a new cache entry.
    FETCH_CACHE[normalized_topic] = (current_time, new_data, len(new_data))
    return new_data, False
