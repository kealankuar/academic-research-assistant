# src/app.py
import os
from retrieval import load_documents, create_embeddings, build_faiss_index, retrieve_documents
from generation import load_generator, generate_response

def main():
    # Construct the path to the JSON dataset stored in data/raw/
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(src_dir, '..')
    data_file = os.path.join(project_root, 'data', 'raw', 'arxiv_documents.json')
    
    # Load documents from the JSON file
    documents = load_documents(data_file)
    print(f"Loaded {len(documents)} documents.")
    
    # Generate embeddings for the document abstracts and build the FAISS index
    embeddings, embedder = create_embeddings(documents)
    index = build_faiss_index(embeddings)
    print("FAISS index built with {} vectors.".format(index.ntotal))
    
    # Load the T5 generative model and tokenizer
    gen_model, tokenizer = load_generator("t5-small")
    
    # Accept a user query from the command line
    query = input("Enter your research query: ")
    
    # Retrieve top relevant documents (e.g., top 3)
    retrieved_docs = retrieve_documents(query, embedder, index, documents, top_k=3)
    
    # Combine the retrieved abstracts into a single context string
    context = " ".join([doc['text'] for doc in retrieved_docs])
    
    # Generate a response using the query and the combined context
    answer = generate_response(query, context, gen_model, tokenizer)
    
    print("\nGenerated Answer:")
    print(answer)

if __name__ == '__main__':
    main()
