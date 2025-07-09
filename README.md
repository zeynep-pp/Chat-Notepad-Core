# ChatNotePad.Ai Agent Backend

[UI Code Repository](https://github.com/zeynep-pp/ChatNotePad.Ai)

ChatNotePad.Ai is a backend agent for a note-taking application that processes natural language commands to edit user text. It exposes a FastAPI server with a `/prompt` endpoint, designed to be integrated with a modern frontend (React, Monaco/CodeMirror, etc.).

---

## 🧩 Architecture

| Frontend (UI) | → | FastAPI Backend (`/prompt`) | → | Agent (Rule-based & LLM) | → | diff-match-patch |
|:-------------:|:-:|:--------------------------:|:-:|:------------------------:|:-:|:----------------:|
|               | ← |        (returns)           | ← |         (returns)        |    |                  |

- **Frontend**: React + Monaco/CodeMirror (not included here)
- **Backend**: FastAPI (this repo)
- **Text Processing**: Rule-based Python functions, ready for LLM integration
- **Diff Calculation**: `diff-match-patch` (HTML output for diff viewer)

---

## 🚀 Features
- Accepts user text and natural language command
- Processes commands (remove, replace, capitalize, etc.)
- Returns both the edited text and a visual diff (HTML)
- CORS enabled for easy frontend integration
- Easily extendable for LLM (OpenAI) support

---

## 🛠️ API Usage
### POST `/prompt`
**Request:**
```json
{
  "text": "Hello, how are you? Today is a beautiful day, isn't it?",
  "command": "Remove all ',' characters from the text."
}
```
**Response:**
```json
{
  "result": "Hello how are you? Today is a beautiful day isn't it?",
  "diff": "<span>Hello</span><del>,</del><span> how are you? Today is a beautiful day</span><del>,</del><span> isn't it?</span>"
}
```

---

## ⚙️ Setup
1. **Install dependencies:**
   ```sh
   python3 -m pip install -r requirements.txt
   ```
2. **Run the server:**
   ```sh
   python3 -m uvicorn main:app --reload
   ```
3. **Test the endpoint:**
   Use Postman, Insomnia, or curl:
   ```sh
   curl -X POST "http://127.0.0.1:8000/prompt" -H "Content-Type: application/json" -d '{"text": "Hello, how are you? Today is a beautiful day, isn't it?", "command": "Remove all ',' characters from the text."}'
   ```

---

## 🧠 Extending the Agent
- Add new command logic in `agent.py` (e.g., paragraph numbering, advanced replacements)
- Integrate LLM (OpenAI API) for more complex natural language understanding
- Customize diff output in `diff_utils.py` for your frontend

---

## 📁 Project Structure
- `main.py` – FastAPI app and endpoints
- `agent.py` – Command parsing and text processing logic
- `diff_utils.py` – Diff calculation utilities
- `requirements.txt` – Python dependencies

---

## 📝 Example Use Case
**Input:**
- Text: `Hello, how are you? Today is a beautiful day, isn't it?`
- Command: `Remove all ',' characters from the text.`

**Output:**
- Result: `Hello how are you? Today is a beautiful day isn't it?`
- Diff: (HTML, for visual diff viewer)

---

## 🦾 Ready for Frontend Integration
- Designed for use with React, Monaco/CodeMirror, and `react-diff-viewer`
- CORS enabled by default
- Returns HTML diff for easy highlighting of changes

---

## 📬 Contact & Contribution
Feel free to open issues or PRs for improvements, new features, or bug fixes!