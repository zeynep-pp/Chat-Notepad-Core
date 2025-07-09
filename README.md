# chatnotepad FastMCP Server

A FastMCP server implementation for educational purposes.

## Prerequisites

- Python 3.11.6 or higher
   uv python install 3.11.6
   uv python pin
   uv add fastmcp
- uv package manager

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync
   ```

## Running the Server

```bash
uv run main.py
```

## Testing

Test the server with the included client:

```bash
uv run client_test.py
fastmcp run client_test.py:mcp
```

## Project Structure

- `main.py` - FastMCP server with a greet tool
- `client_test.py` - Test client for the server
- `pyproject.toml` - Project dependencies and configuration