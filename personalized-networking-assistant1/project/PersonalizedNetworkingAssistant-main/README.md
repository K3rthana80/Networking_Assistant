# Personalized Networking Assistant

## Overview

The Personalized Networking Assistant is an AI-powered web application that helps users generate meaningful and context-aware conversation starters for networking events. It analyzes event descriptions using Hugging Face transformer models, verifies extracted topics through Wikipedia, and generates natural conversation prompts with GPT-2.

The project demonstrates Natural Language Processing (NLP), AI model integration, REST API development, frontend design, testing, and local deployment.

---

## Features

* Event theme extraction using DistilBERT
* AI-generated conversation starters using GPT-2 Small
* Wikipedia fact verification
* FastAPI backend
* Streamlit frontend
* JSON-based conversation history
* Feedback logging
* REST APIs
* Swagger documentation
* Unit testing using pytest
* API testing using httpx

---

## Tech Stack

* Python 3.11
* FastAPI
* Streamlit
* Hugging Face Transformers
* DistilBERT
* GPT-2 Small
* Wikipedia API
* Pytest
* HTTPX
* JSON Storage

---

## Project Structure

```
personalized-networking-assistant/

app/
frontend/
tests/
requirements.txt
README.md
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/SuvarnaRayudu/PersonalizedNetworkingAssistant.git
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

Windows

```bash
venv\Scripts\activate
```

Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run Backend

```bash
uvicorn app.main:app --reload
```

Swagger UI

```
http://127.0.0.1:8000/docs
```

---

## Run Frontend

```bash
streamlit run frontend/streamlit_app.py
```

Application

```
http://localhost:8501
```

---

## API Endpoints

### Analyze Event

```
POST /analyze-event
```

Extracts major networking themes.

---

### Generate Conversation

```
POST /generate-conversation
```

Creates personalized networking conversation starters.

---

### Fact Check

```
POST /fact-check
```

Verifies extracted topics using Wikipedia.

---

## Testing

Run all tests

```bash
pytest
```

Run API tests

```bash
pytest tests/test_routes.py
```

---

## Storage

Conversation history is stored in

```
history.json
```

Feedback is stored in

```
feedback.json
```

---

## Future Improvements

* User authentication
* MongoDB integration
* OpenAI LLM support
* Semantic search
* Conversation recommendation ranking

---

## Outcome

This project demonstrates practical implementation of NLP, AI model integration, REST API development, testing, frontend design, and local deployment using Python technologies.