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
- **Advanced Text Transformation**: Formalization, simplification, and tone shifting ✨ NEW
- **Text Summarization**: AI-powered summarization with different styles
- **User Authentication**: Supabase-powered authentication and user management ✨ NEW
- **Email Verification**: Automated email confirmation workflow ✨ NEW
- **User Preferences**: Personalized settings and preferences storage ✨ NEW
- **Note Storage**: Complete CRUD operations with search and tagging ✨ NEW
- **Export/Import**: Multi-format note export (MD, TXT, PDF) and import (TXT, MD, JSON) ✨ NEW
- **Visual Diff**: HTML diff output for frontend integration
- **RESTful API**: Clean REST endpoints with proper error handling
- **Comprehensive Testing**: Full test coverage with pytest
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
  "diff": "<span>Hello</span><del>,</del><span> how are you? Today is a beautiful day</span><del>,</del><span> isn't it?</span>",
  "agent_info": {
    "model": "rule-based",
    "processing_time_ms": 5,
    "confidence_score": 1.0,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### POST `/api/v1/transform` - Advanced Text Transformation ✨ NEW
**Request:**
```json
{
  "text": "hey there! hope you're doing well",
  "command": "Make this more formal"
}
```
**Response:**
```json
{
  "result": "Good morning. I hope this message finds you well.",
  "success": true,
  "agent_used": "transformer",
  "diff": "<span>Good morning. I hope this message finds you well.</span>",
  "agent_info": {
    "model": "text-transformation-agent",
    "processing_time_ms": 1250,
    "tokens_used": 450,
    "confidence_score": 0.95,
    "timestamp": "2024-01-15T10:30:00Z",
    "transformation_type": "formalization"
  }
}
```

**Supported Transformations:**
- **Formalization**: `formal`, `formalize`, `professional`, `business`, `official`
- **Simplification**: `simplify`, `simple`, `easier`, `beginner`, `layman`
- **Tone Shift**: `tone`, `casual`, `friendly`, `warm`, `conversational`

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
  "diff": "...",
  "agent_info": {
    "model": "gpt-4o",
    "processing_time_ms": 1800,
    "tokens_used": 320,
    "confidence_score": 0.92,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### POST `/api/v1/notes` - Note Storage ✨ NEW
**Request:**
```json
{
  "title": "My Important Note",
  "content": "This is the content of my note...",
  "is_favorite": false,
  "tags": ["work", "important"]
}
```
**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "My Important Note",
  "content": "This is the content of my note...",
  "is_favorite": false,
  "tags": ["work", "important"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "user_id": "user123"
}
```

#### GET `/api/v1/notes` - List User Notes ✨ NEW
**Query Parameters:**
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20, max: 100)
- `is_favorite` - Filter by favorite status
- `tags` - Filter by tags array

**Response:**
```json
{
  "notes": [...],
  "total": 25,
  "page": 1,
  "per_page": 20,
  "pages": 2
}
```

#### GET `/api/v1/notes/search` - Search Notes ✨ NEW
**Query Parameters:**
- `query` - Search term (required)
- `page` - Page number
- `per_page` - Items per page
- `is_favorite` - Filter by favorite status
- `tags` - Filter by tags

#### GET `/api/v1/notes/{note_id}` - Get Specific Note ✨ NEW
#### PUT `/api/v1/notes/{note_id}` - Update Note ✨ NEW
#### DELETE `/api/v1/notes/{note_id}` - Delete Note ✨ NEW
#### GET `/api/v1/notes/favorites` - Get Favorite Notes ✨ NEW
#### GET `/api/v1/notes/tags` - Get User Tags ✨ NEW

### Export/Import API ✨ NEW

#### GET `/api/v1/export/markdown/{note_id}` - Export Note as Markdown ✨ NEW
#### GET `/api/v1/export/txt/{note_id}` - Export Note as TXT ✨ NEW
#### GET `/api/v1/export/pdf/{note_id}` - Export Note as PDF ✨ NEW
#### POST `/api/v1/export/bulk` - Bulk Export Notes ✨ NEW
#### POST `/api/v1/import/file` - Import Notes from File ✨ NEW
#### GET `/api/v1/import/formats` - Get Supported Import Formats ✨ NEW
#### POST `/api/v1/import/validate` - Validate Import File ✨ NEW

#### GET `/api/v1/agents` - List Available Agents
**Response:**
```json
{
  "agents": ["editor", "summarizer", "transformer"]
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
- Supabase project (for authentication and user management)

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
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_TEMPERATURE=0.7
   OPENAI_MAX_TOKENS=1000
   
   # Supabase Configuration
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your_supabase_anon_key_here
   SUPABASE_SERVICE_KEY=your_supabase_service_key_here
   
   # JWT Configuration
   JWT_SECRET=your_jwt_secret_key_here
   JWT_EXPIRATION_HOURS=24
   ```

4. **Run the server:**
   ```sh
   python3 -m uvicorn app.main:app --reload
   ```

5. **Access the API documentation:**
   Open your browser and visit the interactive Swagger UI at:
   ```
   http://127.0.0.1:8000/docs
   ```

6. **Build and test the project:**
   
   **Install dependencies:**
   ```sh
   pip3 install -r requirements.txt
   ```
   
   **Run tests:**
   ```sh
   python3 -m pytest tests/ -v
   ```
   
   **Check code syntax:**
   ```sh
   python3 -m py_compile app/main.py
   python3 -m py_compile app/routers/auth.py
   python3 -m py_compile app/services/auth_service.py
   ```

7. **Test the endpoints:**
   
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
   
   **Text Transformation:**
   ```sh
   curl -X POST "http://127.0.0.1:8000/api/v1/transform" \
     -H "Content-Type: application/json" \
     -d '{"text": "hey there! hope you are doing well", "command": "make this more formal"}'
   ```
   
   **Note Management:**
   ```sh
   # Create a note
   curl -X POST "http://127.0.0.1:8000/api/v1/notes/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"title": "My Note", "content": "Note content", "tags": ["work"]}'
   
   # List notes
   curl -X GET "http://127.0.0.1:8000/api/v1/notes/?page=1&per_page=10" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   
   # Search notes
   curl -X GET "http://127.0.0.1:8000/api/v1/notes/search?query=work" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```
   
   **Authentication:**
   ```sh
   curl -X POST "http://127.0.0.1:8000/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'
   ```

---

## 🔐 Authentication & User Management

### Supabase Integration

The backend now includes comprehensive authentication and user management powered by **Supabase**:

#### Key Features:
- **User Registration & Sign-in**: Secure email/password authentication
- **Email Verification**: Automated email confirmation workflow
- **Password Reset**: Secure password reset with email tokens
- **User Profiles**: Full name, email, verification status management
- **User Preferences**: Theme, language, and application settings
- **Account Management**: Profile updates and account deletion

#### Authentication Endpoints:

**POST `/auth/signup`** - User Registration
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**POST `/auth/signin`** - User Sign-in
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**POST `/auth/confirm-email`** - Email Confirmation ✨ NEW
```json
{
  "token": "supabase_jwt_access_token"
}
```

**POST `/auth/reset-password`** - Password Reset Request
```json
{
  "email": "user@example.com"
}
```

**POST `/auth/update-password`** - Password Update
```json
{
  "token": "reset_token_from_email",
  "new_password": "new_secure_password"
}
```

**GET `/auth/me`** - Get Current User Profile
```json
{
  "id": "user_uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "email_verified": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**PUT `/auth/me`** - Update User Profile
```json
{
  "full_name": "John Updated Doe",
  "email": "new_email@example.com"
}
```

**GET `/auth/preferences`** - Get User Preferences
```json
{
  "theme": "dark",
  "language": "en",
  "editor_settings": {},
  "command_history_enabled": true,
  "auto_save_enabled": true
}
```

**PUT `/auth/preferences`** - Update User Preferences
```json
{
  "preferences": {
    "theme": "dark",
    "language": "en",
    "editor_settings": {"fontSize": 14},
    "command_history_enabled": true,
    "auto_save_enabled": true
  }
}
```

#### Security Features:
- **JWT Authentication**: Secure token-based authentication
- **Email Verification**: Required before sign-in
- **Password Reset**: Secure token-based password reset
- **Admin Operations**: Service key for admin-level operations
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Consistent error responses

#### Database Schema:
```sql
-- User preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    preferences JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Frontend Integration:
- **React Authentication**: Easy integration with React contexts
- **Protected Routes**: JWT-based route protection
- **User State Management**: Persistent user session handling
- **Error Boundaries**: Graceful authentication error handling

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
- **TransformerAgent**: Advanced text transformation with specialized prompts ✨ NEW
  - Formalization (casual → formal)
  - Simplification (complex → simple)
  - Tone shifting (formal → friendly)
- **NoteStorageAgent**: Personalized note storage with CRUD operations ✨ NEW
  - Create, read, update, delete notes
  - Full-text search functionality
  - Tag-based organization
  - Favorite notes system
  - Pagination and filtering

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
│   │   ├── requests.py            # Pydantic request/response models (+ Notes) ✨ NEW
│   │   └── auth.py                # Authentication models ✨ NEW
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Abstract base class
│   │   ├── text_editor_agent.py   # Text editing logic
│   │   ├── summarizer_agent.py    # Summarization logic
│   │   └── transformer_agent.py   # Advanced text transformation ✨ NEW
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent_manager.py       # Agent orchestration
│   │   └── langgraph_workflow.py  # LangGraph workflow orchestration
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── text_operations.py     # API endpoints
│   │   ├── auth.py                # Authentication endpoints ✨ NEW
│   │   ├── notes.py               # Note storage endpoints ✨ NEW
│   │   └── export_import.py       # Export/import endpoints ✨ NEW
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py         # OpenAI integration
│   │   ├── auth_service.py        # Supabase authentication service ✨ NEW
│   │   ├── note_service.py        # Note storage service ✨ NEW
│   │   ├── export_service.py      # Note export service (MD, TXT, PDF) ✨ NEW
│   │   └── import_service.py      # Note import service (TXT, MD, JSON) ✨ NEW
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth_middleware.py     # JWT authentication middleware ✨ NEW
│   ├── utils/
│   │   ├── __init__.py
│   │   └── diff_utils.py          # Diff calculation utilities
│   └── config/
│       ├── __init__.py
│       ├── config.py              # Configuration settings
│       └── supabase.py            # Supabase configuration ✨ NEW
├── database/
│   └── schema.sql                 # Database schema for Supabase ✨ NEW
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── unit/                      # Unit tests
│   │   ├── __init__.py
│   │   ├── test_langgraph_workflow.py
│   │   ├── test_transformer_agent.py         # TransformerAgent tests ✨ NEW
│   │   ├── test_transform_error_handling.py  # Error handling tests ✨ NEW
│   │   └── test_langgraph_transformer.py     # LangGraph integration tests ✨ NEW
│   └── integration/               # Integration tests
│       ├── __init__.py
│       ├── test_text_operations.py
│       └── test_transform_endpoint_simple.py # Transform endpoint tests ✨ NEW
├── main.py                        # Entry point with legacy endpoints
├── agent.py                       # Legacy agent logic (compatibility)
├── test_auth.py                   # Authentication testing script ✨ NEW
├── test_email_confirm.py          # Email confirmation testing script ✨ NEW
├── test_notes_api.py              # Note storage API testing script ✨ NEW
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
├── pyproject.toml                 # Project configuration
├── SUPABASE_SETUP.md              # Supabase setup instructions ✨ NEW
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

### Transformer Agent ✨ NEW
- **Formalization**: Convert casual text to professional language
- **Simplification**: Transform complex text into simple, accessible language
- **Tone Shifting**: Adjust text tone (formal ↔ casual, professional ↔ friendly)
- **Intelligent Routing**: Automatically detects transformation type from commands
- **Specialized Prompts**: Tailored LLM prompts for each transformation type
- **Error Resilience**: Comprehensive error handling and fallback mechanisms

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
- FactCheckerAgent (content verification)
- StyleGuideAgent (brand voice consistency)

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
- ✅ **NEW: `/transform` endpoint with TransformerAgent**
- ✅ **NEW: Advanced text transformation capabilities (formalization, simplification, tone shift)**
- ✅ **NEW: Intelligent command detection and specialized prompts**
- ✅ **NEW: Enhanced agent_info response with transformation_type metadata**
- ✅ **NEW: Comprehensive test coverage for transformation functionality (60+ tests)** 

---

### 🟣 Phase 3: Collaboration & Scalability – **🚧 In Progress**
- ✅ **Supabase integration for user authentication**
- ✅ **User registration and sign-in endpoints** 
- ✅ **Email verification workflow with confirmation endpoint**
- ✅ **Password reset functionality with secure token handling**
- ✅ **User profile management (view, update, delete)**
- ✅ **User preferences storage and management**
- ✅ **JWT-based authentication middleware**
- ✅ **Comprehensive auth error handling and validation**
- ✅ User settings and preferences storage
- ✅ **Personalized note storage** - Complete CRUD API with authentication
- ✅ **Export/Import System** - Full note export/import with multiple formats
- ⬜️ Version history and undo support
- ⬜️ Real-time collaboration foundation
- ⬜️ Multi-language command handling support
- ⬜️ Team/collaborator management features
- ⬜️ API rate limiting and quota management
- ⬜️ Command history storage and retrieval API
- ⬜️ Context-aware command suggestions based on user history
- ✅ **Export API endpoints (Markdown, TXT, PDF formats)**
- ✅ **File import API endpoints (Markdown, TXT, JSON file parsing)**
- ⬜️ WebSocket support for real-time collaboration
- ⬜️ Cloud storage integration APIs (Dropbox, Google Drive)
- ⬜️ Plugin system backend architecture for custom commands
- ⬜️ Advanced AI model integration options

---

### 💡 Future Enhancements
- ⬜️ Agent analytics and usage logging
- ⬜️ Custom agent loader (dynamic import system)
- ⬜️ Support for additional agent types (Translator, Sentiment, Formatter)
- ⬜️ More integration examples for different frontends

---

## 🧪 Testing & Quality Assurance

The project includes comprehensive test coverage to ensure reliability and maintainability:

### Test Structure
```
tests/
├── unit/                                    # Unit tests (53 tests)
│   ├── test_transformer_agent.py          # TransformerAgent core functionality
│   ├── test_transform_error_handling.py   # Error handling and edge cases
│   └── test_langgraph_transformer.py      # LangGraph workflow integration
└── integration/                            # Integration tests (7 tests)
    └── test_transform_endpoint_simple.py  # API endpoint testing
```

### Test Coverage
- **TransformerAgent**: Command detection, prompt generation, processing logic
- **Error Handling**: API failures, network issues, malformed responses
- **LangGraph Integration**: Workflow routing, agent coordination
- **Endpoint Testing**: Input validation, response structure, error scenarios

### Running Tests
```bash
# Run all transformer-related tests
python3 -m pytest tests/unit/test_transformer_agent.py tests/unit/test_transform_error_handling.py tests/unit/test_langgraph_transformer.py -v

# Run integration tests
python3 -m pytest tests/integration/test_transform_endpoint_simple.py -v

# Run specific test categories
python3 -m pytest tests/unit/test_transformer_agent.py::TestTransformerAgent::test_detect_transformation_type_formalization -v
```

### Test Features
- **Mocking**: Comprehensive mocking of OpenAI API calls
- **Edge Cases**: Handling of None inputs, special characters, boundary conditions
- **Error Scenarios**: Network failures, API errors, malformed responses
- **Performance**: Processing time and token usage validation

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