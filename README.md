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

### LangGraph & LangChain Integration

The project leverages **LangGraph** for advanced workflow orchestration and **LangChain** for enhanced AI capabilities:

#### LangGraph Workflow Features:
- **State Management**: Robust state tracking through `WorkflowState` with error handling
- **Conditional Routing**: Smart agent selection based on command analysis
- **Error Recovery**: Built-in error handling and fallback mechanisms
- **Async Processing**: Full async support for scalable operations

#### Workflow Architecture:
```python
# app/core/langgraph_workflow.py
class LangGraphWorkflow:
    def __init__(self):
        self.workflow = self._create_workflow()
    
    async def execute(self, text: str, command: str) -> Dict[str, Any]:
        # Orchestrates agent execution through LangGraph
```

#### Key Benefits:
- **Scalable**: Easy to add new agents and workflow steps
- **Reliable**: Comprehensive error handling and state management
- **Extensible**: Built for complex multi-agent coordination
- **Testable**: Full test coverage for workflow logic

#### Usage Example:
```python
workflow = LangGraphWorkflow()
result = await workflow.execute("Hello world", "uppercase")
# Returns: {"result": "HELLO WORLD", "success": True, "agent_used": "editor"}
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry point (new API)
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
│   │   ├── agent_manager.py       # Agent orchestration
│   │   └── langgraph_workflow.py  # LangGraph workflow orchestration
│   ├── routers/
│   │   ├── __init__.py
│   │   └── text_operations.py     # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── llm_service.py         # OpenAI integration
│   ├── utils/
│   │   ├── __init__.py
│   │   └── diff_utils.py          # Diff calculation utilities
│   └── config/
│       ├── __init__.py
│       └── config.py              # Configuration settings
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── unit/                      # Unit tests
│   │   ├── __init__.py
│   │   └── test_langgraph_workflow.py
│   └── integration/               # Integration tests
│       ├── __init__.py
│       └── test_text_operations.py
├── main.py                        # Entry point with legacy endpoints
├── agent.py                       # Legacy agent logic (compatibility)
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
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

## 🔮 Roadmap

### 🟢 Phase 1: Core Infrastructure – ✅ Completed
- ✅ FastAPI setup with async endpoints
- ✅ `/prompt` endpoint with rule-based command processing
- ✅ `TextEditorAgent` for transformations (remove, replace, capitalize)
- ✅ HTML diff output using `diff-match-patch`
- ✅ CORS support for frontend integration

---

### 🟡 Phase 2: LLM & Smart Agent Expansion – ✅ Completed
- ✅ OpenAI GPT integration for natural language commands
- ✅ `/summarize` endpoint with `SummarizerAgent`
- ✅ Expand agent capabilities to handle diverse natural commands
- ✅ Improve error handling and validation across agents 
- ✅ Provide `agent_used` feedback in API responses
- ✅ Advanced AI features: tone shift, simplification, rephrasing
- ✅ Feedback display for agent response (e.g. "Processed by GPT")
- ✅ LangGraph integration for advanced workflow orchestration and multi-agent coordination
- ✅ Unit and integration test coverage for LangGraph workflow and API endpoints
- ✅ Comprehensive test suite with pytest for reliability and maintainability 

---

### 🟣 Phase 3: Collaboration & Scalability – ⬜️ Not Started
- ⬜️ Basic user authentication and personalized note storage
- ⬜️ Version history and undo support
- ⬜️ Real-time collaboration foundation
- ⬜️ Multi-language command handling support
- ⬜️ Team/collaborator management features
- ⬜️ API rate limiting and quota management
- ⬜️ Command history storage and retrieval API
- ⬜️ Context-aware command suggestions based on user history
- ⬜️ Export API endpoints (Markdown, TXT, PDF formats)
- ⬜️ File import API endpoints (Markdown, TXT file parsing)
- ⬜️ WebSocket support for real-time collaboration
- ⬜️ Cloud storage integration APIs (Dropbox, Google Drive)
- ⬜️ Plugin system backend architecture for custom commands
- ⬜️ User settings and preferences storage
- ⬜️ Advanced AI model integration options

---

### 💡 Future Enhancements
- ⬜️ Agent analytics and usage logging
- ⬜️ Custom agent loader (dynamic import system)
- ⬜️ Support for additional agent types (Translator, Sentiment, Formatter)
- ⬜️ More integration examples for different frontends

## Troubleshooting

<details>
<summary>Import Error: "langgraph.graph" could not be resolved</summary>

If you encounter import errors in your IDE while the package works in terminal:

1. **Configure Python Interpreter:**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter" and select it
   - Choose `/usr/bin/python3`

2. **Create workspace settings** (`.vscode/settings.json`):
   ```json
   {
       "python.defaultInterpreterPath": "/usr/bin/python3"
   }
   ```

3. **Restart your IDE** completely

4. **Alternative: Use virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install langgraph
   ```

5. **For Cursor users:** Try "Developer: Reload Window" from command palette

</details>