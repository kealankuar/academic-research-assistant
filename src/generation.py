# src/generation.py

from transformers import T5ForConditionalGeneration, T5Tokenizer

def load_generator(model_name="t5-small"):
    """
    Load the T5 model and tokenizer.
    """
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    return model, tokenizer

def generate_response(query, context, model, tokenizer, max_length=150):
    """
    Generate a response by combining the query and context.
    
    Args:
        query (str): The user's query.
        context (str): Combined text from the retrieved documents.
        model: The pre-trained generative model.
        tokenizer: The tokenizer corresponding to the model.
        max_length (int): Maximum length of the generated output.
    
    Returns:
        str: The generated answer.
    """
    # Format input text to include both the query and the context.
    # This format can be adjusted based on your experimentation.
    input_text = f"question: {query} context: {context}"
    
    # Encode the input text into token IDs. We use truncation and a max_length for safety.
    input_ids = tokenizer.encode(input_text, return_tensors="pt", truncation=True, max_length=512)
    
    # Generate a response using beam search for better quality.
    outputs = model.generate(input_ids, max_length=max_length, num_beams=4, early_stopping=True)
    
    # Decode the generated token IDs back to a string.
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

if __name__ == "__main__":
    # Test the generative component standalone.
    model, tokenizer = load_generator("t5-small")
    sample_query = "What are the recent advancements in deep learning?"
    sample_context = (
        "Deep learning is evolving rapidly with improvements in neural network architectures, "
        "optimization techniques, and applications across various domains such as computer vision and NLP."
    )
    answer = generate_response(sample_query, sample_context, model, tokenizer)
    print("Generated Answer:", answer)