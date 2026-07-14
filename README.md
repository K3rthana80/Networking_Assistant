# Personalized Networking Assistant

An AI-powered web application that helps users generate intelligent and personalized conversation starters for professional networking events. The application uses **DistilBERT** for event theme extraction, **GPT-2** for conversation generation, and the **Wikipedia API** for fact verification.

---

## ✨ Features

- Event Theme Analysis using DistilBERT
- AI-powered Conversation Starter Generation
- Wikipedia-based Fact Verification
- Conversation History Management
- User Feedback Collection
- Interactive Streamlit Interface
- FastAPI REST Backend

---

## 🛠️ Tech Stack

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

## 📂 Project Structure

```text
Networking_Assistant/
│
├── app/
├── services/
├── routes/
├── history.json
├── feedback.json
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

Clone the repository:

```bash
git clone https://github.com/K3rthana80/Networking_Assistant.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI backend:

```bash
uvicorn main:app --reload
```

Launch the Streamlit application:

```bash
streamlit run app.py
```

---

## 🔮 Future Enhancements

- Cloud Deployment
- Database Integration
- LinkedIn Integration
- OAuth Authentication
- Multi-language Support

---

Developed as part of the **SmartBridge GenAI Virtual Internship Program**.
