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

2.  **Run the summarizer**:
    ```bash
    uv run main.py <youtube_url>
    ```

    Example:
    ```bash
    uv run main.py https://www.youtube.com/watch?v=jNQXAC9IVRw
    ```

    *If you haven't set the API key, the script will prompt you for it securely.*

## Requirements
- Python 3.12+
- `uv` package manager
- A Google Cloud API key with access to Gemini API.
