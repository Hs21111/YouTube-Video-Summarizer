# YouTube Video Summarizer

A Python tool that fetches YouTube video transcripts and uses Google's Gemini 2.5 Pro (via LangChain) to generate a short summary paragraph.

## Features
- **Smart Summarization**: Uses `gemini-2.5-pro` for high-quality summaries.
- **Transcript Fetching**: robustly handles video URLs and IDs.
- **Secure Authentication**:
    - Supports `.env` file for `GOOGLE_API_KEY`.
    - Interactively prompts for the key if missing (no hardcoding!).
- **Modern Tooling**: Managed by `uv` for fast dependency resolution.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd YouTube-Video-Summarizer
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    # or
    uv pip install -r pyproject.toml
    ```

## Usage
1.  **Set your API Key** (Optional but recommended):
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_actual_api_key_here
    ```

2.  **Run the interactive tool**:
    ```bash
    uv run main.py
    ```

3.  **Interact**:
    - Paste the YouTube URL when prompted.
    - View the summary.
    - Ask follow-up questions in the chat interface.
    - See "Suggested Questions" to explore the video further.

    *Type `exit` or `quit` to end the session.*

### Web Interface (Streamlit)
For a visual interface with persistent history:
```bash
uv run streamlit run app.py
```
- **Library Sidebar**: Access past video chats.
- **Rich Chat**: Chat bubble interface.
- **Persistence**: automatically saves chat history to a local SQLite database.

## Features
- **Smart Summarization**: Uses `gemini-2.5-pro` for high-quality summaries.
- **Web GUI**: Full-featured web chat with history sidebar.
- **Interactive TUI**: Beautiful terminal interface.
- **Persistent Memory**: Remembers your chats per video in `chat_history.db`.
- **Auto-Suggestions**: Get 3 relevant follow-up questions after every answer.
- **Transcript Fetching**: robustly handles video URLs and IDs.
- **Secure Authentication**: Supports `.env` and secure prompts.
