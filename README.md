# YouTube Video Summarizer

A Python tool that fetches YouTube video transcripts and uses Google's Gemini 3 Pro Preview (via LangChain) to generate concise bullet-point summaries.

## Features
- **Smart Summarization**: Uses `gemini-3-pro-preview` for high-quality summaries.
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

## Features
- **Smart Summarization**: Uses `gemini-1.5-pro` (or configured model) for high-quality summaries.
- **Interactive Chat**: Ask questions about the video content with context retention.
- **Auto-Suggestions**: Get 3 relevant follow-up questions after every answer.
- **Rich TUI**: Beautiful terminal interface with markdown rendering.
- **Transcript Fetching**: robustly handles video URLs and IDs.
- **Secure Authentication**: Supports `.env` and secure prompts.
