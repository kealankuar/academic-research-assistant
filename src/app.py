# src/app.py

import streamlit as st
import os
import pandas as pd
import time

# Import the data acquisition functions.
from data_acquisition import download_and_save_topic_to_db
# Import the database session getter.
from db import get_session
# Import the Topic model to fetch topics.
from models import Topic
# Import caching utilities from cache_utils module.
from cache_utils import cached_fetch_topic, normalize_topic

# ----------------- Helper Functions -----------------

def get_all_topics():
    """Fetch all topics from the PostgreSQL database."""
    session = get_session()
    try:
        topics = session.query(Topic).all()
    except Exception as e:
        st.error(f"Error retrieving topics: {e}")
        topics = []
    finally:
        session.close()
    return topics

def display_topics_summary():
    """Display a summary table of topics and their document counts."""
    topics = get_all_topics()
    if topics:
        topics_data = [{"Topic": t.name, "Document Count": t.document_count} for t in topics]
        df = pd.DataFrame(topics_data)
        st.subheader("Topics Summary")
        st.dataframe(df)
    else:
        st.info("No topics found in the database yet.")

# ----------------- Data Acquisition Tab -----------------

def acquisition_tab():
    st.header("Data Acquisition")
    st.write("Enter one or more research topics (comma separated) to fetch and store documents from arXiv into the database.")
    
    topics_input = st.text_input("Enter topics", "deep learning, machine learning, neural networks")
    num_docs = st.number_input("Number of documents per topic", min_value=1, max_value=200, value=50, step=5)
    force_refresh = st.checkbox("Force refresh data for these topics", value=False)
    
    if st.button("Fetch Documents"):
        topics = [topic.strip() for topic in topics_input.split(",") if topic.strip()]
        if not topics:
            st.error("Please enter at least one valid topic.")
        else:
            errors = []
            for topic in topics:
                try:
                    with st.spinner(f"Fetching documents for '{topic}' ..."):
                        # If force_refresh is checked, set fetch_interval to 0 so we bypass the cache.
                        fetch_interval = 0 if force_refresh else 3600
                        data, from_cache = cached_fetch_topic(topic, total_requested=int(num_docs), fetch_interval=fetch_interval)
                        if from_cache:
                            st.info(f"Using cached data for topic '{topic}'.")
                        else:
                            st.success(f"Fetched fresh data for topic '{topic}'.")
                except Exception as e:
                    errors.append(f"Error fetching topic '{topic}': {e}")
            if errors:
                for err in errors:
                    st.error(err)
            display_topics_summary()
    else:
        display_topics_summary()

# ----------------- Main App Tab (Placeholder) -----------------

def main_app_tab():
    st.header("Research Query")
    st.write("This tab will eventually allow you to query the stored documents in the database.")
    query = st.text_input("Enter your research query:")
    if query:
        st.info("Querying feature is under construction. Please check back later.")

# ----------------- Main Function -----------------

def main():
    st.title("Academic Research Assistant Dashboard")
    # Create two tabs: one for Data Acquisition, one for Main App.
    tab1, tab2 = st.tabs(["Data Acquisition", "Main App"])
    
    with tab1:
        acquisition_tab()
    
    with tab2:
        main_app_tab()

if __name__ == "__main__":
    main()
