# src/retrieval.py
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

def load_documents(filename):
    """Load documents from a JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_embeddings(documents, model_name='all-MiniLM-L6-v2'):
    """
    Generate embeddings for the document abstracts.
    Returns the list of embeddings and the SentenceTransformer model.
    """
    model = SentenceTransformer(model_name)
    texts = [doc['text'] for doc in documents]
    embeddings = model.encode(texts, convert_to_tensor=False)
    return embeddings, model

def build_faiss_index(embeddings):
    """
    Build a FAISS index from a list of embeddings.
    """
    embeddings_np = np.array(embeddings).astype('float32')
    dim = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings_np)
    return index

def retrieve_documents(query, model, index, documents, top_k=3):
    """
    Retrieve the top_k documents relevant to the query.
    """
    query_embedding = model.encode([query], convert_to_tensor=False)
    query_embedding_np = np.array(query_embedding).astype('float32')
    distances, indices = index.search(query_embedding_np, top_k)
    results = [documents[i] for i in indices[0]]
    return results

if __name__ == '__main__':
    # Load the dataset (adjust filename as needed)
    data_path = os.path.join('..','data', 'raw', 'arxiv_documents.json')
    documents = load_documents(data_path)
    print(f"Loaded {len(documents)} documents.")
    
    # Generate embeddings and build the FAISS index
    embeddings, model = create_embeddings(documents)
    index = build_faiss_index(embeddings)
    print("FAISS index built with {} vectors.".format(index.ntotal))
    
    # Test retrieval with a sample query
    sample_query = "What are the latest developments in convolutional neural networks?"
    results = retrieve_documents(sample_query, model, index, documents, top_k=3)
    
    print("\nTop Retrieved Documents:")
    for i, doc in enumerate(results):
        print(f"\nResult {i+1}:")
        print("Title:", doc['title'])
        print("Abstract:", doc['text'][:300] + "...")
        print("PDF Link:", doc['pdf_link'])