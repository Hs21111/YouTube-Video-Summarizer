import os
import getpass
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

# Load environment variables from .env file
load_dotenv()

# Set model
MODEL_NAME = "gemini-2.5-pro" # Verified available via API

console = Console()

def get_transcript(video_url):
    """
    Retrieves the transcript of a YouTube video given its URL.
    Using `YouTubeTranscriptApi` instance method `fetch`.
    """
    try:
        if "v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be" in video_url:
             video_id = video_url.split("/")[-1]
        else:
             video_id = video_url
    except Exception:
        console.print("[bold red]Error:[/bold red] Could not extract video ID.")
        return None

    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        transcript_text = " ".join([i.text for i in transcript_list])
        return transcript_text
    except Exception as e:
        console.print(f"[bold red]Error retrieving transcript:[/bold red] {e}")
        return None

def main():
    console.print(Panel.fit("[bold blue]YouTube Video Summarizer & Chat[/bold blue]", border_style="blue"))

    # API Key Handling
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        console.print("[yellow]GOOGLE_API_KEY not found in environment.[/yellow]")
        try:
            api_key = getpass.getpass("Enter your GOOGLE_API_KEY: ")
            os.environ["GOOGLE_API_KEY"] = api_key
        except Exception as e:
            console.print(f"[bold red]Error getting API key:[/bold red] {e}")
            return

    if not api_key:
        console.print("[bold red]Error:[/bold red] No API key provided. Exiting.")
        return

    # User Input for URL
    video_url = Prompt.ask("[bold green]Enter YouTube Video URL[/bold green]")
    
    with console.status("[bold green]Fetching transcript...[/bold green]", spinner="dots"):
        transcript = get_transcript(video_url)

    if not transcript:
        return

    console.print("[bold green]Transcript fetched successfully![/bold green]")

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.7)

    # Chat Loop with Memory
    # We maintain a simple list of messages
    messages = [
        SystemMessage(content=f"""
You are a helpful assistant.
Your goal is to answer questions based on the video content provided below.
CRITICAL INSTRUCTION: Do NOT mention "the transcript", "the text", or "according to the video" in your responses. 
Act as if you just watched the video and know the information naturally.
After answering the user's question, you MUST provide 3 short "Next Question" suggestions relevant to the context.
Format the suggestions clearly at the end of your response like this:

**Suggested Questions:**
1. ...
2. ...
3. ...

Context Data:
{transcript}
""")
    ]

    # Initial Summary Request (simulated as the first user "trigger")
    initial_trigger = "Please provide a short summary paragraph of the video content."
    messages.append(HumanMessage(content=initial_trigger))

    console.print(Panel("[bold yellow]Generating Summary...[/bold yellow]", border_style="yellow"))
    
    while True:
        try:
            with console.status("[bold blue]Thinking...[/bold blue]", spinner="dots"):
                response = llm.invoke(messages)
            
            # Display Response
            console.print(Markdown(response.content))
            console.print("-" * 50)
            
            # Add response to memory
            messages.append(AIMessage(content=response.content))

            # Next User Input
            user_input = Prompt.ask("[bold cyan]You (or type 'exit')[/bold cyan]")
            
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[bold green]Goodbye![/bold green]")
                break
            
            messages.append(HumanMessage(content=user_input))

        except Exception as e:
            console.print(f"[bold red]Error encountered:[/bold red] {e}")
            break

if __name__ == "__main__":
    main()
