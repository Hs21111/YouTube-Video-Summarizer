import os
import argparse
import getpass
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables from .env file
load_dotenv()

# Set model to Gemini 3.0 Pro Preview as requested
MODEL_NAME = "gemini-3-pro-preview"

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
             # Assume it's an ID if not a url, or standard ID length
             video_id = video_url
    except Exception:
        print("Error: Could not extract video ID.")
        return None

    try:
        # instantiate the API class
        api = YouTubeTranscriptApi()
        # use fetch which returns the transcript list directly
        transcript_list = api.fetch(video_id)
        transcript_text = " ".join([i.text for i in transcript_list])
        return transcript_text
    except Exception as e:
        print(f"Error retrieving transcript: {e}")
        return None

def summarize_video(transcript_text):
    """
    Summarizes the transcript using Gemini.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not found in environment.")
        try:
            api_key = getpass.getpass("Enter your GOOGLE_API_KEY: ")
            os.environ["GOOGLE_API_KEY"] = api_key # key is set for this session
        except Exception as e:
            print(f"Error getting API key: {e}")
            return None

    if not api_key:
        print("Error: No API key provided.")
        return None

    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.7)
    
    template = """
    You are a helpful assistant.
    Read the following YouTube video transcript and generate a concise 3-bullet point summary.
    
    Transcript:
    {transcript}
    
    Summary:
    """
    
    prompt = PromptTemplate(template=template, input_variables=["transcript"])
    chain = prompt | llm
    
    try:
        response = chain.invoke({"transcript": transcript_text})
        return response.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="YouTube Video Summarizer")
    parser.add_argument("url", help="URL of the YouTube video")
    args = parser.parse_args()

    print(f"Fetching transcript for: {args.url}")
    transcript = get_transcript(args.url)
    
    if transcript:
        print("Transcript fetched. Generating summary...")
        summary = summarize_video(transcript)
        if summary:
            print("\nSummary:")
            print(summary)
        else:
            print("Failed to generate summary.")
    else:
        print("Failed to fetch transcript.")

if __name__ == "__main__":
    main()
