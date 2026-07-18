import re

from backend.models.gpt2 import generator


def build_prompt(event, interest, themes, summary):

    theme_names = ", ".join(
        theme["theme"] for theme in themes
    )

    prompt = f"""
You are a professional networking coach.

Event:
{event}

User Interest:
{interest}

Detected Themes:
{theme_names}

Verified Context:
{summary}

Write ONE short, friendly networking conversation starter.

Conversation Starter:
"""

    return prompt.strip()


def clean_output(text: str):

    text = text.strip()

    # Remove repeated prompt markers
    text = text.replace("Conversation Starter:", "").strip()

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Keep only the first sentence if GPT rambles
    sentences = re.split(r'(?<=[.!?])\s+', text)

    if sentences:
        text = sentences[0]

    return text


def generate_conversation(event, interest, themes, summary):

    prompt = build_prompt(
        event,
        interest,
        themes,
        summary
    )

    result = generator(
        prompt,
        max_new_tokens=50,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.3,
        no_repeat_ngram_size=3,
        num_return_sequences=1
    )

    generated = result[0]["generated_text"]

    generated = generated.replace(prompt, "")

    conversation = clean_output(generated)

    if len(conversation) < 15:

        conversation = (
            f"Hi! I noticed you're interested in {interest}. "
            "What inspired you to attend this event?"
        )

    return conversation