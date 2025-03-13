# src/app.py
import os
import streamlit as st
from retrieval import load_documents, create_embeddings, build_faiss_index, retrieve_documents
from generation import load_generator, generate_response
import re

def capitalize_sentences(text):
    sentences = re.split(r'([.!?]\s+)', text)
    capitalized = []
    for i in range(0, len(sentences), 2):
        sentence = sentences[i].strip().capitalize()
        separator = sentences[i+1] if i+1 < len(sentences) else ""
        capitalized.append(sentence + separator)
    return "".join(capitalized)

def main():
    st.title("Academic Research Assistant")
    
    # Inject custom CSS at the start of your app
    st.markdown(
        """
        <style>
        .generated-answer {
            font-size: 18px;
            color: #000000;  /* Change this to a lighter color if your background is dark */
            line-height: 1.6;
            background-color: #f9f9f9;  /* Optional: add a background color for better contrast */
            padding: 10px;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
)
    
    # Construct the path to your dataset from the project root
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(src_dir, '..')
    data_file = os.path.join(project_root, 'data', 'raw', 'arxiv_documents.json')
    
    # Load the documents
    documents = load_documents(data_file)
    st.write(f"Loaded {len(documents)} documents.")
    
    # Generate embeddings and build the FAISS index
    embeddings, embedder = create_embeddings(documents)
    index = build_faiss_index(embeddings)
    
    # Load the T5 generative model and tokenizer
    gen_model, tokenizer = load_generator("t5-small")
    
    # Accept a user query from the interface
    query = st.text_input("Enter your research query:")
    
    if query:
        # Retrieve top relevant documents
        retrieved_docs = retrieve_documents(query, embedder, index, documents, top_k=3)
        
        # Concatenate abstracts as context for the generative model
        context = " ".join([doc['text'] for doc in retrieved_docs])
        
        # Generate the answer
        answer = generate_response(query, context, gen_model, tokenizer)
        formatted_answer = capitalize_sentences(answer)
        
        # Use columns to display the generated answer and research papers side-by-side
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Generated Answer")
            st.markdown(f"<div class='generated-answer'>{formatted_answer}</div>", unsafe_allow_html=True)
        
        with col2:
            st.subheader("Relevant Research Papers")
            for i, doc in enumerate(retrieved_docs):
                st.markdown(f"**{doc['title']}**")
                st.write(doc['text'][:300] + "...")
                st.markdown(f"[View PDF]({doc['pdf_link']})")

if __name__ == "__main__":
    main()
