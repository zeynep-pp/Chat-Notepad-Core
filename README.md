# ChatNotePad.Ai Backend

[UI Code Repository](https://github.com/zeynep-pp/ChatNotePad.Ai)

ChatNotePad.Ai is a modern multi-agent backend for intelligent text processing. Built with FastAPI, it features specialized agents for different text operations like editing and summarization, powered by AI/LLM integration.

---

## 🧩 Multi-Agent Architecture

| Frontend (UI) | → | FastAPI Backend | → | Agent Manager | → | Specialized Agents | → | AI/LLM |
|:-------------:|:-:|:--------------:|:-:|:-------------:|:-:|:------------------:|:-:|:------:|
|               | ← |   (returns)    | ← |   (returns)   | ← |     (returns)      | ← |        |

- **Frontend**: React + Monaco/CodeMirror (not included here)
- **Backend**: FastAPI with multi-agent architecture
- **Agent Manager**: Routes requests to appropriate specialized agents
- **Agents**: TextEditorAgent, SummarizerAgent (easily extensible)
- **AI Integration**: OpenAI GPT for complex text processing
- **Diff Calculation**: `diff-match-patch` (HTML output for diff viewer)

---

## 🚀 Features
- **Multi-Agent System**: Specialized agents for different tasks
- **AI-Powered**: OpenAI integration for intelligent text processing
- **Text Editing**: Rule-based and AI-powered text transformations
- **Text Summarization**: AI-powered summarization with different styles
- **Visual Diff**: HTML diff output for frontend integration
- **RESTful API**: Clean REST endpoints with proper error handling
- **Extensible**: Easy to add new agents and capabilities
- **CORS Enabled**: Ready for frontend integration

---

## 🛠️ API Endpoints

### New Multi-Agent API

#### POST `/api/v1/prompt` - Text Editing
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
  "success": true,
  "agent_used": "editor",
  "diff": "<span>Hello</span><del>,</del><span> how are you? Today is a beautiful day</span><del>,</del><span> isn't it?</span>"
}
```

#### POST `/api/v1/summarize` - AI Summarization
**Request:**
```json
{
  "text": "This is a very long document with multiple paragraphs and complex ideas that needs to be condensed into a shorter form...",
  "command": "summarize"
}
```
**Response:**
```json
{
  "result": "A concise summary of the main points from the original text.",
  "success": true,
  "agent_used": "summarizer",
  "diff": "..."
}
```

#### GET `/api/v1/agents` - List Available Agents
**Response:**
```json
{
  "agents": ["editor", "summarizer"]
}
```

### Legacy Compatibility API

#### POST `/prompt` - Legacy Text Editing
Legacy endpoint for backward compatibility.

#### POST `/summarize` - Legacy Summarization
Legacy endpoint that redirects to the new summarizer agent.

---

## ⚙️ Setup

### Prerequisites
- Python 3.11.6 or higher
- OpenAI API key (for AI features)

### Installation
1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd Chat-Notepad-Core.Ai
   ```

2. **Install dependencies:**
   ```sh
   python3 -m pip install -r requirements.txt
   # or using uv
   uv sync
   ```

3. **Environment setup:**
   Create a `.env` file or set environment variables:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_TEMPERATURE=0.7
   OPENAI_MAX_TOKENS=1000
   ```

4. **Run the server:**
   ```sh
   python3 -m uvicorn main:app --reload
   ```

5. **Test the endpoints:**
   
   **Text Editing:**
   ```sh
   curl -X POST "http://127.0.0.1:8000/api/v1/prompt" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, world!", "command": "uppercase"}'
   ```
   
   **Text Summarization:**
   ```sh
   curl -X POST "http://127.0.0.1:8000/api/v1/summarize" \
     -H "Content-Type: application/json" \
     -d '{"text": "Long text here...", "command": "summarize"}'
   ```

---

## 🧠 Multi-Agent System

### Adding New Agents

1. **Create Agent Class:**
   ```python
   # app/agents/your_agent.py
   from .base_agent import BaseAgent
   
   class YourAgent(BaseAgent):
       async def process(self, text: str, command: str) -> str:
           # Your agent logic here
           return processed_text
   ```

2. **Register in Agent Manager:**
   ```python
   # app/core/agent_manager.py
   self.agents = {
       "editor": TextEditorAgent("editor"),
       "summarizer": SummarizerAgent("summarizer"),
       "your_agent": YourAgent("your_agent"),  # Add here
   }
   ```

3. **Add Route (Optional):**
   ```python
   # app/routers/text_operations.py
   @router.post("/your-endpoint")
   async def your_endpoint(request: TextRequest, ...):
       result = await agent_manager.execute("your_agent", ...)
   ```

### Current Agents

- **TextEditorAgent**: Handles text transformations (uppercase, replace, etc.)
- **SummarizerAgent**: AI-powered text summarization with various styles

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── requests.py            # Pydantic request/response models
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Abstract base class
│   │   ├── text_editor_agent.py   # Text editing logic
│   │   └── summarizer_agent.py    # Summarization logic
│   ├── core/
│   │   ├── __init__.py
│   │   └── agent_manager.py       # Agent orchestration
│   └── routers/
│       ├── __init__.py
│       └── text_operations.py     # API endpoints
├── main.py                        # Legacy compatibility layer
├── agent.py                       # Legacy agent logic
├── diff_utils.py                  # Diff calculation utilities
├── llm_service.py                 # OpenAI integration
├── config.py                      # Configuration
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration
└── README.md                      # This file
```

---

## 🌟 Features in Detail

### Text Editing Agent
- **Rule-based transformations**: uppercase, lowercase, character removal
- **AI-powered edits**: Complex natural language commands
- **Pattern matching**: Advanced find-and-replace operations

### Summarization Agent
- **Multiple styles**: Brief, detailed, bullet points, executive summary
- **AI-powered**: Uses OpenAI GPT for intelligent summarization
- **Context-aware**: Maintains original tone and important information

---

## 🦾 Frontend Integration

The API is designed for seamless integration with modern frontends:

- **React + Monaco Editor**: Perfect for code/text editing interfaces
- **Diff Visualization**: HTML diff output for `react-diff-viewer`
- **CORS Enabled**: Ready for cross-origin requests
- **TypeScript Ready**: Well-defined request/response schemas

---

## 📬 Contact & Contribution

Feel free to open issues or PRs for improvements, new features, or bug fixes!

**Future Agent Ideas:**
- TranslatorAgent (multi-language support)
- SentimentAnalyzerAgent (emotional tone analysis)
- CodeFormatterAgent (code beautification)
- GrammarCheckerAgent (writing assistance)