# src/generation.py
from transformers import T5ForConditionalGeneration, T5Tokenizer

def load_generator(model_name="t5-small"):
    """
    Load the T5 model and tokenizer.
    You can change model_name to, e.g., "t5-base" or "t5-large" as desired.
    """
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    return model, tokenizer

def generate_response(query, context, model, tokenizer, max_length=150, num_beams=4):
    """
    Generate a response given a query and context.
    Combines query and context, encodes them, and generates an answer.
    """
    input_text = f"question: {query} context: {context}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(input_ids, max_length=max_length, num_beams=num_beams, early_stopping=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response
