# src/app.py

import os
import time
import streamlit as st
import pandas as pd

# For retrieval embeddings and FAISS index
from sentence_transformers import SentenceTransformer
import faiss

# Import your own modules
from data_acquisition import download_and_save_topic_to_db
from db import get_session
from models import Topic, Document
from cache_utils import cached_fetch_topic, normalize_topic
from generation import load_generator, generate_response

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
                        # Use caching with incremental fetching. If force_refresh is checked, bypass cache.
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

# ----------------- Main App Tab (Retrieval and Generation) -----------------

def main_app_tab():
    st.header("Research Query and Answer Generation")
    st.write("Enter your query and select a topic. The app will retrieve the most relevant documents using similarity search and generate an answer using your generative model.")
    
    query = st.text_input("Enter your research query:")
    topic_for_context = st.text_input("Enter the topic to retrieve context from", "deep learning")
    
    # Model selection and generation parameters
    model_option = st.selectbox("Select generative model", options=["t5-small", "t5-base", "t5-large"], index=0)
    max_length = st.slider("Max generated length", min_value=50, max_value=500, value=150, step=10)
    num_beams = st.slider("Number of beams", min_value=1, max_value=10, value=4, step=1)
    top_k = st.slider("Number of documents to retrieve", min_value=1, max_value=10, value=3, step=1)
    
    if query and topic_for_context:
        # Load documents from the database for the given topic
        session = get_session()
        topic_id = session.query(Topic.id).filter(Topic.name.ilike(f"%{topic_for_context.strip().lower()}%")).scalar()
        if topic_id is None:
            st.warning("No documents found for the given topic. Please fetch documents for this topic using the Data Acquisition tab.")
            session.close()
            return

        docs = session.query(Document).filter(Document.topic_id == topic_id).all()
        session.close()
        
        if not docs:
            st.warning("No documents found for the given topic. Please fetch documents for this topic using the Data Acquisition tab.")
            return

        # Prepare document texts for retrieval.
        doc_texts = [doc.text for doc in docs]
        st.write(f"Loaded {len(doc_texts)} documents for topic '{topic_for_context}'.")
        
        # Build embeddings with a SentenceTransformer model.
        embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = embed_model.encode(doc_texts, convert_to_numpy=True)
        dim = embeddings.shape[1]
        
        # Build a FAISS index from the embeddings.
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        
        # Embed the user's query.
        query_embedding = embed_model.encode([query], convert_to_numpy=True)
        distances, indices = index.search(query_embedding, top_k)
        
        # Retrieve the most similar documents.
        retrieved_docs = [docs[i] for i in indices[0] if i < len(docs)]
        
        st.subheader("Retrieved Documents")
        for doc in retrieved_docs:
            # Display a hyperlink with the document title that points to the PDF link.
            st.markdown(f"[{doc.title}]({doc.pdf_link})", unsafe_allow_html=True)
        
        # Combine the retrieved document texts to form context.
        context = " ".join([doc.text for doc in retrieved_docs])
        st.subheader("Context Used for Generation")
        st.write(context[:500] + " ...")  # Display first 500 characters
        
        # Load the generative model.
        with st.spinner("Loading generative model..."):
            gen_model, tokenizer = load_generator(model_name=model_option)
        
        # Generate an answer based on the query and context.
        with st.spinner("Generating answer..."):
            answer = generate_response(query, context, gen_model, tokenizer, max_length=max_length, num_beams=num_beams)
        
        st.subheader("Generated Answer")
        st.write(answer)
    else:
        st.info("Please enter a research query and a topic for context.")


# ----------------- Main Function -----------------

def main():
    st.title("Academic Research Assistant Dashboard")
    tab1, tab2 = st.tabs(["Data Acquisition", "Main App"])
    
    with tab1:
        acquisition_tab()
    
    with tab2:
        main_app_tab()

if __name__ == "__main__":
    main()
