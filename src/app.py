# src/app.py
import streamlit as st
import os
import pandas as pd
from data_acquisition import download_and_save_topic_to_db
from db import get_session
from models import Topic

# Utility function to fetch all topics from the database
def get_all_topics():
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
    topics = get_all_topics()
    if topics:
        # Convert list of Topic objects to a list of dictionaries
        topics_data = [
            {"Topic": t.name, "Document Count": t.document_count} for t in topics
        ]
        df = pd.DataFrame(topics_data)
        st.subheader("Topics Summary")
        st.dataframe(df)
    else:
        st.info("No topics found in the database yet.")

def acquisition_tab():
    st.header("Data Acquisition")
    st.write("Enter one or more research topics (comma separated) to fetch and store documents from arXiv into the database.")
    
    topics_input = st.text_input("Enter topics", "deep learning, machine learning, neural networks")
    num_docs = st.number_input("Number of documents per topic", min_value=1, max_value=200, value=50, step=5)
    
    if st.button("Fetch Documents"):
        topics = [topic.strip() for topic in topics_input.split(",") if topic.strip()]
        if not topics:
            st.error("Please enter at least one valid topic.")
        else:
            errors = []
            # Optionally, you could create a progress bar. Here, we use the spinner for each topic.
            for topic in topics:
                try:
                    with st.spinner(f"Fetching documents for '{topic}' ..."):
                        download_and_save_topic_to_db(topic, total_results=int(num_docs), batch_size=5)
                except Exception as e:
                    errors.append(f"Error for topic '{topic}': {e}")
            if errors:
                for err in errors:
                    st.error(err)
            else:
                st.success("Documents fetched and saved to the database successfully.")
            # Display updated topics summary after fetching
            display_topics_summary()
    else:
        # Show summary even if the button hasn't been clicked yet.
        display_topics_summary()

def main_app_tab():
    st.header("Research Query")
    st.write("This tab will eventually allow you to query the stored documents in the database.")
    
    # Placeholder for future retrieval & query features
    query = st.text_input("Enter your research query:")
    if query:
        st.info("Querying feature is under construction. Please check back later.")

def main():
    st.title("Academic Research Assistant Dashboard")
    tab1, tab2 = st.tabs(["Data Acquisition", "Main App"])
    
    with tab1:
        acquisition_tab()
    
    with tab2:
        main_app_tab()

if __name__ == "__main__":
    main()
