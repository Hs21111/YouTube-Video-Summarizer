import streamlit as st
import os
import requests
import re
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

# --- Helpers ---
def get_video_title(url):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.title.string.replace(" - YouTube", "")
        return title
    except:
        return "Unknown Video"

def extract_suggestions(text):
    """
    Extracts suggested questions from the AI response text.
    Looks for the **Suggested Questions:** pattern.
    """
    suggestions = []
    if "**Suggested Questions:**" in text:
        try:
            # Split by the header
            part = text.split("**Suggested Questions:**")[1].strip()
            lines = part.split('\n')
            for line in lines:
                # Matches "1. Question..." or "1 Question..."
                clean_line = line.strip()
                if clean_line and (clean_line[0].isdigit() and (clean_line[1] == '.' or clean_line[1] == ' ')):
                    # Remove the number and leading dot/space
                    q = re.sub(r'^\d+[\.\s]+\s*', '', clean_line)
                    suggestions.append(q)
                if len(suggestions) >= 3:
                    break
        except Exception:
            pass
    return suggestions

def handle_response(user_text, db_id, system_instruction, llm):
    """
    Handles generating the AI response, displaying it, and saving to DB.
    """
    # Display user message immediately (visual trick, though we rerun)
    # st.chat_message("user").markdown(user_text) # Optional, sidebar/rerun handles state
    
    # Save user message
    database.add_message(db_id, "user", user_text)
    
    # Build Context
    messages = [SystemMessage(content=system_instruction)]
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
    st.rerun()

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

# 1. Input Section
if st.session_state.current_video_id is None:
    st.markdown("# 📺 YouTube Summarizer & Chat")
    st.markdown("Paste a URL to get started.")
    
    url = st.text_input("Enter YouTube Video URL:")
    
    if url:
        vid_id = None
        if "v=" in url:
            vid_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be" in url:
            vid_id = url.split("/")[-1]
        else:
            vid_id = url
            
        with st.spinner("Checking library..."):
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
    v_data = database.get_video_by_id(st.session_state.current_video_id)
    if not v_data:
        st.error("Video not found.")
        st.session_state.current_video_id = None
        st.rerun()
        
    db_id, y_id, title, transcript = v_data
    
    st.title(f"{title}")
    
    history = database.get_chat_history(db_id)
    
    llm = get_model()
    if not llm:
        st.error("API Key not configured.")
        st.stop()

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
        with st.spinner("Generating initial summary..."):
            # We don't use handle_response regarding reruns here to avoid infinite loops easily, 
            # but actually it's fine as long as we check history first.
            handle_response("Please provide a short summary paragraph of the video content.", db_id, system_instruction, llm)

    # Display History
    for role, content in history:
        if role == "user":
            st.chat_message("user").markdown(content)
        else:
            st.chat_message("assistant").markdown(content)

    # Extract Suggestions from Last AI Message
    last_suggestions = []
    if history and history[-1][0] == 'ai':
        last_suggestions = extract_suggestions(history[-1][1])

    # Display Suggestion Buttons (if any)
    if last_suggestions:
        st.write("Something specific?")
        cols = st.columns(len(last_suggestions))
        for idx, suggestion in enumerate(last_suggestions):
            if cols[idx].button(suggestion, key=f"sugg_{idx}"):
                handle_response(suggestion, db_id, system_instruction, llm)

    # Chat Input
    if prompt := st.chat_input("Ask a question about the video..."):
        handle_response(prompt, db_id, system_instruction, llm)
