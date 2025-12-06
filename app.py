import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Import our custom modules
import database
from main import get_transcript, get_model

# Load env vars
load_dotenv()

st.set_page_config(page_title="YouTube Summarizer & Chat", layout="wide")

# Initialize DB
database.init_db()

# --- Sidebar: History ---
st.sidebar.title("📚 Library")
if st.sidebar.button("➕ New Video Check"):
    st.session_state.current_video_id = None
    st.rerun()

st.sidebar.write("---")
all_videos = database.get_all_videos()
for v_id, y_id, v_title in all_videos:
    label = v_title if v_title else f"Video {y_id}"
    if st.sidebar.button(label, key=f"hist_{v_id}", use_container_width=True):
        st.session_state.current_video_id = v_id
        st.rerun()

# --- Main Logic ---

if "current_video_id" not in st.session_state:
    st.session_state.current_video_id = None

def get_video_title(url):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup.title.string.replace(" - YouTube", "")
    except:
        return "Unknown Video"

# 1. Input Section
if st.session_state.current_video_id is None:
    st.markdown("# 📺 YouTube Summarizer & Chat")
    st.markdown("Paste a URL to get started.")
    
    url = st.text_input("Enter YouTube Video URL:")
    
    if url:
        # Extract ID
        vid_id = None
        if "v=" in url:
            vid_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be" in url:
            vid_id = url.split("/")[-1]
        else:
            vid_id = url # fallback
            
        with st.spinner("Checking library..."):
            # Check if exists in DB (by youtube_id)
            # We iterate logic: get_video returns by youtube_id
            existing_vid = database.get_video(vid_id)
        
        if existing_vid:
            st.session_state.current_video_id = existing_vid[0]
            st.rerun()
        else:
            with st.spinner("Fetching transcript & Title..."):
                transcript = get_transcript(url)
                if transcript:
                    title = get_video_title(url)
                    new_id = database.save_video(vid_id, title, transcript)
                    st.session_state.current_video_id = new_id
                    st.rerun()
                else:
                    st.error("Could not fetch transcript. Check the URL.")

# 2. Chat Section
else:
    # Load Video Data
    v_data = database.get_video_by_id(st.session_state.current_video_id)
    if not v_data:
        st.error("Video not found.")
        st.session_state.current_video_id = None
        st.rerun()
        
    db_id, y_id, title, transcript = v_data
    
    st.title(f"{title}")
    
    # Check if we have chat history. If empty, generate summary message first.
    history = database.get_chat_history(db_id)
    
    # Initialize LLM
    llm = get_model()
    if not llm:
        st.error("API Key not configured.")
        st.stop()

    # System Prompt
    system_instruction = f"""
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
"""

    # If history is empty, auto-generate summary
    if not history:
        with st.spinner("Generatng initial summary..."):
            messages = [
                SystemMessage(content=system_instruction),
                HumanMessage(content="Please provide a short summary paragraph of the video content.")
            ]
            response = llm.invoke(messages)
            
            # Save to DB
            database.add_message(db_id, "user", "Please provide a short summary paragraph of the video content.")
            database.add_message(db_id, "ai", response.content)
            
            st.rerun()

    # Display History
    for role, content in history:
        # Convert role for Streamlit icons
        if role == "user":
            st.chat_message("user").markdown(content)
        else:
            st.chat_message("assistant").markdown(content)

    # Chat Input
    if prompt := st.chat_input("Ask a question about the video..."):
        # Display user message
        st.chat_message("user").markdown(prompt)
        
        # Save user message
        database.add_message(db_id, "user", prompt)
        
        # Build Context for LLM
        # We rebuild the message list from history + system prompt
        messages = [SystemMessage(content=system_instruction)]
        # Add history (limit to last 10 pairs if context is huge, but start simple)
        # Re-fetching history including the one we just added
        current_history = database.get_chat_history(db_id)
        for role, content in current_history:
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))
        
        # Generate Answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = llm.invoke(messages)
                st.markdown(response.content)
        
        # Save AI message
        database.add_message(db_id, "ai", response.content)
