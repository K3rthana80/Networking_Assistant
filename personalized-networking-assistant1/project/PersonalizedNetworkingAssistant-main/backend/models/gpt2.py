from transformers import pipeline

generator = pipeline(
    task="text-generation",
    model="gpt2",
    tokenizer="gpt2",
    pad_token_id=50256,
    device=-1
)