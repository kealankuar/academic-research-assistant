# src/app.py

import streamlit as st
import os
from data_acquisition import download_and_save_topic
from retrieval import load_documents, create_embeddings, build_faiss_index, retrieve_documents
from generation import load_generator, generate_response

def acquisition_tab():
    st.header("Data Acquisition")
    st.write("Fetch research papers from arXiv for one or more topics. Enter the topics separated by commas (e.g., deep learning, machine learning, neural networks).")
    
    # Input: Allow multiple topics as a comma-separated string
    topic_input = st.text_input("Enter the research topics:")
    num_docs = st.number_input("Number of documents to fetch per topic:", min_value=5, max_value=200, value=50, step=5)
    
    if st.button("Fetch Documents"):
        if topic_input.strip() == "":
            st.error("Please enter at least one topic.")
        else:
            topics = [t.strip() for t in topic_input.split(",") if t.strip()]
            if not topics:
                st.error("Please enter valid topics separated by commas.")
            else:
                all_docs = []
                for topic in topics:
                    with st.spinner(f"Fetching documents for topic: {topic}..."):
                        docs = download_and_save_topic(topic, total_results=int(num_docs), batch_size=5)
                        all_docs.extend(docs)
                st.success(f"Fetched a total of {len(all_docs)} documents across {len(topics)} topics.")
                # Optionally, display a preview of the first document from the first topic:
                if all_docs:
                    st.write("Example Document:", all_docs[0])
                    
                # Optionally, save combined topics into one file (if required)
                combined_filename = os.path.join("data", "raw", "arxiv_combined_documents.json")
                with open(combined_filename, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(all_docs, f, indent=2)
                st.info(f"Combined dataset saved to {combined_filename}")



def main_app_tab():
    st.header("Main App: Query Research Papers")
    
    # Determine the path to the combined dataset
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    data_file = os.path.join(project_root, "data", "raw", "arxiv_combined_documents.json")
    
    if os.path.exists(data_file):
        documents = load_documents(data_file)
        st.write(f"Loaded {len(documents)} documents.")
        
        # Build the retrieval pipeline
        with st.spinner("Preparing retrieval index..."):
            embeddings, embedder = create_embeddings(documents)
            index = build_faiss_index(embeddings)
        
        gen_model, tokenizer = load_generator("t5-small")
        
        # User query input
        query = st.text_input("Enter your research query:")
        if query:
            with st.spinner("Retrieving and generating response..."):
                retrieved_docs = retrieve_documents(query, embedder, index, documents, top_k=3)
                # Combine the retrieved abstracts as context
                context = " ".join([doc['text'] for doc in retrieved_docs])
                answer = generate_response(query, context, gen_model, tokenizer)
            
            st.subheader("Generated Answer")
            st.write(answer)
            
            st.subheader("Relevant Research Papers")
            for i, doc in enumerate(retrieved_docs):
                st.write(f"**{doc['title']}**")
                st.write(doc['text'][:300] + "...")
                st.markdown(f"[View PDF]({doc['pdf_link']})")
    else:
        st.error("No dataset found. Please use the Data Acquisition tab to fetch documents first.")

# Main dashboard title and tabs
st.title("Academic Research Assistant Dashboard")
tab1, tab2 = st.tabs(["Data Acquisition", "Main App"])

with tab1:
    acquisition_tab()

with tab2:
    main_app_tab()
