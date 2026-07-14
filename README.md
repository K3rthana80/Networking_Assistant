# Personalized Networking Assistant

An AI-powered web application that helps users generate intelligent and personalized conversation starters for professional networking events. The application leverages Natural Language Processing (NLP) and Generative AI to analyze event descriptions, generate context-aware conversation suggestions, verify facts, and maintain conversation history.

---

## ✨ Features

- Event Theme Analysis using DistilBERT
- AI-powered Conversation Starter Generation using GPT-2
- Wikipedia-based Fact Verification
- Conversation History Management
- User Feedback Collection
- FastAPI REST Backend
- Interactive Streamlit Frontend

---

## 🛠️ Technology Stack

- Python
- FastAPI
- Streamlit
- Hugging Face Transformers
- DistilBERT
- GPT-2
- Wikipedia API
- JSON
- Pytest

---

## 🏗️ System Architecture

![System Architecture](Architecture.png)

---

## 📂 Project Structure

```text
Networking_Assistant/
│── app/
│── services/
│── routes/
│── history.json
│── feedback.json
│── requirements.txt
│── README.md
```

---

## ▶️ Getting Started

### Clone the Repository

```bash
git clone https://github.com/K3rthana80/Networking_Assistant.git
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Backend

```bash
uvicorn main:app --reload
```

### Launch the Frontend

```bash
streamlit run app.py
```

---

## 🔮 Future Enhancements

- Cloud Deployment
- Database Integration (PostgreSQL / MongoDB)
- OAuth Authentication
- LinkedIn Integration
- Multi-language Support

---

Developed as part of the **SmartBridge GenAI Virtual Internship Program**.
