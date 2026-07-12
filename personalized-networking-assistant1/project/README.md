# Personalized Networking Assistant

An AI-powered web app that helps professionals walk into any event ready
to talk. Describe the event and a few of your interests, and it detects
the event's themes and generates three personalized conversation
starters — plus a Wikipedia-backed fact checker, conversation history,
and a feedback loop, all wrapped in a responsive, glassmorphic UI.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Backend](#running-the-backend)
- [Running the Frontend](#running-the-frontend)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [AI Models & Offline Fallbacks](#ai-models--offline-fallbacks)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Features

- **AI Event Theme Extraction** — zero-shot classification (`facebook/bart-large-mnli`) detects the top three themes in any event description.
- **AI Conversation Starters** — GPT-2 Small generates three short, professional icebreakers tailored to the event's themes and your stated interests.
- **Wikipedia Fact Checking** — look up any topic and get a clean, first-paragraph summary with a link to the full article.
- **Conversation History** — every generated set of starters is saved locally (JSON) and browsable, searchable, newest-first.
- **Feedback System** — like or dislike any suggestion; feedback is stored and viewable on its own page, filterable by like/dislike.
- **Modern, Responsive UI** — a conference-badge-inspired design system with light/dark mode, animated cards, toast notifications, and mobile-friendly navigation.
- **Fully Modular Backend** — FastAPI app split into schemas, services, and routers, each independently testable.
- **No Database Required** — all persistence is local JSON with atomic writes.

---

## Tech Stack

**Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2, Requests, Hugging Face Transformers, Torch, `wikipedia`
**Frontend:** HTML5, CSS3 (custom design system, no framework dependency), vanilla JavaScript
**AI Models:** `facebook/bart-large-mnli` (zero-shot theme extraction), `gpt2` (conversation generation), Wikipedia API (fact checking)
**Testing:** pytest, httpx `TestClient`, pytest-cov
**Storage:** local JSON files (`history.json`, `feedback.json`) — no SQL database

---

## Project Structure

```
project/
├── app/
│   ├── main.py                  # FastAPI app, CORS, error handlers, route registration
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models + validation
│   ├── services/
│   │   ├── event_analyzer.py    # Zero-shot theme extraction (+ keyword fallback)
│   │   ├── topic_generator.py   # GPT-2 conversation generation (+ template fallback)
│   │   ├── fact_checker.py      # Wikipedia lookup with graceful error handling
│   │   ├── history_logger.py    # Atomic JSON read/write for conversation history
│   │   └── feedback_logger.py   # Atomic JSON read/write for feedback
│   └── routers/
│       └── conversation.py      # All API endpoints
├── frontend/
│   ├── index.html               # Home page (hero, features, how it works, models)
│   ├── networking.html          # Networking Assistant tool
│   ├── fact-checker.html        # Fact Checker tool
│   ├── history.html             # Conversation History
│   ├── feedback.html            # Feedback dashboard
│   ├── style.css                # Shared design system
│   └── script.js                # Shared frontend logic (API calls, theming, nav, toasts)
├── tests/
│   ├── test_routes.py
│   ├── test_event_analyzer.py
│   ├── test_generator.py
│   └── test_fact_checker.py
├── history.json
├── feedback.json
├── requirements.txt
├── pytest.ini
└── README.md
```

> Note: the brief's file tree names the frontend's two feature pages
> generically; this implementation names them `networking.html` and
> `fact-checker.html` for clarity, alongside the explicitly-named
> `index.html`, `history.html`, and `feedback.html`.

---

## Installation

### 1. Clone / unzip the project and enter it

```bash
cd project
```

### 2. Create a virtual environment

```bash
python3 -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note on model downloads:** `transformers` and `torch` are used for
> the highest-quality theme extraction and text generation. The first
> time each model runs, Hugging Face will download it (~1.6 GB for
> BART-large-MNLI, ~550 MB for GPT-2), which requires an internet
> connection. If those packages aren't installed, or the download
> can't complete, both AI services **automatically fall back** to
> fast, deterministic, fully-offline heuristics (keyword matching and
> templated questions) — the app keeps working end-to-end either way.

---

## Running the Backend

From the `project/` root, with the virtual environment active:

```bash
uvicorn app.main:app --reload
```

The API is now running at `http://127.0.0.1:8000`, with interactive
docs at `http://127.0.0.1:8000/docs`.

---

## Running the Frontend

The frontend is static HTML/CSS/JS — no build step required.

**Option A — open directly:**
Open `frontend/index.html` in your browser.

**Option B — serve it (recommended, avoids `file://` quirks):**

```bash
cd frontend
python3 -m http.server 5500
```

Then visit `http://127.0.0.1:5500`.

Make sure the backend (`uvicorn`) is running at the same time — the
frontend calls it directly for every action.

---

## Running Tests

```bash
pytest --cov=app --cov-report=term-missing
```

All AI model calls and file storage are mocked/redirected in tests, so
the suite runs fully offline and fast. Tests cover:

- Every API route (`test_routes.py`) — success paths, validation
  errors (422), and history/feedback persistence.
- The event analyzer's keyword-fallback theme detection.
- The topic generator's template-fallback conversation starters.
- The fact checker's handling of found pages, missing pages,
  disambiguation, and network failures.

---

## API Documentation

Full interactive documentation is auto-generated by FastAPI at
`/docs` (Swagger UI) and `/redoc` once the server is running. Summary:

| Method | Endpoint                | Description                                             |
|--------|--------------------------|-----------------------------------------------------------|
| POST   | `/analyze-event`         | Extract top 3 themes from an event description            |
| POST   | `/generate-conversation` | Detect themes + generate 3 conversation starters (logs it) |
| POST   | `/fact-check`             | Get a Wikipedia summary for a topic                        |
| GET    | `/history`                | List all past conversations, newest first                  |
| GET    | `/feedback`               | List all recorded feedback, newest first                   |
| POST   | `/feedback`               | Record a like/dislike for a suggestion                     |

### Example: `POST /generate-conversation`

Request:
```json
{
  "description": "AI for Sustainable Cities Conference",
  "interests": ["Artificial Intelligence", "Climate Change", "Urban Planning"]
}
```

Response:
```json
{
  "themes": ["Artificial Intelligence", "Climate Change", "Urban Planning"],
  "suggestions": [
    "What inspired you to attend this event?",
    "Which AI innovations excite you most?",
    "How do you see sustainability evolving?"
  ]
}
```

Invalid requests return `422` with a structured validation error body;
unexpected server-side failures return `500` with a plain-language
`detail` message.

---

## AI Models & Offline Fallbacks

| Service            | Primary Model                  | Fallback (if model unavailable)       |
|---------------------|----------------------------------|------------------------------------------|
| Theme extraction    | `facebook/bart-large-mnli` (zero-shot) | Keyword matching against a curated theme list |
| Conversation generation | `gpt2` (small)               | Template engine combining themes + interests |
| Fact checking        | Wikipedia API                  | Friendly "not found" / "temporarily unavailable" messages |

This means the app is demoable and fully testable without GPU access,
large downloads, or even an internet connection — while still using
real transformer models when they're available.

---

## Screenshots

_Add screenshots of the Home, Networking Assistant, Fact Checker,
History, and Feedback pages here once the app is running locally._

```
docs/screenshots/home.png
docs/screenshots/networking-assistant.png
docs/screenshots/fact-checker.png
docs/screenshots/history.png
docs/screenshots/feedback.png
```

---

## Future Improvements

- Swap local JSON storage for a lightweight embedded database (e.g. SQLite) as history grows.
- Add user accounts so history/feedback are personal rather than shared per-machine.
- Fine-tune the conversation generator on a curated icebreaker dataset instead of relying on base GPT-2.
- Add streaming responses for conversation generation to show starters as they're produced.
- Support event agendas/speaker lists as additional theme-extraction input.
- Add export (PDF/CSV) of conversation history for offline use at events.

---

## License

MIT License. See `LICENSE` for details (or add one — none is bundled
by default with this scaffold).
