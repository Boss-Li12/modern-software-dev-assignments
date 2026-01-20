# Action Item Extractor

An intelligent note-taking tool that automatically extracts actionable tasks from your free-form notes using both heuristic rules and Local LLMs (Ollama + Llama 3).

## 🌟 Features

- **Store Notes**: Save and manage your meeting notes, ideas, and brain dumps.
- **Smart Extraction**:
  - **Rule-Based**: Fast extraction using regex patterns (bullets, checkboxes, keywords like `todo:`).
  - **AI-Powered**: Deep semantic extraction using local LLMs (Llama 3 via Ollama) to find tasks in narrative text.
- **Web Interface**: Simple, responsive frontend to manage notes and action items.
- **RESTful API**: Fully documented API built with FastAPI.
- **SQLite Database**: Lightweight, zero-config persistence.

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic, SQLite
- **AI/LLM**: Ollama, Llama 3.1
- **Frontend**: Vanilla HTML/JS/CSS
- **Testing**: Pytest, FastAPI TestClient

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+** and **Poetry** installed.
2. **Ollama** installed and running locally.
3. Pull the required model:
   ```bash
   ollama pull llama3.1:8b
   ```

### Installation

1. Navigate to the project directory:
   ```bash
   cd week2
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Create a `.env` file (optional, defaults are provided in `app/config.py`):
   ```env
   APP_DEBUG=true
   APP_DEFAULT_LLM_MODEL=llama3.1:8b
   ```

### Running the Application

Start the development server:

```bash
poetry run uvicorn week2.app.main:app --reload
```

Open your browser and visit: **http://127.0.0.1:8000**

## 🔌 API Documentation

The API comes with automatic Swagger UI documentation available at:
**http://127.0.0.1:8000/docs**

### Key Endpoints

#### Action Items
- `POST /action-items/extract`: Extract items from text.
  - Body: `{"text": "...", "use_llm": true, "save_note": true}`
- `GET /action-items`: List all action items.
- `POST /action-items/{id}/done`: Mark an item as complete.

#### Notes
- `GET /notes`: List all saved notes.
- `POST /notes`: Create a new note manually.
- `DELETE /notes/{id}`: Delete a note and its associated tasks.

## 🧪 Running Tests

This project includes unit tests and integration tests.

### Run Unit Tests
Test the extraction logic and API endpoints:

```bash
poetry run pytest week2/tests/
```

### Run Integration Tests
Verify the full frontend-backend flow (requires backend to be simulated):

```bash
PYTHONPATH=. poetry run python week2/test_integration.py
```

## 📂 Project Structure

```
week2/
├── app/
│   ├── routers/      # API endpoints (notes, action_items)
│   ├── services/     # Business logic (LLM extraction)
│   ├── config.py     # Application settings
│   ├── db.py         # Database operations
│   ├── main.py       # App factory & lifecycle
│   ├── models.py     # Pydantic schemas
│   └── exceptions.py # Custom error handling
├── frontend/         # Static HTML/JS assets
├── tests/            # Pytest suite
└── data/             # SQLite database storage
```

## 📝 License

This project is part of the Modern Software Development course assignments.
